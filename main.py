import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import aiohttp
import database.database as db
import keyboards as kb
import websockets
from aiohttp import web
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
    round_rub_amount,
    tr,
    usdt_amount_text,
    load_pricing_config,
)
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
db.set_bot(bot)

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "1867377574"))
PLATEGA_MERCHANT_ID = os.getenv("PLATEGA_MERCHANT_ID")
PLATEGA_SECRET = os.getenv("PLATEGA_SECRET")
PLATEGA_BASE_URL = os.getenv("PLATEGA_BASE_URL", "https://app.platega.io")
PLATEGA_RETURN_URL = os.getenv("PLATEGA_RETURN_URL")
PLATEGA_FAILED_URL = os.getenv("PLATEGA_FAILED_URL")
PLATEGA_CALLBACK_URL = os.getenv("PLATEGA_CALLBACK_URL")
PLATEGA_LISTEN_HOST = os.getenv("PLATEGA_LISTEN_HOST", "127.0.0.1")
PLATEGA_LISTEN_PORT = int(os.getenv("PLATEGA_LISTEN_PORT", "8080"))
BETATRANSFER_API_KEY = os.getenv("BETATRANSFER_API_KEY")
BETATRANSFER_SECRET_KEY = os.getenv("BETATRANSFER_SECRET_KEY")
BETATRANSFER_BASE_URL = os.getenv("BETATRANSFER_BASE_URL", "https://merchant.betatransfer.io")
BETATRANSFER_CALLBACK_URL = os.getenv("BETATRANSFER_CALLBACK_URL")
BETATRANSFER_SUCCESS_URL = os.getenv("BETATRANSFER_SUCCESS_URL")
BETATRANSFER_FAIL_URL = os.getenv("BETATRANSFER_FAIL_URL")
BETATRANSFER_CURRENCY = os.getenv("BETATRANSFER_CURRENCY", "USD").upper()
BETATRANSFER_PAYMENT_SYSTEM = (os.getenv("BETATRANSFER_PAYMENT_SYSTEM") or "").strip()
BETATRANSFER_FULL_CALLBACK = int(os.getenv("BETATRANSFER_FULL_CALLBACK", "1"))
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


def platega_amount_rub(price_usd: float | int) -> float:
    pricing_config = load_pricing_config()
    return float(
        round_rub_amount(
            float(price_usd) * float(pricing_config["usd_to_rub_rate"]),
            int(pricing_config["rub_rounding_step"]),
        )
    )


def build_platega_payload(user_id: int, product_code: str, plan_code: str) -> str:
    return f"platega:{user_id}:{product_code}:{plan_code}:{uuid.uuid4().hex[:12]}"


def generate_betatransfer_signature(params: list[str], secret_key: str) -> str:
    sign_string = "".join(params) + secret_key
    return hashlib.md5(sign_string.encode("utf-8")).hexdigest()


def build_betatransfer_signature_params(payload: dict, ordered_fields: list[str]) -> list[str]:
    params: list[str] = []
    for field in ordered_fields:
        value = payload.get(field)
        if value is None or value == "":
            continue
        params.append(str(value))
    return params


def betatransfer_locale(language: str) -> str:
    return language if language in {"en", "ru", "uk"} else "en"


def betatransfer_amount(price_usd: float | int, currency: str) -> str:
    normalized_currency = currency.upper()
    if normalized_currency == "RUB":
        return f"{platega_amount_rub(price_usd):.2f}"
    return f"{float(price_usd):.2f}"


def build_betatransfer_order_id(user_id: int, product_code: str, plan_code: str) -> str:
    product_map = {
        "anxieest": "anx",
        "coomeet": "coo",
        "mandy_rose": "mdy",
    }
    plan_map = {
        "lifetime": "life",
        "monthly": "m1",
        "quarterly": "m3",
        "yearly": "y12",
        "lifetime_request": "lreq",
    }
    product_part = product_map.get(product_code, "prd")
    plan_part = plan_map.get(plan_code, "pln")
    suffix = uuid.uuid4().hex[:8]
    return f"bt-{user_id}-{product_part}-{plan_part}-{suffix}"[:40]


BETATRANSFER_SIGN_FIELDS = [
    "orderId",
    "amount",
    "currency",
    "fullCallback",
]


def build_betatransfer_request_body(user_id: int, product_code: str, plan_code: str, language: str) -> tuple[dict, str, str]:
    plan = PRODUCTS[product_code]["plans"][plan_code]
    locale = betatransfer_locale(language)
    amount = betatransfer_amount(plan["price_usd"], BETATRANSFER_CURRENCY)
    order_id = build_betatransfer_order_id(user_id, product_code, plan_code)
    description = f"{product_name(product_code, 'en')} | {plan_name(product_code, plan_code, 'en')} | user {user_id}"

    request_body = {
        "orderId": order_id,
        "amount": amount,
        "currency": BETATRANSFER_CURRENCY,
        "urlResult": BETATRANSFER_CALLBACK_URL,
        "locale": locale,
        "user_comment": description,
        "fullCallback": BETATRANSFER_FULL_CALLBACK,
    }
    if BETATRANSFER_PAYMENT_SYSTEM:
        request_body["paymentSystem"] = BETATRANSFER_PAYMENT_SYSTEM
    if BETATRANSFER_SUCCESS_URL:
        request_body["urlSuccess"] = BETATRANSFER_SUCCESS_URL
    if BETATRANSFER_FAIL_URL:
        request_body["urlFail"] = BETATRANSFER_FAIL_URL

    return request_body, order_id, locale


async def create_platega_checkout(user_id: int, product_code: str, plan_code: str) -> dict:
    if not PLATEGA_MERCHANT_ID or not PLATEGA_SECRET:
        raise RuntimeError("Platega credentials are not configured.")
    if not PLATEGA_RETURN_URL or not PLATEGA_FAILED_URL:
        raise RuntimeError("Platega return URLs are not configured.")

    plan = PRODUCTS[product_code]["plans"][plan_code]
    if plan.get("support_only"):
        raise ValueError("This plan is support-only and cannot be paid automatically.")

    amount_rub = platega_amount_rub(plan["price_usd"])
    payload = build_platega_payload(user_id, product_code, plan_code)
    description = f"{product_name(product_code, 'en')} | {plan_name(product_code, plan_code, 'en')} | user {user_id}"
    request_body = {
        "paymentDetails": {
            "amount": amount_rub,
            "currency": "RUB",
        },
        "description": description,
        "return": PLATEGA_RETURN_URL,
        "failedUrl": PLATEGA_FAILED_URL,
        "payload": payload,
    }
    headers = {
        "Content-Type": "application/json",
        "X-MerchantId": PLATEGA_MERCHANT_ID,
        "X-Secret": PLATEGA_SECRET,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PLATEGA_BASE_URL}/v2/transaction/process",
            json=request_body,
            headers=headers,
        ) as response:
            response_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"Platega error {response.status}: {response_text}")
            data = json.loads(response_text)

    transaction_id = data.get("transactionId")
    redirect_url = data.get("url") or data.get("redirect")
    status = data.get("status", "PENDING")
    if not transaction_id or not redirect_url:
        raise RuntimeError(f"Unexpected Platega response: {data}")

    await db.create_platega_payment(
        user_id=user_id,
        product_code=product_code,
        plan_code=plan_code,
        amount=amount_rub,
        currency="RUB",
        description=description,
        payload=payload,
        transaction_id=transaction_id,
        redirect_url=redirect_url,
        status=status,
        payment_method=None,
        payment_method_code=None,
        return_url=PLATEGA_RETURN_URL,
        failed_url=PLATEGA_FAILED_URL,
        expires_in=data.get("expiresIn"),
    )

    return {
        "transaction_id": transaction_id,
        "payment_url": redirect_url,
        "amount_rub": amount_rub,
        "payload": payload,
        "status": status,
    }


async def create_platega_checkout_with_method(
    user_id: int,
    product_code: str,
    plan_code: str,
    payment_method: int,
    payment_method_code: str,
) -> dict:
    if not PLATEGA_MERCHANT_ID or not PLATEGA_SECRET:
        raise RuntimeError("Platega credentials are not configured.")
    if not PLATEGA_RETURN_URL or not PLATEGA_FAILED_URL:
        raise RuntimeError("Platega return URLs are not configured.")

    plan = PRODUCTS[product_code]["plans"][plan_code]
    amount_rub = platega_amount_rub(plan["price_usd"])
    payload = build_platega_payload(user_id, product_code, plan_code)
    description = f"{product_name(product_code, 'en')} | {plan_name(product_code, plan_code, 'en')} | user {user_id}"
    request_body = {
        "paymentMethod": payment_method,
        "paymentDetails": {
            "amount": amount_rub,
            "currency": "RUB",
        },
        "description": description,
        "return": PLATEGA_RETURN_URL,
        "failedUrl": PLATEGA_FAILED_URL,
        "payload": payload,
    }
    headers = {
        "Content-Type": "application/json",
        "X-MerchantId": PLATEGA_MERCHANT_ID,
        "X-Secret": PLATEGA_SECRET,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PLATEGA_BASE_URL}/transaction/process",
            json=request_body,
            headers=headers,
        ) as response:
            response_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"Platega error {response.status}: {response_text}")
            data = json.loads(response_text)

    transaction_id = data.get("transactionId")
    redirect_url = data.get("url") or data.get("redirect")
    status = data.get("status", "PENDING")
    if not transaction_id or not redirect_url:
        raise RuntimeError(f"Unexpected Platega response: {data}")

    await db.create_platega_payment(
        user_id=user_id,
        product_code=product_code,
        plan_code=plan_code,
        amount=amount_rub,
        currency="RUB",
        description=description,
        payload=payload,
        transaction_id=transaction_id,
        redirect_url=redirect_url,
        status=status,
        payment_method=payment_method,
        payment_method_code=payment_method_code,
        return_url=PLATEGA_RETURN_URL,
        failed_url=PLATEGA_FAILED_URL,
        expires_in=data.get("expiresIn"),
    )

    return {
        "transaction_id": transaction_id,
        "payment_url": redirect_url,
        "amount_rub": amount_rub,
        "payload": payload,
        "status": status,
    }


async def create_betatransfer_checkout(user_id: int, product_code: str, plan_code: str, language: str) -> dict:
    if not BETATRANSFER_API_KEY or not BETATRANSFER_SECRET_KEY:
        raise RuntimeError("BetaTransfer credentials are not configured.")
    if not BETATRANSFER_CALLBACK_URL:
        raise RuntimeError("BetaTransfer callback URL is not configured.")

    plan = PRODUCTS[product_code]["plans"][plan_code]
    if plan.get("support_only"):
        raise ValueError("This plan is support-only and cannot be paid automatically.")

    request_body, order_id, locale = build_betatransfer_request_body(user_id, product_code, plan_code, language)
    amount = request_body["amount"]
    description = request_body["user_comment"]

    request_body["sign"] = generate_betatransfer_signature(
        build_betatransfer_signature_params(request_body, BETATRANSFER_SIGN_FIELDS),
        BETATRANSFER_SECRET_KEY,
    )

    params = {"token": BETATRANSFER_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BETATRANSFER_BASE_URL}/api/payment",
            params=params,
            data=request_body,
        ) as response:
            response_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"BetaTransfer error {response.status}: {response_text}")
            data = json.loads(response_text)

    payment_url = data.get("url")
    provider_payment_id = str(data.get("id") or "").strip()
    provider_hash = str(data.get("hash") or "").strip()
    status = str(data.get("status") or "created")
    if not payment_url:
        raise RuntimeError(f"Unexpected BetaTransfer response: {data}")

    await db.create_betatransfer_payment(
        user_id=user_id,
        product_code=product_code,
        plan_code=plan_code,
        amount=float(amount),
        currency=BETATRANSFER_CURRENCY,
        locale=locale,
        description=description,
        order_id=order_id,
        status=status,
        callback_url=BETATRANSFER_CALLBACK_URL,
        success_url=BETATRANSFER_SUCCESS_URL,
        fail_url=BETATRANSFER_FAIL_URL,
        payment_system=BETATRANSFER_PAYMENT_SYSTEM or None,
        payment_url=payment_url,
        provider_payment_id=provider_payment_id or None,
        provider_hash=provider_hash or None,
        full_callback=BETATRANSFER_FULL_CALLBACK == 1,
    )

    return {
        "order_id": order_id,
        "payment_id": provider_payment_id,
        "payment_hash": provider_hash,
        "payment_url": payment_url,
        "amount": amount,
        "currency": BETATRANSFER_CURRENCY,
        "status": status,
        "locale": locale,
    }


async def get_betatransfer_payment_info(order_id: str | None = None, payment_id: str | None = None) -> dict:
    if not BETATRANSFER_API_KEY or not BETATRANSFER_SECRET_KEY:
        raise RuntimeError("BetaTransfer credentials are not configured.")
    if not order_id and not payment_id:
        raise ValueError("Either order_id or payment_id must be provided.")

    request_body: dict[str, str] = {}
    if order_id:
        request_body["orderId"] = order_id
    if payment_id:
        request_body["id"] = str(payment_id)

    sign_fields = ["id", "orderId"]
    request_body["sign"] = generate_betatransfer_signature(
        build_betatransfer_signature_params(request_body, sign_fields),
        BETATRANSFER_SECRET_KEY,
    )

    params = {"token": BETATRANSFER_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BETATRANSFER_BASE_URL}/api/info",
            params=params,
            data=request_body,
        ) as response:
            response_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"BetaTransfer info error {response.status}: {response_text}")
            return json.loads(response_text)


def special_payment_flow(language: str, product_code: str, plan_code: str) -> bool:
    if language == "ru":
        return (
            (product_code == "anxieest" and plan_code == "lifetime")
            or (product_code in {"coomeet", "mandy_rose"} and plan_code in {"monthly", "quarterly", "yearly"})
        )
    if language == "en":
        plan = PRODUCTS[product_code]["plans"].get(plan_code, {})
        return not plan.get("support_only", False)
    return False


def special_payment_method_label(method_code: str, language: str) -> str:
    labels = {
        "sbp": {"en": "QR / SBP", "ru": "QR / СБП"},
        "card": {"en": "Card", "ru": "Карта"},
        "crypto": {"en": "Cryptocurrency", "ru": "Криптовалюта"},
    }
    return labels[method_code][language]


def build_platega_payment_text(language: str, product_code: str, plan_code: str, method_code: str) -> str:
    method = special_payment_method_label(method_code, language)
    if language == "ru":
        return (
            f"<b>РЎРїРѕСЃРѕР± РѕРїР»Р°С‚С‹:</b> {method}\n"
            f"<b>РџСЂРѕРґСѓРєС‚:</b> {product_name(product_code, language)}\n"
            f"<b>РўР°СЂРёС„:</b> {plan_name(product_code, plan_code, language)}\n"
            f"<b>РЎСѓРјРјР°:</b> {price_text(language, PRODUCTS[product_code]['plans'][plan_code]['price_usd'])}\n\n"
            "РќР°Р¶РјРёС‚Рµ РєРЅРѕРїРєСѓ РЅРёР¶Рµ, С‡С‚РѕР±С‹ РѕС‚РєСЂС‹С‚СЊ СЃС‚СЂР°РЅРёС†Сѓ РѕРїР»Р°С‚С‹."
        )
    return (
        f"<b>Payment method:</b> {method}\n"
        f"<b>Product:</b> {product_name(product_code, language)}\n"
        f"<b>Plan:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Amount:</b> {price_text(language, PRODUCTS[product_code]['plans'][plan_code]['price_usd'])}\n\n"
        "Use the button below to open the payment page."
        if language == "en"
        else f"<b>Способ оплаты:</b> {method}\n"
        f"<b>Продукт:</b> {product_name(product_code, language)}\n"
        f"<b>Тариф:</b> {plan_name(product_code, plan_code, language)}\n"
        f"<b>Сумма:</b> {price_text(language, PRODUCTS[product_code]['plans'][plan_code]['price_usd'])}\n\n"
        "Нажмите кнопку ниже, чтобы открыть страницу оплаты."
    )


def special_payment_method_label(method_code: str, language: str) -> str:
    labels = {
        "default": {"en": "QR / SBP / Crypto", "ru": "QR / СБП / Криптовалюта"},
        "sbp": {"en": "QR / SBP", "ru": "QR / СБП"},
        "card": {"en": "Card", "ru": "Карта"},
        "crypto": {"en": "Cryptocurrency", "ru": "Криптовалюта"},
    }
    return labels[method_code][language]


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


async def send_access_result_to_user(user_id: int, result: dict):
    language = await get_user_language(user_id)
    product_label = product_name(result["product_code"], language)
    is_extension = result.get("is_extension", False)

    if is_extension:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is already active for life."
                if language == "en"
                else f"Р’Р°С€ РґРѕСЃС‚СѓРї Рє {product_label} СѓР¶Рµ Р°РєС‚РёРІРµРЅ РЅР°РІСЃРµРіРґР°."
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} subscription has been extended. Active until {end_date}."
                if language == "en"
                else f"Р’Р°С€Р° РїРѕРґРїРёСЃРєР° РЅР° {product_label} Р±С‹Р»Р° РїСЂРѕРґР»РµРЅР°. РђРєС‚РёРІРЅР° РґРѕ {end_date}."
            )
        await bot.send_message(user_id, text, parse_mode="HTML")
        return

    if result["invite_link"]:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is active for life.\nHere is your invite link:\n{result['invite_link']}"
                if language == "en"
                else f"Р’Р°С€ РґРѕСЃС‚СѓРї Рє {product_label} Р°РєС‚РёРІРёСЂРѕРІР°РЅ РЅР°РІСЃРµРіРґР°.\nР’РѕС‚ РІР°С€Р° СЃСЃС‹Р»РєР°-РїСЂРёРіР»Р°С€РµРЅРёРµ:\n{result['invite_link']}"
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} access is active until {end_date}.\nHere is your invite link:\n{result['invite_link']}"
                if language == "en"
                else f"Р’Р°С€ РґРѕСЃС‚СѓРї Рє {product_label} Р°РєС‚РёРІРёСЂРѕРІР°РЅ РґРѕ {end_date}.\nР’РѕС‚ РІР°С€Р° СЃСЃС‹Р»РєР°-РїСЂРёРіР»Р°С€РµРЅРёРµ:\n{result['invite_link']}"
            )
    else:
        if result["is_lifetime"]:
            text = (
                f"Your {product_label} access is active for life.\n"
                f"If the invite link was not generated automatically, contact support here:\n{SUPPORT_URL}"
                if language == "en"
                else f"Р’Р°С€ РґРѕСЃС‚СѓРї Рє {product_label} Р°РєС‚РёРІРёСЂРѕРІР°РЅ РЅР°РІСЃРµРіРґР°.\n"
                f"Р•СЃР»Рё СЃСЃС‹Р»РєР°-РїСЂРёРіР»Р°С€РµРЅРёРµ РЅРµ Р±С‹Р»Р° СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅР° Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё, РЅР°РїРёС€РёС‚Рµ РІ РїРѕРґРґРµСЂР¶РєСѓ СЃСЋРґР°:\n{SUPPORT_URL}"
            )
        else:
            end_date = result["subscription_end"].strftime("%Y-%m-%d")
            text = (
                f"Your {product_label} access is active until {end_date}.\n"
                f"If the invite link was not generated automatically, contact support here:\n{SUPPORT_URL}"
                if language == "en"
                else f"Р’Р°С€ РґРѕСЃС‚СѓРї Рє {product_label} Р°РєС‚РёРІРёСЂРѕРІР°РЅ РґРѕ {end_date}.\n"
                f"Р•СЃР»Рё СЃСЃС‹Р»РєР°-РїСЂРёРіР»Р°С€РµРЅРёРµ РЅРµ Р±С‹Р»Р° СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅР° Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё, РЅР°РїРёС€РёС‚Рµ РІ РїРѕРґРґРµСЂР¶РєСѓ СЃСЋРґР°:\n{SUPPORT_URL}"
            )

    await bot.send_message(user_id, text, parse_mode="HTML")


async def send_platega_access_result_to_user(user_id: int, result: dict):
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
        await bot.send_message(user_id, text, parse_mode="HTML")
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

    await bot.send_message(user_id, text, parse_mode="HTML")


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


@dp.message(Command("platega_test"))
async def platega_test(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "Usage:\n"
            "/platega_test 1 lifetime\n"
            "/platega_test 2 monthly\n"
            "/platega_test 2 quarterly\n"
            "/platega_test 3 yearly\n"
            "/platega_test 2 monthly <user_id>"
        )
        return

    try:
        product_choice = int(args[1])
    except ValueError:
        await message.reply("Invalid product choice.")
        return

    product_code = ADMIN_PRODUCT_CHOICES.get(product_choice)
    if product_code is None:
        await message.reply("Unknown product. Use 1 for Anxieest, 2 for CooMeet, 3 for Mandy Rose.")
        return

    plan_code = args[2].strip().lower()
    plan = PRODUCTS.get(product_code, {}).get("plans", {}).get(plan_code)
    if plan is None:
        await message.reply(f"Unknown plan '{plan_code}' for {product_name(product_code, 'en')}.")
        return
    if plan.get("support_only"):
        await message.reply("This plan is support-only and cannot be used for automatic Platega testing.")
        return

    target_user_id = message.from_user.id
    if len(args) >= 4:
        try:
            target_user_id = int(args[3])
        except ValueError:
            await message.reply("Invalid user_id.")
            return

    try:
        payment = await create_platega_checkout(target_user_id, product_code, plan_code)
    except Exception as e:
        await message.reply(f"Failed to create Platega payment: {e}")
        return

    await message.reply(
        "Platega test payment created.\n"
        f"User ID: {target_user_id}\n"
        f"Product: {product_name(product_code, 'en')}\n"
        f"Plan: {plan_name(product_code, plan_code, 'en')}\n"
        f"Amount: {payment['amount_rub']:.0f} ₽\n"
        f"Transaction ID: {payment['transaction_id']}\n"
        f"Callback URL: {PLATEGA_CALLBACK_URL}\n"
        f"Payment URL:\n{payment['payment_url']}"
    )


@dp.message(Command("beta_test"))
async def betatransfer_test(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "Usage:\n"
            "/beta_test 1 lifetime\n"
            "/beta_test 2 monthly\n"
            "/beta_test 2 quarterly\n"
            "/beta_test 3 yearly\n"
            "/beta_test 2 monthly <user_id>\n"
            "/beta_test 2 monthly <user_id> <locale>"
        )
        return

    try:
        product_choice = int(args[1])
    except ValueError:
        await message.reply("Invalid product choice.")
        return

    product_code = ADMIN_PRODUCT_CHOICES.get(product_choice)
    if product_code is None:
        await message.reply("Unknown product. Use 1 for Anxieest, 2 for CooMeet, 3 for Mandy Rose.")
        return

    plan_code = args[2].strip().lower()
    plan = PRODUCTS.get(product_code, {}).get("plans", {}).get(plan_code)
    if plan is None:
        await message.reply(f"Unknown plan '{plan_code}' for {product_name(product_code, 'en')}.")
        return
    if plan.get("support_only"):
        await message.reply("This plan is support-only and cannot be used for automatic BetaTransfer testing.")
        return

    target_user_id = message.from_user.id
    if len(args) >= 4:
        try:
            target_user_id = int(args[3])
        except ValueError:
            await message.reply("Invalid user_id.")
            return

    locale_language = "en"
    if len(args) >= 5:
        locale_language = args[4].strip().lower()

    try:
        payment = await create_betatransfer_checkout(target_user_id, product_code, plan_code, locale_language)
    except Exception as e:
        await message.reply(f"Failed to create BetaTransfer payment: {e}")
        return

    await message.reply(
        "BetaTransfer test payment created.\n"
        f"User ID: {target_user_id}\n"
        f"Product: {product_name(product_code, 'en')}\n"
        f"Plan: {plan_name(product_code, plan_code, 'en')}\n"
        f"Amount: {payment['amount']} {payment['currency']}\n"
        f"Order ID: {payment['order_id']}\n"
        f"Payment ID: {payment['payment_id'] or '-'}\n"
        f"Locale: {payment['locale']}\n"
        f"Callback URL: {BETATRANSFER_CALLBACK_URL}\n"
        f"Payment URL:\n{payment['payment_url']}"
    )


@dp.message(Command("beta_info"))
async def betatransfer_info(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Usage:\n/beta_info <order_id>")
        return

    order_id = args[1].strip()
    if not order_id:
        await message.reply("Order ID cannot be empty.")
        return

    try:
        info = await get_betatransfer_payment_info(order_id=order_id)
    except Exception as e:
        await message.reply(f"Failed to fetch BetaTransfer payment info: {e}")
        return

    await message.reply(
        "BetaTransfer payment info:\n"
        f"Order ID: {info.get('orderId', '-')}\n"
        f"Payment ID: {info.get('id', '-')}\n"
        f"Status: {info.get('status', '-')}\n"
        f"Amount: {info.get('amount', '-')}\n"
        f"Paid amount: {info.get('paidAmount', '-')}\n"
        f"Currency: {info.get('currency', '-')}\n"
        f"Payment system: {info.get('paymentSystem', '-')}\n"
        f"Created: {info.get('createdAt', '-')}\n"
        f"Updated: {info.get('updatedAt', '-')}"
    )


@dp.message(Command("beta_debug"))
async def betatransfer_debug(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "Usage:\n"
            "/beta_debug 1 lifetime\n"
            "/beta_debug 2 monthly\n"
            "/beta_debug 2 quarterly\n"
            "/beta_debug 3 yearly\n"
            "/beta_debug 2 monthly <user_id>\n"
            "/beta_debug 2 monthly <user_id> <locale>"
        )
        return

    try:
        product_choice = int(args[1])
    except ValueError:
        await message.reply("Invalid product choice.")
        return

    product_code = ADMIN_PRODUCT_CHOICES.get(product_choice)
    if product_code is None:
        await message.reply("Unknown product. Use 1 for Anxieest, 2 for CooMeet, 3 for Mandy Rose.")
        return

    plan_code = args[2].strip().lower()
    plan = PRODUCTS.get(product_code, {}).get("plans", {}).get(plan_code)
    if plan is None:
        await message.reply(f"Unknown plan '{plan_code}' for {product_name(product_code, 'en')}.")
        return

    target_user_id = message.from_user.id
    if len(args) >= 4:
        try:
            target_user_id = int(args[3])
        except ValueError:
            await message.reply("Invalid user_id.")
            return

    locale_language = "en"
    if len(args) >= 5:
        locale_language = args[4].strip().lower()

    request_body, order_id, locale = build_betatransfer_request_body(
        target_user_id,
        product_code,
        plan_code,
        locale_language,
    )
    sign_params = build_betatransfer_signature_params(request_body, BETATRANSFER_SIGN_FIELDS)
    sign_string_without_secret = "".join(sign_params)
    sign_value = generate_betatransfer_signature(sign_params, BETATRANSFER_SECRET_KEY or "")

    body_lines = [f"{key}={value}" for key, value in request_body.items()]
    params_lines = [f"{index + 1}. {value}" for index, value in enumerate(sign_params)]

    await message.reply(
        "BetaTransfer debug:\n"
        f"Product: {product_name(product_code, 'en')}\n"
        f"Plan: {plan_name(product_code, plan_code, 'en')}\n"
        f"User ID: {target_user_id}\n"
        f"Order ID: {order_id}\n"
        f"Locale: {locale}\n\n"
        "Request body:\n"
        f"<pre>{chr(10).join(body_lines)}</pre>\n"
        "Sign fields:\n"
        f"<pre>{chr(10).join(BETATRANSFER_SIGN_FIELDS)}</pre>\n"
        "Sign params:\n"
        f"<pre>{chr(10).join(params_lines)}</pre>\n"
        "Sign string:\n"
        f"<pre>{sign_string_without_secret}[SECRET]</pre>\n"
        f"MD5 sign: <pre>{sign_value}</pre>",
        parse_mode="HTML",
    )


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
        reply_markup=kb.product_back(language, product_code),
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


@dp.callback_query(F.data.startswith("specialpay:"))
async def special_payment_selected(callback: CallbackQuery):
    _, action, product_code, plan_code, *rest = callback.data.split(":")
    language = await get_user_language(callback.from_user.id)
    user_id = callback.from_user.id
    await callback.answer("")

    if not special_payment_flow(language, product_code, plan_code):
        await callback.message.edit_text(
            build_plan_text(language, product_code, plan_code),
            parse_mode="HTML",
            reply_markup=kb.payment_methods(language, product_code, plan_code),
        )
        return

    if action == "other":
        await callback.message.edit_text(
            build_plan_text(language, product_code, plan_code),
            parse_mode="HTML",
            reply_markup=kb.anxieest_ru_other_methods(product_code, plan_code),
        )
        return

    if action == "crypto":
        crypto_markup = (
            kb.anxieest_ru_crypto_methods(product_code, plan_code)
            if language == "ru"
            else kb.en_crypto_methods(product_code, plan_code)
        )
        await callback.message.edit_text(
            build_plan_text(language, product_code, plan_code),
            parse_mode="HTML",
            reply_markup=crypto_markup,
        )
        return

    if action == "direct":
        direct_markup = (
            kb.anxieest_ru_direct_crypto(product_code, plan_code)
            if language == "ru"
            else kb.en_direct_crypto(product_code, plan_code)
        )
        await callback.message.edit_text(
            build_plan_text(language, product_code, plan_code),
            parse_mode="HTML",
            reply_markup=direct_markup,
        )
        return

    if action == "cryptopay":
        text = "CryptoPay will be added later." if language == "en" else "CryptoPay добавим чуть позже."
        await callback.message.edit_text(
            text,
            reply_markup=kb.simple_back(language, f"specialpay:crypto:{product_code}:{plan_code}"),
        )
        return

    if action != "checkout" or not rest:
        return

    method_code = rest[0]
    if method_code == "card":
        return

    method_settings = {
        "default": {"payment_method": None, "back_callback": f"plan:{product_code}:{plan_code}"},
        "crypto": {"payment_method": 13, "back_callback": f"specialpay:crypto:{product_code}:{plan_code}"},
    }
    settings = method_settings.get(method_code)
    if settings is None:
        return

    try:
        if method_code == "default":
            payment = await create_platega_checkout(user_id, product_code, plan_code)
        else:
            payment = await create_platega_checkout_with_method(
                user_id,
                product_code,
                plan_code,
                settings["payment_method"],
                method_code,
            )
    except Exception as e:
        await callback.message.edit_text(
            (
                f"Не удалось создать платёж: {e}"
                if language == "ru"
                else f"Failed to create payment: {e}"
            ),
            reply_markup=kb.simple_back(language, settings["back_callback"]),
        )
        return

    await callback.message.edit_text(
        build_platega_payment_text(language, product_code, plan_code, method_code),
        parse_mode="HTML",
        reply_markup=kb.payment_link(language, payment["payment_url"], settings["back_callback"]),
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


async def platega_healthcheck(_: web.Request) -> web.Response:
    return web.json_response(
        {
            "ok": True,
            "service": "platega-callback",
            "callback_url": PLATEGA_CALLBACK_URL,
        }
    )


async def betatransfer_healthcheck(_: web.Request) -> web.Response:
    return web.json_response(
        {
            "ok": True,
            "service": "betatransfer-callback",
            "callback_url": BETATRANSFER_CALLBACK_URL,
        }
    )


async def parse_callback_payload(request: web.Request) -> dict:
    content_type = (request.content_type or "").lower()
    if "application/json" in content_type:
        payload = await request.json()
        return dict(payload)

    post_data = await request.post()
    return {key: value for key, value in post_data.items()}


def verify_betatransfer_callback_signature(payload: dict) -> bool:
    if not BETATRANSFER_SECRET_KEY:
        return False

    provided_signature = str(payload.get("sign") or payload.get("signature") or "").strip().lower()
    amount = payload.get("amount")
    order_id = payload.get("orderId")
    if not provided_signature or amount is None or not order_id:
        return False

    expected_signature = hashlib.md5(f"{amount}{order_id}{BETATRANSFER_SECRET_KEY}".encode("utf-8")).hexdigest()
    return provided_signature == expected_signature


async def platega_callback(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "invalid_json"}, status=400)

    transaction_id = str(payload.get("id") or "").strip()
    status = str(payload.get("status") or "").upper()

    if not transaction_id:
        return web.json_response({"ok": False, "error": "missing_transaction_id"}, status=400)

    payment = await db.get_platega_payment_by_transaction_id(transaction_id)
    if payment is None:
        return web.json_response({"ok": False, "error": "unknown_transaction"}, status=404)

    await db.update_platega_payment_status(
        transaction_id=transaction_id,
        status=status or payment.status,
        callback_payload=payload,
        callback_status=status or None,
        callback_processed=payment.callback_processed,
    )

    refreshed_payment = await db.get_platega_payment_by_transaction_id(transaction_id)
    if refreshed_payment is None:
        return web.json_response({"ok": False, "error": "payment_disappeared"}, status=500)

    if status != "CONFIRMED":
        return web.json_response({"ok": True, "message": f"status {status or 'UNKNOWN'} recorded"})

    if refreshed_payment.callback_processed or refreshed_payment.activated_at is not None:
        return web.json_response({"ok": True, "message": "duplicate callback ignored"})

    try:
        result = await db.activate_subscription(
            refreshed_payment.user_id,
            refreshed_payment.product_code,
            refreshed_payment.plan_code,
        )
        await db.mark_platega_payment_activated(transaction_id)
        try:
            await send_platega_access_result_to_user(refreshed_payment.user_id, result)
        except Exception:
            logging.exception("Platega payment confirmed, but failed to notify user.")
    except Exception:
        logging.exception("Failed to activate Platega payment for transaction %s", transaction_id)
        return web.json_response({"ok": False, "error": "activation_failed"}, status=500)

    return web.json_response({"ok": True, "message": "payment confirmed and access granted"})


async def betatransfer_callback(request: web.Request) -> web.Response:
    try:
        payload = await parse_callback_payload(request)
    except Exception:
        return web.json_response({"ok": False, "error": "invalid_callback_payload"}, status=400)

    order_id = str(payload.get("orderId") or "").strip()
    status = str(payload.get("status") or "").lower()

    if not order_id:
        return web.json_response({"ok": False, "error": "missing_order_id"}, status=400)

    payment = await db.get_betatransfer_payment_by_order_id(order_id)
    if payment is None:
        return web.json_response({"ok": False, "error": "unknown_order"}, status=404)

    if not verify_betatransfer_callback_signature(payload):
        logging.warning("BetaTransfer callback signature mismatch for order %s", order_id)
        return web.json_response({"ok": False, "error": "invalid_signature"}, status=400)

    provider_payment_id = str(payload.get("id") or "").strip() or None
    provider_hash = str(payload.get("hash") or "").strip() or None

    await db.update_betatransfer_payment_status(
        order_id=order_id,
        status=status or payment.status,
        callback_payload=payload,
        callback_status=status or None,
        callback_processed=payment.callback_processed,
        provider_payment_id=provider_payment_id,
        provider_hash=provider_hash,
        payment_url=str(payload.get("url") or "").strip() or None,
    )

    refreshed_payment = await db.get_betatransfer_payment_by_order_id(order_id)
    if refreshed_payment is None:
        return web.json_response({"ok": False, "error": "payment_disappeared"}, status=500)

    if status != "success":
        return web.json_response({"ok": True, "message": f"status {status or 'unknown'} recorded"})

    if refreshed_payment.callback_processed or refreshed_payment.activated_at is not None:
        return web.json_response({"ok": True, "message": "duplicate callback ignored"})

    try:
        result = await db.activate_subscription(
            refreshed_payment.user_id,
            refreshed_payment.product_code,
            refreshed_payment.plan_code,
        )
        await db.mark_betatransfer_payment_activated(order_id)
        try:
            await send_platega_access_result_to_user(refreshed_payment.user_id, result)
        except Exception:
            logging.exception("BetaTransfer payment succeeded, but failed to notify user.")
    except Exception:
        logging.exception("Failed to activate BetaTransfer payment for order %s", order_id)
        return web.json_response({"ok": False, "error": "activation_failed"}, status=500)

    return web.json_response({"ok": True, "message": "payment confirmed and access granted"})


async def run_platega_http_server():
    app = web.Application()
    app.router.add_get("/api/betatransfer/health", betatransfer_healthcheck)
    app.router.add_post("/api/betatransfer/callback", betatransfer_callback)
    app.router.add_get("/api/platega/health", platega_healthcheck)
    app.router.add_post("/api/platega/callback", platega_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, PLATEGA_LISTEN_HOST, PLATEGA_LISTEN_PORT)
    await site.start()
    logging.info("Callback server started on http://%s:%s", PLATEGA_LISTEN_HOST, PLATEGA_LISTEN_PORT)

    await asyncio.Event().wait()


async def main():
    ltc_rate, ton_rate = await asyncio.gather(get_crypto_rate("LTC"), get_crypto_rate("GRAM"))
    print(f"LTC rate: {ltc_rate}, TON rate: {ton_rate}")

    await db.init_db()
    auth_subscribe_task = asyncio.create_task(authenticate_and_ping())
    bot_task = asyncio.create_task(dp.start_polling(bot))
    scheduler_task = asyncio.create_task(db.scheduler())
    platega_web_task = asyncio.create_task(run_platega_http_server())

    await asyncio.gather(auth_subscribe_task, bot_task, scheduler_task, platega_web_task)


if __name__ == "__main__":
    asyncio.run(main())
