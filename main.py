import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

import aiohttp
import database.database as db
import keyboards as kb
import websockets
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery, SuccessfulPayment
from bot_content import (
    DEFAULT_LANGUAGE,
    FAQ_TEXT,
    LANGUAGE_NAMES,
    LTC_ADDRESS,
    MENU_TEXT,
    PREVIEW_TEXT,
    PRODUCTS,
    SUPPORT_TEXT,
    SUPPORT_URL,
    TON_ADDRESS,
    TRC20_ADDRESS,
    menu_text,
    plan_name,
    price_text,
    prices_text,
    product_name,
    tr,
    usdt_amount_text,
)
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
db.set_bot(bot)

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "1867377574"))
MENU_VARIANTS = {key: tuple(values.values()) for key, values in MENU_TEXT.items()}
ADMIN_PRODUCT_CHOICES = {
    1: "anxieest",
    2: "coomeet",
    3: "mandy_rose",
}
def replace_price_line(text: str, display_price: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "</b>:" in line and "$" in line:
            prefix, _, _ = line.partition("</b>:")
            lines[index] = f"{prefix}</b>: {display_price}"
            break
    return "\n".join(lines)


def build_faq_text(language: str, product_code: str) -> str:
    text = FAQ_TEXT[product_code][language]
    plans = PRODUCTS[product_code]["plans"]

    if product_code == "anxieest":
        return replace_price_line(text, price_text(language, plans["lifetime"]["price_usd"]))

    ordered_codes = [code for code in ("monthly", "quarterly", "yearly") if code in plans]
    display_prices = prices_text(language, *(plans[code]["price_usd"] for code in ordered_codes))
    return replace_price_line(text, display_prices)


def build_manual_payment_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    if language == "en":
        return (
            f"<b>Payment method:</b> Via Telegram\n"
            f"<b>Product:</b> {product_name(product_code, language)}\n"
            f"<b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Cost:</b> {display_price}\n"
            f"<b>Your ID:</b> {user_id}\n\n"
            f"Contact me here to complete the payment manually:\n{SUPPORT_URL}"
        )
    return (
        f"<b>Способ оплаты:</b> Через Telegram\n"
        f"<b>Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Стоимость:</b> {display_price}\n"
        f"<b>Ваш ID:</b> {user_id}\n\n"
        f"Напишите мне сюда, чтобы завершить оплату вручную:\n{SUPPORT_URL}"
    )


def build_donation_alerts_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    donation_alerts_url = "https://www.donationalerts.com/r/wweuniverse69"
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Donation Alerts\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>💰 Cost:</b> {display_price}\n"
            f"<b>Your ID:</b> {user_id}\n\n"
            f"1. Open the link below:\n{donation_alerts_url}\n\n"
            "2. Send the exact amount shown above.\n"
            "3. Put your Telegram ID into the message field.\n"
            "4. After payment, wait for transaction approval ✅\n\n"
            "If you have questions, contact support : https://t.me/PinkLeakSupport"
        )
    return (
        f"<b>Способ оплаты:</b> Donation Alerts\n"
        f"<b>Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Стоимость:</b> {display_price}\n"
        f"<b>Ваш ID:</b> {user_id}\n\n"
        f"1. Откройте ссылку ниже:\n{donation_alerts_url}\n\n"
        "2. Отправьте точную сумму, указанную выше.\n"
        "3. В поле сообщения укажите ваш Telegram ID.\n"
        "4. После оплаты дождитесь окончания транзакции ✅\n\n"
        "Если у Вас остались какие-то вопросы, напишите в поддержку : https://t.me/PinkLeakSupport"
    )


async def create_signature(timestamp, method, request_path, body=""):
    if body == "{}" or body is None:
        body = ""
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        bytes(os.getenv("OKX_secret_key"), encoding="utf-8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode("utf-8")


async def get_time():
    timestamp = int(datetime.now(timezone.utc).timestamp())
    return str(timestamp)


async def ping_pong(websocket):
    while True:
        try:
            await websocket.ping()
            print("Ping sent")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Ping error: {e}")
            break


async def authenticate_and_ping():
    url = "wss://ws.okx.com:8443/ws/v5/business"
    async with websockets.connect(url, open_timeout=15, ping_timeout=None, ping_interval=None) as websocket:
        print("WebSocket connection established")

        timestamp = await get_time()
        signature = await create_signature(timestamp, "GET", "/users/self/verify", "")

        login_message = {
            "op": "login",
            "args": [
                {
                    "apiKey": os.getenv("OKX_api_key"),
                    "passphrase": os.getenv("OKX_passphrase"),
                    "timestamp": timestamp,
                    "sign": signature,
                }
            ],
        }
        await websocket.send(json.dumps(login_message))
        auth_response = await websocket.recv()
        print(f"Authentication response: {auth_response}")

        subscribe_message = {
            "op": "subscribe",
            "args": [{"channel": "deposit-info", "uid": "429658822286951495"}],
        }
        await websocket.send(json.dumps(subscribe_message))
        response = await websocket.recv()
        print(f"Subscription response: {response}")

        await asyncio.gather(handle_responses(websocket), ping_pong(websocket))


async def handle_responses(websocket):
    while True:
        try:
            response = await websocket.recv()
            print("Received response:", response)

            try:
                data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                continue

            if "data" not in data:
                continue

            for deposit in data["data"]:
                tx_id = deposit.get("txId")
                amount = deposit.get("amt")
                state = deposit.get("state")
                timestamp = deposit.get("ts")
                currency = deposit.get("ccy")

                if not tx_id:
                    continue

                try:
                    amount = float(amount)
                    state = int(state)
                    timestamp = datetime.fromtimestamp(float(timestamp) / 1000)
                except (TypeError, ValueError):
                    continue

                await db.handle_deposit(tx_id, amount, state, timestamp, currency)

        except websockets.ConnectionClosedOK:
            print("WebSocket connection closed by server")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


async def get_crypto_rate(crypto_symbol: str) -> float:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {"symbol": crypto_symbol, "convert": "USDT"}
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv("CMC_api_key"),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data["data"][crypto_symbol]["quote"]["USDT"]["price"]


class TransactionState(StatesGroup):
    waiting_for_hash = State()


async def get_user_language(user_id: int) -> str:
    return await db.get_user_language(user_id)


def format_duration(language: str, plan: dict) -> str:
    if plan["is_lifetime"]:
        return "Lifetime" if language == "en" else "Навсегда"
    return f"{plan['duration_days']} days" if language == "en" else f"{plan['duration_days']} дней"


def build_plan_text(language: str, product_code: str, plan_code: str) -> str:
    product = PRODUCTS[product_code]
    plan = product["plans"][plan_code]
    if "custom_text" in plan:
        return replace_price_line(plan["custom_text"][language], price_text(language, plan["price_usd"]))
    features = "\n".join(f"- {feature}" for feature in plan["features"][language])
    duration_label = "Duration" if language == "en" else "Длительность"
    price_label = "Price" if language == "en" else "Цена"
    important_label = "Important" if language == "en" else "Важно"

    return (
        f"<b>{plan_name(product_code, plan_code, language)}</b>\n"
        f"{product['intro'][language]}\n\n"
        f"{features}\n\n"
        f"⚠️ <b>{important_label}:</b>\n"
        f"{plan['description'][language]}\n\n"
        f"<b>{duration_label}:</b> {format_duration(language, plan)}\n"
        f"<b>{price_label}:</b> {price_text(language, plan['price_usd'])}\n\n"
        f"<b>{tr(language, 'choose_payment_method')}</b>"
    )


def build_trc20_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    exact_usdt = usdt_amount_text(plan["price_usd"])
    if language == "en":
        return (
            f"💳 <b>Payment method:</b> USDT (TRC20)\n"
            f"🔞 <b>Product:</b> {product_name(product_code, language)}\n"
            f"💎 <b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"💰 <b>Price:</b> {plan['price_usd']}$\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>Payment address:</b>\n<pre>{TRC20_ADDRESS}</pre>\n\n"
            "Send funds to the address above, send your transaction hash below, then press the button 'I paid'."
        )
    return (
        f"<b>💳 Способ оплаты:</b> USDT (TRC20)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>💰 Цена:</b> {plan['price_usd']}$\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>Адрес для оплаты:</b>\n<pre>{TRC20_ADDRESS}</pre>\n\n"
        "Отправьте средства на адрес выше, затем отправьте хеш транзакции в сообщении, после нажмите 'Я оплатил'."
    )


def build_ton_intro_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    if language == "en":
        return (
            f"💳 <b>Payment method:</b> Toncoin (TON)\n"
            f"🔞 <b>Product:</b> {product_name(product_code, language)}\n"
            f"💎 <b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"💰 <b>Cost:</b> {plan['price_usd']}$\n\n"
            "Press <b>Start payment</b>, copy the exact amount, address (without memo), then send the transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Toncoin (TON)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {plan['price_usd']}$\n\n"
        "Нажмите <b>Начать оплату</b>, скопируйте точную сумму, адрес (без MEMO), а затем после оплаты отправьте хеш транзакции."
    )


def build_ton_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Toncoin (TON)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Cost:</b> {plan['price_usd']}$\n"
            f"<b>Address:</b>\n<pre>{TON_ADDRESS}</pre>\n"
            f"<b>Amount (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy the address, exact amount, then send the transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Toncoin (TON)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {plan['price_usd']}$\n"
        f"<b>Адрес:</b>\n<pre>{TON_ADDRESS}</pre>\n"
        f"<b>Сумма (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте адрес, точную сумму, а затем после оплаты отправьте хеш транзакции."
    )


def build_ltc_intro_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Litecoin (LTC)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Cost:</b> {plan['price_usd']}$\n\n"
            "Press <b>Start payment</b>, copy the exact amount and address, then send your transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Litecoin (LTC)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {plan['price_usd']}$\n\n"
        "Нажмите <b>Начать оплату</b>, скопируйте точную сумму и адрес, а затем после оплаты отправьте хеш транзакции."
    )


def build_ltc_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Litecoin (LTC)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Price:</b> {plan['price_usd']}$\n"
            f"<b>Address:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
            f"<b>Amount (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy address, exact amount, then send the transaction hash below after payment."

        )
    return (
        f"<b>💳 Способ оплаты:</b> Litecoin (LTC)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Цена:</b> {plan['price_usd']}$\n"
        f"<b>Адрес:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
        f"<b>Сумма (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте точную сумму и адрес, а затем после оплаты отправьте хеш транзакции."
    )


def build_trc20_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    exact_usdt = usdt_amount_text(plan["price_usd"])
    if language == "en":
        return (
            f"💳 <b>Payment method:</b> USDT (TRC20)\n"
            f"🔞 <b>Product:</b> {product_name(product_code, language)}\n"
            f"💎 <b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"💰 <b>Price:</b> {display_price}\n"
            f"<b>Amount (USDT):</b> {exact_usdt}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>Payment address:</b>\n<pre>{TRC20_ADDRESS}</pre>\n\n"
            "Send funds to the address above, send your transaction hash below, then press the button 'I paid'."
        )
    return (
        f"<b>💳 Способ оплаты:</b> USDT (TRC20)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>💰 Цена:</b> {display_price}\n"
        f"<b>Сумма (USDT):</b> {exact_usdt}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>Адрес для оплаты:</b>\n<pre>{TRC20_ADDRESS}</pre>\n\n"
        "Отправьте средства на адрес выше, затем отправьте хеш транзакции в сообщении, после нажмите 'Я оплатил'."
    )


def build_ton_intro_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    if language == "en":
        return (
            f"💳 <b>Payment method:</b> Toncoin (TON)\n"
            f"🔞 <b>Product:</b> {product_name(product_code, language)}\n"
            f"💎 <b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"💰 <b>Cost:</b> {display_price}\n\n"
            "Press <b>Start payment</b>, copy the exact amount, address (without memo), then send the transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Toncoin (TON)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {display_price}\n\n"
        "Нажмите <b>Начать оплату</b>, скопируйте точную сумму, адрес (без MEMO), а затем после оплаты отправьте хеш транзакции."
    )


def build_ton_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Toncoin (TON)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Cost:</b> {display_price}\n"
            f"<b>Address:</b>\n<pre>{TON_ADDRESS}</pre>\n"
            f"<b>Amount (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy the address, exact amount, then send the transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Toncoin (TON)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {display_price}\n"
        f"<b>Адрес:</b>\n<pre>{TON_ADDRESS}</pre>\n"
        f"<b>Сумма (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте адрес, точную сумму, а затем после оплаты отправьте хеш транзакции."
    )


def build_ltc_intro_text(language: str, product_code: str, plan_code: str, user_id: int) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Litecoin (LTC)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Cost:</b> {display_price}\n\n"
            "Press <b>Start payment</b>, copy the exact amount and address, then send your transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Litecoin (LTC)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Стоимость:</b> {display_price}\n\n"
        "Нажмите <b>Начать оплату</b>, скопируйте точную сумму и адрес, а затем после оплаты отправьте хеш транзакции."
    )


def build_ltc_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    display_price = price_text(language, plan["price_usd"])
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Litecoin (LTC)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>💰 Price:</b> {display_price}\n"
            f"<b>Address:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
            f"<b>Amount (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy address, exact amount, then send the transaction hash below after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Litecoin (LTC)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>💰 Цена:</b> {display_price}\n"
        f"<b>Адрес:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
        f"<b>Сумма (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте точную сумму и адрес, а затем после оплаты отправьте хеш транзакции."
    )


def build_ton_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Toncoin (TON)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>Address:</b>\n<pre>{TON_ADDRESS}</pre>\n"
            f"<b>Amount (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy the address, exact amount, then send the transaction hash after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Toncoin (TON)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>Адрес:</b>\n<pre>{TON_ADDRESS}</pre>\n"
        f"<b>Сумма (TON):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте адрес, точную сумму, а затем после оплаты отправьте хеш транзакции."
    )


def build_ltc_live_text(
    language: str,
    product_code: str,
    plan_code: str,
    user_id: int,
    crypto_amount: float,
    payment_window_end: datetime,
) -> str:
    if language == "en":
        return (
            f"<b>💳 Payment method:</b> Litecoin (LTC)\n"
            f"<b>🔞 Product:</b> {product_name(product_code, language)}\n"
            f"<b>💎 Plan:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>Your ID:</b> {user_id}\n"
            f"<b>Address:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
            f"<b>Amount (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
            f"<b>⏳ Payment window ends:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
            "Please, copy address, exact amount, then send the transaction hash below after payment."
        )
    return (
        f"<b>💳 Способ оплаты:</b> Litecoin (LTC)\n"
        f"<b>🔞 Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>💎 Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Ваш ID:</b> {user_id}\n"
        f"<b>Адрес:</b>\n<pre>{LTC_ADDRESS}</pre>\n"
        f"<b>Сумма (LTC):</b>\n<pre>{crypto_amount:.8f}</pre>\n"
        f"<b>⏳ Окно оплаты до:</b> {payment_window_end.strftime('%H:%M:%S')} UTC\n"
        "Пожалуйста, скопируйте точную сумму и адрес, а затем после оплаты отправьте хеш транзакции."
    )


async def send_access_result(target: Message, user_id: int, result: dict):
    language = await get_user_language(user_id)
    product_label = product_name(result["product_code"], language)
    is_extension = result.get("is_extension", False)

    if is_extension:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is already active for life."
                if language == "en"
                else f"Ваш доступ к {product_label} уже активен навсегда."
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} subscription has been extended. Active until {end_date}."
                if language == "en"
                else f"Ваша подписка на {product_label} была продлена. Активна до {end_date}."
            )
        await target.answer(text, parse_mode="HTML")
        return

    if result["invite_link"]:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is active for life.\nHere is your invite link:\n{result['invite_link']}"
                if language == "en"
                else f"Ваш доступ к {product_label} активирован навсегда.\nВот ваша ссылка-приглашение:\n{result['invite_link']}"
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} access is active until {end_date}.\nHere is your invite link:\n{result['invite_link']}"
                if language == "en"
                else f"Ваш доступ к {product_label} активирован до {end_date}.\nВот ваша ссылка-приглашение:\n{result['invite_link']}"
            )
    else:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is active for life.\n"
                f"If the invite link was not generated automatically, contact support here:\n{SUPPORT_URL}"
                if language == "en"
                else f"Ваш доступ к {product_label} активирован навсегда.\n"
                f"Если ссылка-приглашение не была сгенерирована автоматически, напишите в поддержку сюда:\n{SUPPORT_URL}"
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} access is active until {end_date}.\n"
                f"If the invite link was not generated automatically, contact support here:\n{SUPPORT_URL}"
                if language == "en"
                else f"Ваш доступ к {product_label} активирован до {end_date}.\n"
                f"Если ссылка-приглашение не была сгенерирована автоматически, напишите в поддержку сюда:\n{SUPPORT_URL}"
            )

    await target.answer(text, parse_mode="HTML")


@dp.message(Command("as"))
async def add_subscription(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "Usage:\n"
            "/as <user_id> 1\n"
            "/as <user_id> 2 <months>\n"
            "/as <user_id> 3 <months>"
        )
        return

    try:
        user_id = int(args[1])
        product_choice = int(args[2])
    except ValueError:
        await message.reply("Invalid arguments.")
        return

    product_code = ADMIN_PRODUCT_CHOICES.get(product_choice)
    if product_code is None:
        await message.reply("Unknown product. Use 1 for Anxieest, 2 for CooMeet, 3 for Mandy Rose.")
        return

    months = None
    if product_code != "anxieest":
        if len(args) < 4:
            await message.reply("Please provide the number of months for this product.")
            return
        try:
            months = int(args[3])
            if months <= 0:
                raise ValueError
        except ValueError:
            await message.reply("Invalid number of months.")
            return
    else:
        if len(args) >= 4:
            try:
                extra_value = int(args[3])
                if extra_value not in (0,):
                    await message.reply("For Anxieest use /as <user_id> 1 or /as <user_id> 1 0")
                    return
            except ValueError:
                await message.reply("For Anxieest use /as <user_id> 1 or /as <user_id> 1 0")
                return

    try:
        result = await db.admin_grant_access(user_id, product_code, months)
    except Exception as e:
        await message.reply(f"Failed to add user {user_id}: {e}")
        return

    invite_link = result.get("invite_link")
    product_label = product_name(product_code, "en")
    if invite_link:
        await bot.send_message(user_id, f"Your link to the channel: {invite_link}.")

    if result["is_lifetime"]:
        await message.reply(f"User {user_id} received lifetime access to {product_label}.")
    else:
        await message.reply(f"User {user_id}'s access to {product_label} was extended by {months} month(s).")


@dp.message(Command("rs"))
async def remove_subscription(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply(
            "Usage:\n"
            "/rs <user_id>\n"
            "/rs <user_id> 1\n"
            "/rs <user_id> 2\n"
            "/rs <user_id> 3"
        )
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("Invalid user_id.")
        return

    product_code = None
    if len(args) >= 3:
        try:
            product_choice = int(args[2])
        except ValueError:
            await message.reply("Invalid product choice.")
            return
        product_code = ADMIN_PRODUCT_CHOICES.get(product_choice)
        if product_code is None:
            await message.reply("Unknown product. Use 1 for Anxieest, 2 for CooMeet, 3 for Mandy Rose.")
            return

    result = await db.admin_remove_access(user_id, product_code)

    if result["not_found"]:
        if product_code is None:
            await message.reply(f"No subscriptions found for user {user_id}.")
        else:
            await message.reply(f"No subscription found for user {user_id} in {product_name(product_code, 'en')}.")
        return

    if product_code is None:
        removed_labels = ", ".join(product_name(item["product_code"], "en") for item in result["removed"])
        await message.reply(f"Removed subscriptions for user {user_id}: {removed_labels}.")
    else:
        await message.reply(f"Removed {product_name(product_code, 'en')} subscription for user {user_id}.")


@dp.message(Command("ls"))
async def list_subscriptions(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage:\n/ls <user_id>")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("Invalid user_id.")
        return

    subscriptions = await db.get_active_subscriptions(user_id)
    if not subscriptions:
        await message.reply(f"No active subscriptions found for user {user_id}.")
        return

    lines = [f"Active subscriptions for user {user_id}:"]
    for subscription in subscriptions:
        label = product_name(subscription.product_code, "en")
        if subscription.is_lifetime:
            lines.append(f"- {label}: lifetime")
        else:
            lines.append(f"- {label}: until {subscription.subscription_end.strftime('%Y-%m-%d')}")

    await message.reply("\n".join(lines))


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.add_user(message.from_user.id)
    await message.answer("Пожалуйста, выберите язык. / Please choose your language.", reply_markup=kb.language_selector())


@dp.message(F.text.in_(MENU_VARIANTS["language"]))
async def choose_language_from_menu(message: types.Message):
    await message.answer("Пожалуйста, выберите язык. / Please choose your language.", reply_markup=kb.language_selector())


@dp.callback_query(F.data.startswith("lang:"))
async def save_language(callback: CallbackQuery):
    language = callback.data.split(":", 1)[1]
    await db.add_user(callback.from_user.id)
    await db.set_user_language(callback.from_user.id, language)
    await callback.answer(LANGUAGE_NAMES.get(language, DEFAULT_LANGUAGE))
    chat_id = callback.message.chat.id
    await callback.message.delete()
    await bot.send_message(chat_id, tr(language, "menu_ready"), reply_markup=kb.main_menu(language))
    await bot.send_message(chat_id, tr(language, "products_welcome"), reply_markup=kb.product_selector(language))


@dp.message(F.text.in_(MENU_VARIANTS["subscriptions"]))
async def subscription_menu(message: types.Message):
    language = await get_user_language(message.from_user.id)
    await message.answer(tr(language, "products_welcome"), reply_markup=kb.product_selector(language))


@dp.callback_query(F.data == "menu:products")
async def product_menu_callback(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await callback.message.edit_text(tr(language, "products_welcome"), reply_markup=kb.product_selector(language))


@dp.message(F.text.in_(MENU_VARIANTS["support"]))
async def support_handler(message: types.Message):
    language = await get_user_language(message.from_user.id)
    await message.answer(SUPPORT_TEXT[language], parse_mode="HTML", reply_markup=kb.support_back(language))


@dp.message(F.text.in_(MENU_VARIANTS["faq"]))
async def faq_handler(message: types.Message):
    language = await get_user_language(message.from_user.id)
    await message.answer(tr(language, "faq_welcome"), reply_markup=kb.faq_selector(language))


@dp.callback_query(F.data == "menu:faq")
async def faq_menu_callback(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await callback.message.edit_text(tr(language, "faq_welcome"), reply_markup=kb.faq_selector(language))


@dp.callback_query(F.data.startswith("faq:"))
async def faq_product_selected(callback: CallbackQuery):
    _, product_code = callback.data.split(":", 1)
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await callback.message.edit_text(
        build_faq_text(language, product_code),
        parse_mode="HTML",
        reply_markup=kb.faq_actions(language, product_code),
    )


@dp.callback_query(F.data.startswith("product:"))
async def product_selected(callback: CallbackQuery):
    _, product_code = callback.data.split(":", 1)
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await callback.message.edit_text(
        PRODUCTS[product_code]["intro"][language],
        parse_mode="HTML",
        reply_markup=kb.product_plans(language, product_code),
    )


@dp.callback_query(F.data.startswith("preview:"))
async def preview_selected(callback: CallbackQuery):
    _, product_code = callback.data.split(":", 1)
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await callback.message.edit_text(
        PREVIEW_TEXT[product_code][language],
        reply_markup=kb.support_back(language),
    )


@dp.callback_query(F.data.startswith("plan:"))
async def plan_selected(callback: CallbackQuery):
    _, product_code, plan_code = callback.data.split(":")
    language = await get_user_language(callback.from_user.id)
    plan = PRODUCTS[product_code]["plans"][plan_code]
    await callback.answer("")
    if plan.get("support_only"):
        await callback.message.edit_text(
            plan["custom_text"][language],
            parse_mode="HTML",
            reply_markup=kb.product_back(language, product_code),
        )
        return
    await callback.message.edit_text(
        build_plan_text(language, product_code, plan_code),
        parse_mode="HTML",
        reply_markup=kb.payment_methods(language, product_code, plan_code),
    )


@dp.callback_query(F.data.startswith("payment:"))
async def payment_selected(callback: CallbackQuery):
    _, product_code, plan_code, method_code = callback.data.split(":")
    language = await get_user_language(callback.from_user.id)
    plan = PRODUCTS[product_code]["plans"][plan_code]
    user_id = callback.from_user.id
    await callback.answer("")

    if method_code == "manual":
        text = build_manual_payment_text(language, product_code, plan_code, user_id)
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=kb.donation_alerts_back(language, product_code, plan_code),
        )
        return

    if method_code == "da":
        text = build_donation_alerts_text(language, product_code, plan_code, user_id)
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=kb.donation_alerts_back(language, product_code, plan_code),
        )
        return

    if method_code == "stars":
        invoice_description = plan.get("description", {}).get(language)
        if not invoice_description:
            invoice_description = (
                "Purchase access via Telegram Stars."
                if language == "en"
                else "Покупка доступа через Telegram Stars."
            )
        prices = [LabeledPrice(label=plan_name(product_code, plan_code, language), amount=plan["stars_amount"])]
        await bot.send_invoice(
            callback.message.chat.id,
            title=plan_name(product_code, plan_code, language),
            description=invoice_description,
            currency="XTR",
            prices=prices,
            start_parameter=f"stars_{product_code}_{plan_code}",
            payload=f"stars:{product_code}:{plan_code}",
        )
        return

    if method_code == "trc20":
        await db.create_manual_usdt_payment(user_id, product_code, plan_code)
        await callback.message.edit_text(
            build_trc20_text(language, product_code, plan_code, user_id),
            parse_mode="HTML",
            reply_markup=kb.hash_confirmation(language, product_code, plan_code),
        )
        return

    if method_code == "ton":
        await callback.message.edit_text(
            build_ton_intro_text(language, product_code, plan_code, user_id),
            parse_mode="HTML",
            reply_markup=kb.crypto_start(language, product_code, plan_code, method_code),
        )
        return

    if method_code == "ltc":
        await callback.message.edit_text(
            build_ltc_intro_text(language, product_code, plan_code, user_id),
            parse_mode="HTML",
            reply_markup=kb.crypto_start(language, product_code, plan_code, method_code),
        )


@dp.callback_query(F.data.startswith("crypto:start:"))
async def crypto_start(callback: CallbackQuery):
    _, _, product_code, plan_code, method_code = callback.data.split(":")
    language = await get_user_language(callback.from_user.id)
    user_id = callback.from_user.id
    await callback.answer("")

    if method_code == "ton":
        crypto_rate = await get_crypto_rate("GRAM")
        crypto_amount, payment_window_end = await db.initiate_paymentTON(user_id, product_code, plan_code, crypto_rate)
        text = build_ton_live_text(language, product_code, plan_code, user_id, crypto_amount, payment_window_end)
    else:
        crypto_rate = await get_crypto_rate("LTC")
        crypto_amount, payment_window_end = await db.initiate_paymentLTC(user_id, product_code, plan_code, crypto_rate)
        text = build_ltc_live_text(language, product_code, plan_code, user_id, crypto_amount, payment_window_end)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.crypto_live(language, product_code, plan_code),
    )


@dp.callback_query(F.data.startswith("crypto:cancel:"))
async def crypto_cancel(callback: CallbackQuery):
    _, _, product_code, plan_code = callback.data.split(":")
    language = await get_user_language(callback.from_user.id)
    await db.cancel_payment(callback.from_user.id)
    await callback.answer(tr(language, "payment_cancelled"))
    await callback.message.edit_text(
        build_plan_text(language, product_code, plan_code),
        parse_mode="HTML",
        reply_markup=kb.payment_methods(language, product_code, plan_code),
    )


@dp.callback_query(F.data.startswith("hash:"))
async def ask_for_hash(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    await callback.answer("")
    await state.set_state(TransactionState.waiting_for_hash)
    await callback.message.answer(tr(language, "enter_hash"))


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    successful_payment: SuccessfulPayment = message.successful_payment
    payload = successful_payment.invoice_payload
    language = await get_user_language(message.from_user.id)

    if not payload.startswith("stars:"):
        await message.answer("Unknown payment payload." if language == "en" else "Неизвестный payload оплаты.")
        return

    _, product_code, plan_code = payload.split(":")
    result = await db.provide_productStars(message.from_user.id, product_code, plan_code)
    await send_access_result(message, message.from_user.id, result)


@dp.message(StateFilter(TransactionState.waiting_for_hash))
async def process_transaction_hash(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    transaction_hash = (message.text or "").strip()

    if len(transaction_hash) not in (64, 66):
        await message.answer(tr(language, "hash_invalid"))
        await state.clear()
        return

    result = await db.verify_and_activate_hash_payment(message.from_user.id, transaction_hash)
    status = result["status"]

    if status == "success":
        await send_access_result(message, message.from_user.id, result)
    elif status == "used":
        await message.answer(tr(language, "hash_used"))
    elif status == "pending":
        await message.answer(tr(language, "hash_pending"))
    elif status == "not_found":
        await message.answer(tr(language, "hash_not_found"))
    elif status == "currency_mismatch":
        await message.answer(tr(language, "currency_mismatch").format(expected=result["expected"], actual=result["actual"]))
    elif status == "insufficient_amount":
        await message.answer("Insufficient amount." if language == "en" else "Недостаточная сумма.")
    elif status == "expired":
        await message.answer("Payment window expired." if language == "en" else "Окно оплаты истекло.")
    elif status == "no_payment":
        await message.answer("No active payment found." if language == "en" else "Активный платёж не найден.")
    else:
        await message.answer("Payment verification failed." if language == "en" else "Не удалось проверить оплату.")

    await state.clear()


@dp.message(F.text.in_(MENU_VARIANTS["my_subscription"]))
async def my_subscriptions(message: types.Message):
    language = await get_user_language(message.from_user.id)
    subscriptions = await db.get_active_subscriptions(message.from_user.id)

    if not subscriptions:
        await message.answer(tr(language, "no_subscription"), reply_markup=kb.buy_from_subscription(language))
        return

    lines = [tr(language, "my_subscriptions_intro")]
    for subscription in subscriptions:
        localized_product = product_name(subscription.product_code, language)
        if subscription.is_lifetime:
            lines.append(tr(language, "subscription_lifetime").format(product=localized_product))
        else:
            lines.append(
                tr(language, "subscription_until").format(
                    product=localized_product,
                    date=subscription.subscription_end.strftime("%Y-%m-%d"),
                )
            )

    await message.answer("\n".join(lines), parse_mode="HTML")


async def main():
    ltc_rate, ton_rate = await asyncio.gather(get_crypto_rate("LTC"), get_crypto_rate("GRAM"))
    print(f"LTC rate: {ltc_rate}, TON rate: {ton_rate}")

    await db.init_db()
    auth_subscribe_task = asyncio.create_task(authenticate_and_ping())
    bot_task = asyncio.create_task(dp.start_polling(bot))
    scheduler_task = asyncio.create_task(db.scheduler())

    await asyncio.gather(auth_subscribe_task, bot_task, scheduler_task)


if __name__ == "__main__":
    asyncio.run(main())
