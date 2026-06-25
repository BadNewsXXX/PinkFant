from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot_content import LANGUAGE_NAMES, MENU_TEXT, PAYMENT_METHOD_TEXT, PRODUCTS, menu_text, tr


def language_selector() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LANGUAGE_NAMES["ru"], callback_data="lang:ru"),
                InlineKeyboardButton(text=LANGUAGE_NAMES["en"], callback_data="lang:en"),
            ]
        ]
    )


def main_menu(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=menu_text(language, "subscriptions")),
                KeyboardButton(text=menu_text(language, "my_subscription")),
            ],
            [
                KeyboardButton(text=menu_text(language, "support")),
                KeyboardButton(text=menu_text(language, "faq")),
            ],
            [KeyboardButton(text=menu_text(language, "language"))],
        ],
        resize_keyboard=True,
        input_field_placeholder="Select menu item...",
    )


def product_selector(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=PRODUCTS["anxieest"]["name"][language], callback_data="product:anxieest")],
            [InlineKeyboardButton(text=PRODUCTS["coomeet"]["name"][language], callback_data="product:coomeet")],
            [InlineKeyboardButton(text=PRODUCTS["mandy_rose"]["name"][language], callback_data="product:mandy_rose")],
        ]
    )


def faq_selector(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=PRODUCTS["anxieest"]["name"][language], callback_data="faq:anxieest")],
            [InlineKeyboardButton(text=PRODUCTS["coomeet"]["name"][language], callback_data="faq:coomeet")],
            [InlineKeyboardButton(text=PRODUCTS["mandy_rose"]["name"][language], callback_data="faq:mandy_rose")],
        ]
    )


def faq_back(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data="menu:faq")]
        ]
    )


def faq_actions(language: str, product_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "get_access"), callback_data=f"product:{product_code}")],
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data="menu:faq")],
        ]
    )


def support_back(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data="menu:products")]
        ]
    )


def product_back(language: str, product_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data=f"product:{product_code}")]
        ]
    )


def product_plans(language: str, product_code: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=tr(language, "content_preview"),
                callback_data=f"preview:{product_code}",
            )
        ]
    ]
    rows.extend([
        [
            InlineKeyboardButton(
                text=plan["button"][language],
                callback_data=f"plan:{product_code}:{plan_code}",
            )
        ]
        for plan_code, plan in PRODUCTS[product_code]["plans"].items()
    ])
    rows.append(
        [
            InlineKeyboardButton(
                text=tr(language, "back_to_products"),
                callback_data="menu:products",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_methods(language: str, product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    rows = []
    for method_code in ("manual", "trc20", "ton", "ltc", "stars", "da"):
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🌎 {PAYMENT_METHOD_TEXT[method_code][language]}",
                    callback_data=f"payment:{product_code}:{plan_code}:{method_code}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=tr(language, "back_to_menu"),
                callback_data=f"product:{product_code}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def hash_confirmation(language: str, product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "i_paid"), callback_data=f"hash:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data=f"plan:{product_code}:{plan_code}")],
        ]
    )


def crypto_start(language: str, product_code: str, plan_code: str, method_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=tr(language, "start_payment"),
                    callback_data=f"crypto:start:{product_code}:{plan_code}:{method_code}",
                )
            ],
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data=f"plan:{product_code}:{plan_code}")],
        ]
    )


def crypto_live(language: str, product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "i_paid"), callback_data=f"hash:{product_code}:{plan_code}")],
            [
                InlineKeyboardButton(
                    text=tr(language, "cancel_payment"),
                    callback_data=f"crypto:cancel:{product_code}:{plan_code}",
                )
            ],
        ]
    )


def donation_alerts_back(language: str, product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "back_to_menu"), callback_data=f"plan:{product_code}:{plan_code}")]
        ]
    )


def buy_from_subscription(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "buy_access"), callback_data="menu:products")]
        ]
    )
