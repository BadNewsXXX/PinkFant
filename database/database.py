import asyncio
import os
from datetime import datetime, timedelta, timezone

from bot_content import DEFAULT_LANGUAGE, LIFETIME_END, PRODUCT_CHANNELS, PRODUCTS
from dotenv import load_dotenv
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

CHANNEL_ID = PRODUCT_CHANNELS["mandy_rose"]
bot_instance = None


def set_bot(bot):
    global bot_instance
    bot_instance = bot


async def is_user_in_channel(user_id: int, channel_id: int | None) -> bool:
    if bot_instance is None or channel_id is None:
        return False

    try:
        member = await bot_instance.get_chat_member(channel_id, user_id)
    except Exception:
        return False

    return member.status in {"member", "administrator", "creator", "restricted"}


class UserSubscription(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    product_code = Column(String(50), nullable=False, server_default="mandy_rose")
    channel_id = Column(BigInteger, nullable=True)
    is_lifetime = Column(Boolean, nullable=False, server_default="false")
    invite_link = Column(String(1024), nullable=True)
    subscription_start = Column(DateTime(timezone=True), nullable=False)
    subscription_end = Column(DateTime(timezone=True), nullable=False)


class PaymentInfo(Base):
    __tablename__ = "pay_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    product_code = Column(String(50), nullable=False, server_default="mandy_rose")
    plan_code = Column(String(50), nullable=False, server_default="monthly")
    duration_days = Column(Integer, nullable=True)
    is_lifetime = Column(Boolean, nullable=False, server_default="false")
    channel_id = Column(BigInteger, nullable=True)
    crypto_amount = Column(Float, nullable=False)
    crypto_rate = Column(Float, nullable=False)
    payment_window_end = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    transaction_hash = Column(String(255), unique=True)
    ccy = Column(String)


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    txId = Column(String(255), unique=True, index=True)
    amount = Column(Float)
    state = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    user_id = Column(BigInteger, ForeignKey("user_track.user_id"), nullable=True)
    ccy = Column(String)

    user = relationship("UserTrack", back_populates="deposits")


class UserTrack(Base):
    __tablename__ = "user_track"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    language = Column(String(2), nullable=False, server_default=DEFAULT_LANGUAGE)

    deposits = relationship("Deposit", back_populates="user")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("ALTER TABLE user_track ADD COLUMN IF NOT EXISTS language VARCHAR(2) DEFAULT 'en'"))
        await conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.table_constraints
                        WHERE table_name = 'users'
                          AND constraint_name = 'users_user_id_key'
                    ) THEN
                        ALTER TABLE users DROP CONSTRAINT users_user_id_key;
                    END IF;
                END $$;
                """
            )
        )
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS product_code VARCHAR(50) DEFAULT 'mandy_rose'"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_id BIGINT"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_lifetime BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS invite_link VARCHAR(1024)"))
        await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_user_product ON users (user_id, product_code)"))
        await conn.execute(text("ALTER TABLE pay_info ADD COLUMN IF NOT EXISTS product_code VARCHAR(50) DEFAULT 'mandy_rose'"))
        await conn.execute(text("ALTER TABLE pay_info ADD COLUMN IF NOT EXISTS plan_code VARCHAR(50) DEFAULT 'monthly'"))
        await conn.execute(text("ALTER TABLE pay_info ADD COLUMN IF NOT EXISTS duration_days INTEGER"))
        await conn.execute(text("ALTER TABLE pay_info ADD COLUMN IF NOT EXISTS is_lifetime BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE pay_info ADD COLUMN IF NOT EXISTS channel_id BIGINT"))


async def scheduler():
    while True:
        await remove_expired_users()
        await asyncio.sleep(21600)


async def revoke_invite_link(channel_id: int | None, invite_link: str | None):
    if bot_instance is None or channel_id is None or not invite_link:
        return

    try:
        await bot_instance.revoke_chat_invite_link(channel_id, invite_link)
    except Exception as e:
        print(f"Error revoking invite link for channel {channel_id}: {e}")


async def create_single_use_invite_link(channel_id: int | None, previous_invite_link: str | None = None) -> str | None:
    if bot_instance is None or channel_id is None:
        return None

    if previous_invite_link:
        await revoke_invite_link(channel_id, previous_invite_link)

    result = await bot_instance.create_chat_invite_link(channel_id, member_limit=1)
    return result.invite_link


async def remove_expired_users():
    async with async_session() as session:
        current_time = datetime.now(timezone.utc)
        result = await session.execute(
            select(UserSubscription).where(
                UserSubscription.is_lifetime.is_(False),
                UserSubscription.subscription_end < current_time,
            )
        )
        expired_users = result.scalars().all()

        for user in expired_users:
            try:
                await revoke_invite_link(user.channel_id, user.invite_link)
                if user.channel_id and bot_instance is not None:
                    await bot_instance.ban_chat_member(user.channel_id, user.user_id)
                    await bot_instance.unban_chat_member(user.channel_id, user.user_id)
                await session.delete(user)
                await session.commit()
            except Exception as e:
                print(f"Error removing user {user.user_id}: {e}")


async def add_user(user_id: int):
    async with async_session() as session:
        existing_user = await session.scalar(select(UserTrack).where(UserTrack.user_id == user_id))
        if existing_user is None:
            session.add(UserTrack(user_id=user_id, language=DEFAULT_LANGUAGE))
            await session.commit()


async def set_user_language(user_id: int, language: str):
    async with async_session() as session:
        user = await session.scalar(select(UserTrack).where(UserTrack.user_id == user_id))
        if user is None:
            user = UserTrack(user_id=user_id, language=language)
            session.add(user)
        else:
            user.language = language
        await session.commit()


async def get_user_language(user_id: int) -> str:
    async with async_session() as session:
        language = await session.scalar(select(UserTrack.language).where(UserTrack.user_id == user_id))
        return language or DEFAULT_LANGUAGE


async def calculate_crypto_amount(fiat_amount: float, crypto_rate: float) -> float:
    return fiat_amount / crypto_rate


async def create_payment_intent(
    user_id: int,
    product_code: str,
    plan_code: str,
    ccy: str,
    crypto_amount: float,
    crypto_rate: float,
    window_minutes: int = 45,
):
    plan = PRODUCTS[product_code]["plans"][plan_code]
    payment_window_end = datetime.now(timezone.utc) + timedelta(minutes=window_minutes)

    async with async_session() as session:
        payment_info = PaymentInfo(
            user_id=user_id,
            product_code=product_code,
            plan_code=plan_code,
            duration_days=plan["duration_days"],
            is_lifetime=plan["is_lifetime"],
            channel_id=PRODUCT_CHANNELS.get(product_code),
            crypto_amount=crypto_amount,
            crypto_rate=crypto_rate,
            payment_window_end=payment_window_end,
            transaction_hash=None,
            ccy=ccy,
            status="pending",
        )
        session.add(payment_info)
        await session.commit()

    return crypto_amount, payment_window_end


async def create_manual_usdt_payment(user_id: int, product_code: str, plan_code: str):
    plan = PRODUCTS[product_code]["plans"][plan_code]
    return await create_payment_intent(
        user_id=user_id,
        product_code=product_code,
        plan_code=plan_code,
        ccy="USDT",
        crypto_amount=float(plan["price_usd"]),
        crypto_rate=1.0,
        window_minutes=1440,
    )


async def initiate_paymentTON(user_id: int, product_code: str, plan_code: str, crypto_rate: float):
    plan = PRODUCTS[product_code]["plans"][plan_code]
    crypto_amount = await calculate_crypto_amount(plan["price_usd"], crypto_rate)
    return await create_payment_intent(user_id, product_code, plan_code, "TON", crypto_amount, crypto_rate)


async def initiate_paymentLTC(user_id: int, product_code: str, plan_code: str, crypto_rate: float):
    plan = PRODUCTS[product_code]["plans"][plan_code]
    crypto_amount = await calculate_crypto_amount(plan["price_usd"], crypto_rate)
    return await create_payment_intent(user_id, product_code, plan_code, "LTC", crypto_amount, crypto_rate)


async def get_latest_payment(user_id: int):
    async with async_session() as session:
        return await session.scalar(
            select(PaymentInfo).where(PaymentInfo.user_id == user_id).order_by(PaymentInfo.id.desc())
        )


async def get_transaction_info(user_id: int):
    async with async_session() as session:
        deposit_info = await session.scalar(select(Deposit).where(Deposit.user_id == user_id).order_by(Deposit.id.desc()))
        if deposit_info:
            return {
                "transaction_hash": deposit_info.txId,
                "amount_received": deposit_info.amount,
            }
        return None


async def update_payment_info_with_hash(user_id: int, transaction_hash: str):
    async with async_session() as session:
        payment_info = await session.scalar(
            select(PaymentInfo).where(PaymentInfo.user_id == user_id).order_by(PaymentInfo.id.desc())
        )
        if payment_info:
            payment_info.transaction_hash = transaction_hash
            await session.commit()


async def find_matching_deposit(transaction_hash: str):
    async with async_session() as session:
        deposit = await session.scalar(select(Deposit).where(Deposit.txId == transaction_hash))
        if deposit:
            if deposit.state == 2:
                return {"status": "completed", "amount": deposit.amount, "ccy": deposit.ccy}
            return {"status": "pending", "amount": deposit.amount, "ccy": deposit.ccy}
        return None


async def get_expected_currency(transaction_hash: str):
    async with async_session() as session:
        return await session.scalar(select(PaymentInfo.ccy).where(PaymentInfo.transaction_hash == transaction_hash))


async def get_user_id_by_transaction_hash(transaction_hash: str):
    async with async_session() as session:
        return await session.scalar(select(Deposit.user_id).where(Deposit.txId == transaction_hash))


async def handle_deposit(transaction_hash: str, amount: float, state: int, timestamp: datetime, currency: str):
    async with async_session() as session:
        deposit = await session.scalar(select(Deposit).where(Deposit.txId == transaction_hash))
        if deposit:
            deposit.amount = amount
            deposit.state = state
            deposit.timestamp = timestamp
            deposit.ccy = currency
        else:
            session.add(
                Deposit(
                    txId=transaction_hash,
                    amount=amount,
                    state=state,
                    timestamp=timestamp,
                    ccy=currency,
                )
            )
        await session.commit()


async def link_deposit_with_user(transaction_hash: str, user_id: int):
    async with async_session() as session:
        deposit = await session.scalar(select(Deposit).where(Deposit.txId == str(transaction_hash)))
        if not deposit:
            return False
        if deposit.user_id is not None and deposit.user_id != user_id:
            return False
        deposit.user_id = user_id
        await session.commit()
        return True


async def cancel_payment(user_id: int):
    async with async_session() as session:
        payment_info = await session.scalar(
            select(PaymentInfo).where(PaymentInfo.user_id == user_id).order_by(PaymentInfo.id.desc())
        )
        if payment_info:
            await session.delete(payment_info)
            await session.commit()
            return True
        return False


async def activate_subscription(user_id: int, product_code: str, plan_code: str):
    plan = PRODUCTS[product_code]["plans"][plan_code]
    channel_id = PRODUCT_CHANNELS.get(product_code)
    now = datetime.now(timezone.utc)
    already_in_channel = await is_user_in_channel(user_id, channel_id)

    async with async_session() as session:
        subscription = await session.scalar(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.product_code == product_code,
            )
            .order_by(UserSubscription.id.desc())
        )
        had_existing_subscription = subscription is not None

        if subscription is None:
            subscription = UserSubscription(
                user_id=user_id,
                product_code=product_code,
                channel_id=channel_id,
                is_lifetime=plan["is_lifetime"],
                subscription_start=now,
                subscription_end=LIFETIME_END if plan["is_lifetime"] else now + timedelta(days=plan["duration_days"]),
            )
            session.add(subscription)
        else:
            subscription.channel_id = channel_id
            if plan["is_lifetime"] or subscription.is_lifetime:
                subscription.is_lifetime = True
                subscription.subscription_end = LIFETIME_END
            else:
                base_time = subscription.subscription_end if subscription.subscription_end > now else now
                subscription.subscription_end = base_time + timedelta(days=plan["duration_days"])
                if not subscription.subscription_start:
                    subscription.subscription_start = now

        await session.commit()
        await session.refresh(subscription)

        invite_link = None
        is_extension = had_existing_subscription and already_in_channel
        if not is_extension:
            invite_link = await create_single_use_invite_link(channel_id, subscription.invite_link)
            subscription.invite_link = invite_link
            await session.commit()

    return {
        "status": "success",
        "product_code": product_code,
        "plan_code": plan_code,
        "is_lifetime": plan["is_lifetime"],
        "subscription_end": subscription.subscription_end,
        "invite_link": invite_link,
        "already_in_channel": already_in_channel,
        "is_extension": is_extension,
    }


async def check_payment(transaction_hash: str, amount_received: float):
    async with async_session() as session:
        payment_info = await session.scalar(
            select(PaymentInfo)
            .where(PaymentInfo.transaction_hash == transaction_hash)
            .order_by(PaymentInfo.id.desc())
        )

        if not payment_info:
            return {"status": "no_transaction"}

        if datetime.now(timezone.utc) > payment_info.payment_window_end.astimezone(timezone.utc):
            return {"status": "expired"}

        if amount_received < payment_info.crypto_amount:
            return {"status": "insufficient_amount"}

        payment_info.status = "completed"
        await session.commit()

        return await activate_subscription(payment_info.user_id, payment_info.product_code, payment_info.plan_code)


async def verify_and_activate_hash_payment(user_id: int, transaction_hash: str):
    deposit_info = await find_matching_deposit(transaction_hash)
    if not deposit_info:
        return {"status": "not_found"}

    if deposit_info["status"] == "pending":
        return {"status": "pending"}

    linked_user = await get_user_id_by_transaction_hash(transaction_hash)
    if linked_user is not None and linked_user != user_id:
        return {"status": "used"}

    latest_payment = await get_latest_payment(user_id)
    if latest_payment is None:
        return {"status": "no_payment"}

    if latest_payment.ccy != deposit_info["ccy"]:
        return {
            "status": "currency_mismatch",
            "expected": latest_payment.ccy,
            "actual": deposit_info["ccy"],
        }

    await link_deposit_with_user(transaction_hash, user_id)
    await update_payment_info_with_hash(user_id, transaction_hash)
    return await check_payment(transaction_hash, deposit_info["amount"])


async def provide_productStars(user_id: int, product_code: str, plan_code: str):
    return await activate_subscription(user_id, product_code, plan_code)


async def add_subscription(user_id: int, start_date: datetime, end_date: datetime):
    async with async_session() as session:
        session.add(
            UserSubscription(
                user_id=user_id,
                product_code="mandy_rose",
                channel_id=CHANNEL_ID,
                is_lifetime=False,
                subscription_start=start_date,
                subscription_end=end_date,
            )
        )
        await session.commit()


async def extend_subscription_months(user_id: int, months: int, product_code: str = "mandy_rose"):
    now = datetime.now(timezone.utc)
    duration_days = 30 * months

    async with async_session() as session:
        subscription = await session.scalar(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.product_code == product_code,
            )
            .order_by(UserSubscription.id.desc())
        )

        if subscription is None:
            session.add(
                UserSubscription(
                    user_id=user_id,
                    product_code=product_code,
                    channel_id=PRODUCT_CHANNELS.get(product_code),
                    is_lifetime=False,
                    subscription_start=now,
                    subscription_end=now + timedelta(days=duration_days),
                )
            )
        else:
            base_time = subscription.subscription_end if subscription.subscription_end > now else now
            subscription.subscription_end = base_time + timedelta(days=duration_days)
        await session.commit()


async def admin_grant_access(user_id: int, product_code: str, months: int | None = None):
    now = datetime.now(timezone.utc)
    channel_id = PRODUCT_CHANNELS.get(product_code)
    is_lifetime = product_code == "anxieest"
    already_in_channel = await is_user_in_channel(user_id, channel_id)

    async with async_session() as session:
        subscription = await session.scalar(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.product_code == product_code,
            )
            .order_by(UserSubscription.id.desc())
        )
        had_existing_subscription = subscription is not None

        if subscription is None:
            subscription = UserSubscription(
                user_id=user_id,
                product_code=product_code,
                channel_id=channel_id,
                is_lifetime=is_lifetime,
                subscription_start=now,
                subscription_end=LIFETIME_END if is_lifetime else now + timedelta(days=30 * months),
            )
            session.add(subscription)
        else:
            subscription.channel_id = channel_id
            if is_lifetime:
                subscription.is_lifetime = True
                subscription.subscription_end = LIFETIME_END
            else:
                base_time = subscription.subscription_end if subscription.subscription_end > now else now
                subscription.subscription_end = base_time + timedelta(days=30 * months)

        await session.commit()
        await session.refresh(subscription)

        invite_link = None
        is_extension = had_existing_subscription and already_in_channel
        if not is_extension:
            invite_link = await create_single_use_invite_link(channel_id, subscription.invite_link)
            subscription.invite_link = invite_link
            await session.commit()

    return {
        "product_code": product_code,
        "is_lifetime": is_lifetime,
        "subscription_end": subscription.subscription_end,
        "invite_link": invite_link,
        "already_in_channel": already_in_channel,
        "is_extension": is_extension,
    }


async def admin_remove_access(user_id: int, product_code: str | None = None):
    async with async_session() as session:
        query = select(UserSubscription).where(UserSubscription.user_id == user_id)
        if product_code is not None:
            query = query.where(UserSubscription.product_code == product_code)

        result = await session.execute(query)
        subscriptions = result.scalars().all()

        if not subscriptions:
            return {"removed": [], "not_found": True}

        removed = []
        for subscription in subscriptions:
            removed.append(
                {
                    "product_code": subscription.product_code,
                    "channel_id": subscription.channel_id,
                    "invite_link": subscription.invite_link,
                }
            )
            await session.delete(subscription)

        await session.commit()

    if bot_instance is not None:
        for item in removed:
            channel_id = item["channel_id"]
            invite_link = item["invite_link"]
            await revoke_invite_link(channel_id, invite_link)
            if channel_id:
                try:
                    await bot_instance.ban_chat_member(channel_id, user_id)
                    await bot_instance.unban_chat_member(channel_id, user_id)
                except Exception as e:
                    print(f"Error removing user {user_id} from channel {channel_id}: {e}")

    return {"removed": removed, "not_found": False}


async def get_active_subscriptions(user_id: int):
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                ((UserSubscription.is_lifetime.is_(True)) | (UserSubscription.subscription_end > now)),
            )
            .order_by(UserSubscription.id.asc())
        )
        return result.scalars().all()


async def get_subscription(user_id: int):
    subscriptions = await get_active_subscriptions(user_id)
    if subscriptions:
        subscription = subscriptions[0]
        return subscription.subscription_start, subscription.subscription_end
    return None
