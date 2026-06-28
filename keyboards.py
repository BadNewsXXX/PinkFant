from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot_content import LANGUAGE_NAMES, MENU_TEXT, PAYMENT_METHOD_TEXT, PRODUCTS, menu_text, price_text, tr


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
    custom_order = None
    custom_labels = {}

    if language == "ru" and product_code in {"coomeet", "mandy_rose"}:
        custom_order = ["quarterly", "monthly", "yearly", "lifetime_request"]
        custom_labels = {
            "quarterly": "Премиум на 3 месяца (выгодно)💎",
            "monthly": "Премиум на 1 месяц",
            "yearly": "Премиум на 12 месяцев",
            "lifetime_request": "Пожизненный доступ 👑",
        }

    rows = [
        [
            InlineKeyboardButton(
                text=tr(language, "content_preview"),
                callback_data=f"preview:{product_code}",
            )
        ]
    ]
    plan_items = PRODUCTS[product_code]["plans"].items()
    if custom_order is not None:
        ordered_codes = [code for code in custom_order if code in PRODUCTS[product_code]["plans"]]
        plan_items = [(plan_code, PRODUCTS[product_code]["plans"][plan_code]) for plan_code in ordered_codes]

    rows.extend(
        [
            [
                InlineKeyboardButton(
                    text=custom_labels.get(plan_code, plan["button"][language]),
                    callback_data=f"plan:{product_code}:{plan_code}",
                )
            ]
            for plan_code, plan in plan_items
        ]
    )
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
    if language == "ru" and (
        (product_code == "anxieest" and plan_code == "lifetime")
        or (product_code in {"coomeet", "mandy_rose"} and plan_code in {"monthly", "quarterly", "yearly"})
    ):
        return anxieest_ru_payment_menu(product_code, plan_code)
    if language == "en":
        return en_payment_menu(product_code, plan_code)

    rows = []
    method_codes = ["trc20", "ton", "ltc", "stars"]

    for method_code in method_codes:
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


def en_payment_menu(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Crypto", callback_data=f"specialpay:crypto:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data=f"payment:{product_code}:{plan_code}:stars")],
            [InlineKeyboardButton(text="💳 Donation Alerts (Card)", callback_data=f"payment:{product_code}:{plan_code}:da")],
            [InlineKeyboardButton(text="Back to menu", callback_data=f"product:{product_code}")],
        ]
    )


def en_crypto_methods(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    amount = price_text("en", PRODUCTS[product_code]["plans"][plan_code]["price_usd"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ Pay {amount}",
                    callback_data=f"specialpay:checkout:{product_code}:{plan_code}:crypto",
                )
            ],
            [InlineKeyboardButton(text="💰 CryptoPay", callback_data=f"specialpay:cryptopay:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="✉️ Direct payment", callback_data=f"specialpay:direct:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="Back", callback_data=f"plan:{product_code}:{plan_code}")],
        ]
    )


def en_direct_crypto(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="USDT (TRC20)", callback_data=f"payment:{product_code}:{plan_code}:trc20")],
            [InlineKeyboardButton(text="Toncoin (TON)", callback_data=f"payment:{product_code}:{plan_code}:ton")],
            [InlineKeyboardButton(text="Litecoin (LTC)", callback_data=f"payment:{product_code}:{plan_code}:ltc")],
            [InlineKeyboardButton(text="Back", callback_data=f"specialpay:crypto:{product_code}:{plan_code}")],
        ]
    )


def anxieest_ru_payment_menu(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    amount = price_text("ru", PRODUCTS[product_code]["plans"][plan_code]["price_usd"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💳 Оплатить {amount} (QR/СБП)",
                    callback_data=f"specialpay:checkout:{product_code}:{plan_code}:default",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Другие способы оплаты",
                    callback_data=f"specialpay:other:{product_code}:{plan_code}",
                )
            ],
            [InlineKeyboardButton(text="Назад в меню", callback_data=f"product:{product_code}")],
        ]
    )


def anxieest_ru_other_methods(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Оплатить картой",
                    callback_data=f"specialpay:checkout:{product_code}:{plan_code}:card",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Криптовалюта",
                    callback_data=f"specialpay:crypto:{product_code}:{plan_code}",
                )
            ],
            [InlineKeyboardButton(text="⭐️ Телеграм звёзды", callback_data=f"payment:{product_code}:{plan_code}:stars")],
            [InlineKeyboardButton(text="Назад", callback_data=f"plan:{product_code}:{plan_code}")],
        ]
    )


def anxieest_ru_crypto_methods(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Оплатить",
                    callback_data=f"specialpay:checkout:{product_code}:{plan_code}:crypto",
                )
            ],
            [InlineKeyboardButton(text="💰 CryptoPay", callback_data=f"specialpay:cryptopay:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="✉️ Оплатить напрямую", callback_data=f"specialpay:direct:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"specialpay:other:{product_code}:{plan_code}")],
        ]
    )


def anxieest_ru_direct_crypto(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="USDT (TRC20)", callback_data=f"payment:{product_code}:{plan_code}:trc20")],
            [InlineKeyboardButton(text="Toncoin (TON)", callback_data=f"payment:{product_code}:{plan_code}:ton")],
            [InlineKeyboardButton(text="Litecoin (LTC)", callback_data=f"payment:{product_code}:{plan_code}:ltc")],
            [InlineKeyboardButton(text="Назад", callback_data=f"specialpay:crypto:{product_code}:{plan_code}")],
        ]
    )


def anxieest_ru_crypto_methods(product_code: str, plan_code: str) -> InlineKeyboardMarkup:
    amount = price_text("ru", PRODUCTS[product_code]["plans"][plan_code]["price_usd"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ Оплатить {amount}",
                    callback_data=f"specialpay:checkout:{product_code}:{plan_code}:crypto",
                )
            ],
            [InlineKeyboardButton(text="💰 CryptoPay", callback_data=f"specialpay:cryptopay:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="✉️ Оплатить напрямую", callback_data=f"specialpay:direct:{product_code}:{plan_code}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"specialpay:other:{product_code}:{plan_code}")],
        ]
    )


def payment_link(language: str, payment_url: str, back_callback: str) -> InlineKeyboardMarkup:
    open_label = "Открыть оплату" if language == "ru" else "Open payment"
    back_label = "Назад" if language == "ru" else "Back"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=open_label, url=payment_url)],
            [InlineKeyboardButton(text=back_label, callback_data=back_callback)],
        ]
    )


def simple_back(language: str, callback_data: str) -> InlineKeyboardMarkup:
    back_label = "Назад" if language == "ru" else "Back"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=back_label, callback_data=callback_data)],
        ]
    )


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
