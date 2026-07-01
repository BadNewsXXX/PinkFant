from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


DEFAULT_LANGUAGE = "en"
LIFETIME_END = datetime(2099, 12, 31)

SUPPORT_URL = "https://t.me/PinkLeakSupport"
CONTENT_SAMPLES_URL = "https://t.me/your_public_channel"
DONATION_ALERTS_URL = "https://www.donationalerts.com/r/wweuniverse69"

TRC20_ADDRESS = "TGsNKiNTHRxMXmymYRzV73TkwidzJLV4Uu"
TON_ADDRESS = "UQACJ-XRCODtBALYuVuBSCIgNmLGW-7-GS9suDmlS_ani32p"
LTC_ADDRESS = "MPaZJcoVdhUeNerRaYKVkcLgxpNwjQPhif"

# RU prices are displayed from USD using a configurable rate and clean rounding.
USD_TO_RUB_RATE = 90
RUB_ROUNDING_STEP = 50
PRICING_CONFIG_PATH = Path(__file__).with_name("pricing_config.json")

PRODUCT_CHANNELS = {
    "anxieest": -1003968958494,
    "coomeet": -1003956372346,
    "mandy_rose": -1002087896627,
}

LANGUAGE_NAMES = {
    "en": "🇺🇸 English",
    "ru": "🇷🇺 Русский",
}

MENU_TEXT = {
    "subscriptions": {
        "en": "Subscriptions 💵",
        "ru": "Подписки 💵",
    },
    "my_subscription": {
        "en": "My subscriptions ⏳",
        "ru": "Мои подписки ⏳",
    },
    "support": {
        "en": "Support ⚙️",
        "ru": "Поддержка ⚙️",
    },
    "faq": {
        "en": "FAQ ❔",
        "ru": "FAQ ❔",
    },
    "language": {
        "en": "Language 🌐",
        "ru": "Язык 🌐",
    },
}

PAYMENT_METHOD_TEXT = {
    "manual": {
        "en": "Via Telegram",
        "ru": "Через Telegram",
    },
    "trc20": {
        "en": "Crypto: USDT (TRC20)",
        "ru": "Крипто: USDT (TRC20)",
    },
    "ton": {
        "en": "Crypto: Toncoin (TON)",
        "ru": "Крипто: Toncoin (TON)",
    },
    "ltc": {
        "en": "Crypto: Litecoin (LTC)",
        "ru": "Крипто: Litecoin (LTC)",
    },
    "stars": {
        "en": "Telegram Stars",
        "ru": "Telegram Stars",
    },
    "da": {
        "en": "Donation Alerts",
        "ru": "Donation Alerts",
    },
}

PRODUCTS = {
    "anxieest": {
        "name": {
            "en": "Anxieest (OnlyFans)",
            "ru": "Anxieest (OnlyFans)",
        },
        "intro": {
            "en": "Choose how you want to get access to anxieest.",
            "ru": "Выберите, как вы хотите получить доступ к anxieest.",
        },
        "plans": {
            "lifetime": {
                "button": {
                    "en": "Lifetime access 💎",
                    "ru": "Пожизненный доступ 💎",
                },
                "title": {
                    "en": "Lifetime access 💎",
                    "ru": "Пожизненный доступ 💎",
                },
                "duration_days": None,
                "is_lifetime": True,
                "price_usd": 10,
                "stars_amount": 500,
                "custom_text": {
                    "en": (
                        "In private channel : \n"
                        "• 2 photos of her ass\n"
                        "• anal plug + dildo masturbation video 🔞\n"
                        "💰<b>Price</b>: 10$\n"
                        "🔗 After your purchase, private channel link will be sent to you.\n"
                        "⏳<b>Duration</b> : Forever ✅\n\n"
                        "❗️ This is rare archival material that was previously on her OnlyFans but was later removed."
                        ),
                    "ru": (
                        "В приватном канале с Anxieest есть :\n"
                        "• 2 фото её попки\n"
                        "• видео с анальной пробкой и трах дилдо 🔞\n"
                        "💰<b>Стоимость</b>: 10$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : Навсегда ✅\n\n"
                        "❗️ Это редкий архивный материал, который ранее был на её OnlyFans, но в последствии был удалён."
                    ),
                "description": {
                    "en": "Purchase permanent access to the channel",
                    "ru": "Приобрести навсегда доступ к каналу",
                },
                },
            }
        },
    },
    "coomeet": {
        "name": {
            "en": "CooMeet",
            "ru": "CooMeet",
        },
        "intro": {
            "en": (
                "Choose the subscription plan for Coomeet."
            ),
            "ru": (
                "Выберите тариф подписки для Coomeet."
            ),
        },
        "plans": {
            "monthly": {
                "button": {
                    "en": "Premium access for 1 month 💎",
                    "ru": "Премиум-доступ на 1 месяц 💎",
                },
                "title": {
                    "en": "Premium access for 1 month",
                    "ru": "Премиум-доступ на 1 месяц",
                },
                "duration_days": 30,
                "is_lifetime": False,
                "price_usd": 6,
                "stars_amount": 300,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• 500+ videos from Coomeet girls featuring a wide variety of content from different countries.\n"
                        "• A large part of the collection includes content that is not publicly available.\n\n"
                        "❗️ <b>Updates</b>\n"
                        "Content is updated regularly. Private channel subscribers can also take part in polls and influence which model will appear in future updates.\n\n\n"
                        "💰<b>Price</b>: 6$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 1 month ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 500+ видео девушек Coomeet с разным контентом и из разных стран.\n"
                        "• Большая часть контента - эксклюзив, которого нет в открытом доступе.\n\n"
                        "❗️ <b>Обновления</b>\n"
                        "Контент обновляется на постоянной основе. Подписчики приватного канала могут участвовать в опросах и влиять на то, с какой моделью выйдет следующий контент.\n\n\n"
                        "💰<b>Стоимость</b>: 6$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 1 месяц ✅"
                    ),
                },
                "features": {
                    "en": [
                        "Private coomeet access",
                        "30 days of access",
                        "The public/private split can be expanded later",
                    ],
                    "ru": [
                        "Доступ к приватному coomeet",
                        "30 дней доступа",
                        "Разделение на public/private можно расширить позже",
                    ],
                },
                "description": {
                    "en": "This option gives 30 days of access.",
                    "ru": "Этот вариант даёт 30 дней доступа.",
                },
            },
            "quarterly": {
                "button": {
                    "en": "Premium access for 3 months 💎",
                    "ru": "Премиум-доступ на 3 месяца 💎",
                },
                "title": {
                    "en": "Premium access for 3 months",
                    "ru": "Премиум-доступ на 3 месяца",
                },
                "duration_days": 90,
                "is_lifetime": False,
                "price_usd": 14,
                "stars_amount": 700,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• 500+ videos from Coomeet girls featuring a wide variety of content from different countries.\n"
                        "• A large part of the collection includes content that is not publicly available.\n\n"
                        "❗️ <b>Updates</b>\n"
                        "Content is updated regularly. Private channel subscribers can also take part in polls and influence which model will appear in future updates.\n\n\n"
                        "💰<b>Price</b>: 14$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 3 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 500+ видео девушек Coomeet с разным контентом и из разных стран.\n"
                        "• Большая часть контента - эксклюзив, которого нет в открытом доступе.\n\n"
                        "❗️ <b>Обновления</b>\n"
                        "Контент обновляется на постоянной основе. Подписчики приватного канала могут участвовать в опросах и влиять на то, с какой моделью выйдет следующий контент.\n\n\n"
                        "💰<b>Стоимость</b>: 14$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 3 месяца ✅"
                    ),
                },
                "features": {
                    "en": [
                        "Private coomeet access",
                        "90 days of access",
                        "The public/private split can be expanded later",
                    ],
                    "ru": [
                        "Доступ к приватному coomeet",
                        "90 дней доступа",
                        "Разделение на public/private можно расширить позже",
                    ],
                },
                "description": {
                    "en": "This option gives 90 days of access.",
                    "ru": "Этот вариант даёт 90 дней доступа.",
                },
            },
            "yearly": {
                "button": {
                    "en": "Premium access for 12 months 💎",
                    "ru": "Премиум-доступ на 12 месяцев 💎",
                },
                "title": {
                    "en": "Premium access for 12 months",
                    "ru": "Премиум-доступ на 12 месяцев",
                },
                "duration_days": 360,
                "is_lifetime": False,
                "price_usd": 49,
                "stars_amount": 2450,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• 500+ videos from Coomeet girls featuring a wide variety of content from different countries.\n"
                        "• A large part of the collection includes content that is not publicly available.\n\n"
                        "❗️ <b>Updates</b>\n"
                        "Content is updated regularly. Private channel subscribers can also take part in polls and influence which model will appear in future updates.\n\n\n"
                        "💰<b>Price</b>: 49$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 12 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 500+ видео девушек Coomeet с разным контентом и из разных стран.\n"
                        "• Большая часть контента - эксклюзив, которого нет в открытом доступе.\n\n"
                        "❗️ <b>Обновления</b>\n"
                        "Контент обновляется на постоянной основе. Подписчики приватного канала могут участвовать в опросах и влиять на то, с какой моделью выйдет следующий контент.\n\n\n"
                        "💰<b>Стоимость</b>: 49$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 12 месяцев ✅"
                    ),
                },
                "description": {
                    "en": "This option gives 12 months of access.",
                    "ru": "Этот вариант даёт 12 месяцев доступа.",
                },
            },
            "lifetime_request": {
                "button": {
                    "en": "Lifetime access 💎",
                    "ru": "Пожизненный доступ 💎",
                },
                "title": {
                    "en": "Lifetime access",
                    "ru": "Пожизненный доступ",
                },
                "duration_days": None,
                "is_lifetime": False,
                "support_only": True,
                "custom_text": {
                    "en": "💎 Lifetime access is available upon request.\nContact support for more details.",
                    "ru": "👑 Пожизненный доступ доступен в индивидуальном формате.\nСвяжитесь с поддержкой, чтобы узнать подробности и условия получения доступа.",
                },
            },
        }
    },
    "mandy_rose": {
        "name": {
            "en": "Mandy Rose",
            "ru": "Mandy Rose",
        },
        "intro": {
            "en": (
                "Choose the subscription plan for Mandy Rose."
            ),
            "ru": (
                "Выберите тариф подписки для Mandy Rose."
            ),
        },
        "plans": {
            "monthly": {
                "button": {
                    "en": "Premium access for 1 month 💎",
                    "ru": "Премиум-доступ на 1 месяц 💎",
                },
                "title": {
                    "en": "Premium access for 1 month",
                    "ru": "Премиум-доступ на 1 месяц",
                },
                "duration_days": 30,
                "is_lifetime": False,
                "price_usd": 5,
                "stars_amount": 250,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• Mandy Sacs's OnlyFans content (current and previous)\n"
                        "• Mandy Sacs's Fansly content (previous)\n"
                        "• Mandy Sacs's Fantime content (previous)\n\n"
                        "❗️ Collection includes content from multiple platforms in one place.\n\n\n"
                        "💰<b>Price</b>: 5$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 1 month ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
	                    "• Удалённый контент с Fantime 🔞\n"
                        "• Удалённый контент с Fansly 🔞\n\n\n"
                        "💰<b>Стоимость</b>: 5$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 1 месяц ✅"
                    ),
                },
            },
            "quarterly": {
                "button": {
                    "en": "Premium access for 3 months 💎",
                    "ru": "Премиум-доступ на 3 месяца 💎",
                },
                "title": {
                    "en": "Premium access for 3 months",
                    "ru": "Премиум-доступ на 3 месяца",
                },
                "duration_days": 90,
                "is_lifetime": False,
                "price_usd": 12,
                "stars_amount": 600,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• Mandy Sacs's OnlyFans content (current and previous)\n"
                        "• Mandy Sacs's Fansly content (previous)\n"
                        "• Mandy Sacs's Fantime content (previous)\n\n"
                        "❗️ Collection includes content from multiple platforms in one place.\n\n\n"
                        "💰<b>Price</b>: 12$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 3 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
	                    "• Удалённый контент с Fantime 🔞\n"
                        "• Удалённый контент с Fansly 🔞\n\n\n"
                        "💰<b>Стоимость</b>: 12$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 3 месяцa ✅"
                    ),
                },
            },
            "yearly": {
                "button": {
                    "en": "Premium access for 12 months 💎",
                    "ru": "Премиум-доступ на 12 месяцев 💎",
                },
                "title": {
                    "en": "Premium access for 12 months",
                    "ru": "Премиум-доступ на 12 месяцев",
                },
                "duration_days": 360,
                "is_lifetime": False,
                "price_usd": 39,
                "stars_amount": 1950,
                "custom_text": {
                    "en": (
                        "Inside the private channel you’ll get:\n"
                        "• Mandy Sacs's OnlyFans content (current and previous)\n"
                        "• Mandy Sacs's Fansly content (previous)\n"
                        "• Mandy Sacs's Fantime content (previous)\n\n"
                        "❗️ Collection includes content from multiple platforms in one place.\n\n\n"
                        "💰<b>Price</b>: 39$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 12 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
                        "• Удалённый контент с Fantime 🔞\n"
                        "• Удалённый контент с Fansly 🔞\n\n\n"
                        "💰<b>Стоимость</b>: 39$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : 12 месяцев ✅"
                    ),
                },
                "description": {
                    "en": "This option gives 12 months of access.",
                    "ru": "Этот вариант даёт 12 месяцев доступа.",
                },
            },
            "lifetime_request": {
                "button": {
                    "en": "Lifetime access 💎",
                    "ru": "Пожизненный доступ 💎",
                },
                "title": {
                    "en": "Lifetime access",
                    "ru": "Пожизненный доступ",
                },
                "duration_days": None,
                "is_lifetime": False,
                "support_only": True,
                "custom_text": {
                    "en": "💎 Lifetime access is available upon request.\nContact support for more details.",
                    "ru": "👑 Пожизненный доступ доступен в индивидуальном формате.\nСвяжитесь с поддержкой, чтобы узнать подробности и условия получения доступа.",
                },
            },
        },
    },
}

PREVIEW_TEXT = {
    "anxieest": {
        "en": "Preview content is available via the link : https://t.me/+B2cN062YW6tjNjk6",
        "ru": "Ознакомиться с превью контента можно по ссылке : https://t.me/+B2cN062YW6tjNjk6",
    },
    "coomeet": {
        "en": "Preview content is available via the link : https://t.me/+M2cR7lys0AhiMmYy",
        "ru": "Ознакомиться с превью контента можно по ссылке : https://t.me/+M2cR7lys0AhiMmYy",
    },
    "mandy_rose": {
        "en": "The public channel is available via the link : https://t.me/wwe_superstarsMRs.",
        "ru": "Ознакомиться с публичным каналом можно по ссылке : https://t.me/wwe_superstarsMRs",
    },
}

SUPPORT_TEXT = {
    "en": (
        "<b>1. Why PinkLeak is worth it</b> 💎\n\n"
        "We collect content from various platforms and models to provide it to you at reasonable and affordable prices. "
        "On official platforms (OnlyFans, Coomeet, etc.), content is often overpriced.\n\n"
        "❗️ A significant part of the content is not publicly available.\n\n"
        "Our goal is to give you the best content without unnecessary overpaying or limitations. Your support helps us grow and improve the service.\n\n"
        "<b>2. Payment issues</b> 💳\n\n"
        "Did you complete a payment but something went wrong?\n"
        "Send us a direct message — we’ll quickly help you sort it out. Our support is available 24/7.\n\n"
        "<b>3. No convenient payment method</b> ⚙️\n\n"
        "Can’t find a suitable payment method?\n"
        "If none of the available payment methods work for you, feel free to message us. We’ll do our best to find a convenient solution.\n"
        "Support is available 24/7. 🟢\n\n"
        "<b>4. Content samples</b> 👀\n\n"
        "Open Subscriptions and choose any product you’re interested in. Then tap Content Preview to view sample content before purchasing.\n\n"
        "<b>5. Will new models and categories be added?</b> 😈\n\n"
        "Yes, we plan to expand our content library based on the interests of our audience.\n"
        "If you’d like to influence future updates, take part in the poll using the link below.\n\n\n"
        "<b>Need more help?</b> 🤝\n"
        f"If you read the all answers above and still need help, contact support: {SUPPORT_URL}\n\n\n\n"
        "Privacy policy: https://telegra.ph/Privacy-Policy-06-09-143\n"
        "User agreement: https://telegra.ph/User-Agreement-06-09-57"
    ),
    "ru": (
        "<b>1. Почему PinkLeak — это выгодно?</b> 💎\n\n"
        "Мы собираем контент с разных платформ и от разных моделей, чтобы предоставить его вам по доступным и удобным ценам.\n\n"
        "На официальных площадках (OnlyFans, Coomeet и др.) стоимость контента часто завышена, а также могут возникать сложности с оплатой и пополнением баланса.\n\n"
        "❗️ Значительная часть материалов недоступна в открытом доступе.\n\n"
        "Наша цель - дать вам лучший контент без лишних переплат и ограничений.\n"
        "Ваша поддержка помогает нам развиваться и делать сервис ещё лучше.\n\n"
        "<b>2. Возникли проблемы при оплате</b> 💳\n\n"
        "Оплатили, но платёж не прошёл или возникла ошибка?\n"
        "Напишите нам в личные сообщения - мы быстро поможем разобраться. Поддержка работает 24/7.\n\n"
        "<b>3. Не нашли удобный способ оплаты</b> ⚙️\n\n"
        "Если у вас возникли сложности с оплатой (например, при использовании криптовалюты) или не нашли подходящий способ, напишите нам в личные сообщения.\n"
        "Мы постараемся подобрать для вас удобное решение. Поддержка доступна 24/7. 🟢\n\n"
        "<b>4. Примеры контента</b> 👀\n\n"
        "Зайдите в Подписки, далее выберите любой интересующий вас продукт и там выберите 'Превью контента'.\n\n"
        "<b>5. Будут ли добавляться новые модели и направления?</b> 😈\n\n"
        "Да, мы планируем расширять библиотеку контента на основе интересов нашей аудитории.\n\n"
        "Если вы хотите повлиять на будущие обновления, примите участие в опросе по ссылке ниже.\n\n\n"
        f"Если вы прочитали ответы на вопросы выше, но не нашли решение, напишите в поддержку: {SUPPORT_URL}\n\n\n\n"
        "Политика конфиденциальности: https://telegra.ph/Politika-konfidencialnosti-04-01-26\n"
        "Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19"
    ),
}

FAQ_TEXT = {
    "anxieest": {
        "en": (
            "<b>Anxieest</b> is known for the funny and corny jokes she posts on TikTok and Instagram.\n\n"
            "At one point, she created an OnlyFans “just for fun,” as she put it — and for a long time, that really seemed to be the case, since there was no content there at all. But then something changed.\n"
            "One day, I checked her OnlyFans and was surprised to see that she had started posting lifestyle content: selfies, everyday moments, and similar material that usually isn’t what people come to OF for. Then, unexpectedly, she posted 2 photos of her juicy ass and later uploaded a video featuring a butt plug and masturbation. I immediately bought this content. It cost me $30 for that single video.\n"
            "After some time, it seems she became concerned about her career, or had other reasons, and ended up deleting everything from her OnlyFans. Now the page is completely empty, and that content can’t be found anywhere.\n\n"
            "Here’s our offer for you! 🔥\n"
            "In our private channel : 2 photos of her ass and that butt plug + masturbation video 🔞\n"
            "💰<b>Price</b>: 10$\n"
            "🔗 After your purchase, private channel link will be sent to you.\n"
            "⏳<b>Duration</b> : Forever ✅"

        ),
        "ru": (
            "<b>Anxieest</b> известна благодаря своим смешным и пошлым шуткам, которые она выкладывает в тик-ток/инстаграм. \n\n"
            "Однажды она создала OnlyFans <b>'по приколу'</b> как она это объяснила и впринципе так оно и оказалось : постов там вообще никаких не было долгое время. <b>НО ТУТ СЛУЧИЛОСЬ ЧУДО!</b>\n\n"
            "Однажды я очень удивился когда зашёл к ней на Онлик : она начала постить туда какой-то лайф контент, лицо, и всякий подобный мусор который очевидно никому на Онлике не интересен. С пониманием этого Настюша сначала запостила 2 фотографии своей сладкой попки, а после вошла во вкус : Настя запостила видео с пробкой в попке и мастурбацией с дилдо. \n"
            "Я конечно же не долго думая, всё это дело купил. За видос Настюша попросила аж целые <b>30$</b>, от чего я конечно же знатно <s>охуел</s> был недоволен . \n\n"
            "Спустя какое-то время Настюша видимо испугалась, что может загубить свою карьеру, либо ещё по каким-то причинам удалила ВСЁ, что было на Онлике. Сейчас там пусто и этого контента нигде нет. Ну может у каких-нибудь американцев разве что. \n\n"
            "Поэтому у нас есть предложение для Вас! 🔥\n"
            "В приватном канале с Anxieest есть :\n"
            "2 фото её попки и видео мастурбации с анальной пробкой + дилдо 🔞\n"
            "💰<b>Стоимость</b>: 10$\n"
            "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
            "⏳<b>Длительность</b> : Навсегда ✅"
            
        ),
    },
    "coomeet": {
        "en": (
            "<b>Coomeet</b> is a roulette platform for <s>chatting</s> adult content, flirting, and everything around it. Like any platform, it has its pros and cons.\n"
            "<b>What’s the problem?</b>\n"
            "Getting good content directly is expensive, time-consuming, inconvenient, and often unpredictable: searching takes a lot of time, minutes disappear quickly, and the quality of the content doesn’t always justify the cost.\n\n"
            "<b>What does PinkLeak do?</b>\n"
            "We collect, filter, and organize the best content from the platform, including material that is difficult to find in the public domain.\n"
            "This gives you instant access to a large collection without wasting extra time or money.\n\n"
            "❗️ <b>Updates</b>\n"
            "Content is updated regularly. Private channel subscribers can also take part in polls and influence which model will appear in future updates.\n\n"
            "Here’s our offer for you! 🔥\n"
            "Inside the private channel you’ll get:\n"
            "500+ videos from Coomeet girls featuring a wide variety of content from different countries. A large part of the collection includes content that is not publicly available.\n"
            "💰<b>Price</b>: 6$ / 14$ / 49$\n"
            "🔗 After purchase, you’ll receive access to a private channel\n"
            "⏳<b>Duration</b> : 1 / 3 / 12 months ✅"
        ),
        "ru": (
            "<b>Coomeet</b> - рулетка для <s>общения</s> разврата/порно и всего остального. У площадки есть свои минусы и плюсы.\n"
            "<b>В чём проблема?</b>\n"
            "Получить хороший контент напрямую - дорого, долго, неудобно и часто непредсказуемо: поиск занимает много времени, минуты быстро расходуются, а качество и результат не всегда оправдывают ожидания.\n\n"
            "<b>Чем занимается PinkLeak?</b>\n"
            "Мы собираем, отбираем и структурируем лучший контент с площадки, включая материалы, которые сложно найти в открытом доступе.\n"
            "Это позволяет вам получить доступ сразу к большой подборке без лишних трат времени и денег.\n\n"
            "❗️ <b>Обновления</b>\n"
            "Контент обновляется на постоянной основе. Подписчики приватного канала могут участвовать в опросах и влиять на то, с какой моделью выйдет следующий контент.\n\n"
            "Поэтому у нас есть предложение для Вас! 🔥\n"
            "В приватном канале есть :\n"
            "500+ видео девушек Coomeet с разным контентом и из разных стран. Большая часть контента - эксклюзив, которого нет в открытом доступе.\n"
            "💰<b>Стоимость</b>: 6$ / 14$ / 49$\n"
            "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
            "⏳<b>Длительность</b> : 1 / 3 / 12 месяцев ✅"
        ),
    },
    "mandy_rose": {
        "en": (
            "<b>Mandy Rose</b> is an American wrestler best known for her work in WWE and NXT. She hardly needs any introduction.\n\n"
            "For a long time, wrestling was Mandy’s main focus. Later, she launched her Fantime page, where she began posting exclusive content.\n"
            "At first, the content was relatively soft and reserved. But over time, Mandy became much more open, eventually creating an OnlyFans and moving to a more explicit and professional style of content. Fantime was later removed, and she fully transitioned to OnlyFans.\n"
            "She now also does collaborations with Laisey Evans (WWE superstar) and other models.\n\n"
            "❗️ Mandy has also started posting content with her husband, and the material there is especially hot. 🔥\n\n"
            "That’s why we’ve put together a private collection for you 🔥:\n"
            "Inside the private channel you’ll get:\n"
            "• All of her OnlyFans content 🔞\n"
            "• Deleted content from Fantime 🔞\n"
            "💰<b>Price</b>: $5 / $12 / $39\n"
            "🔗 After purchase, you will be sent a link to the private channel.\n"
            "⏳<b>Duration</b>: 1 / 3 / 12 months ✅"
            
        ),
        "ru": (
            "<b>Mandy Rose</b> - американская рестлерша, более известная благодаря WWE а так же NXT. Думаю данную персону представлять не стоит.\n\n"
            "Mandy Rose долгое время выступала на ринге и это было её основной деятельностью. Далее Mandy создала площадку Fantime и начала выкладывать сочный и грязный контент.\n"
            "Сначала контент был 'аккуратным' и Mandy много чего не показывала. Но позже дама раскрепостилась и уже из Fantime создала OnlyFans и начала постить уже более профессиональный контент + светить своими огромными прелестями. Fantime в последствии был удалён и она полностью перешла на OnlyFans. \nСейчас делает коллабы с Laisey Evans(тоже подружка-рестлерша) и другими моделями.\n\n"
            "❗️ Так же Mandy начала постить контент со своим мужем. Контент там весьма горячий 🔥\n\n"
            "На OnlyFans доступ к её контенту стоит от 8$ в месяц. Для пользователей из СНГ оплата и пополнение баланса сейчас часто связаны с трудностями, поэтому у нас есть более удобное решение для Вас. 🔥\n"
            "В приватном канале есть :\n"
            "• Весь контент с её OnlyFans 🔞\n"
	        "• Удалённый контент с Fantime 🔞\n"
            "💰<b>Стоимость</b>: 5$ / 12$ / 39$\n"
            "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
            "⏳<b>Длительность</b> : 1 / 3 / 12 месяцев ✅"
        ),
    },
}

UI_TEXT = {
    "choose_language": {
        "en": "Please choose your language.",
        "ru": "Пожалуйста, выберите язык.",
    },
    "language_saved": {
        "en": "Language saved.",
        "ru": "Язык сохранён.",
    },
    "menu_greeting": {
        "en": "Hello. Choose what you want to open below.",
        "ru": "Привет. Выберите, что хотите открыть ниже.",
    },
    "products_welcome": {
        "en": "Welcome to PinkLeak ✨\n\nA private collection of exclusive content 😈\nChoose an option below to get started.",
        "ru": "Добро пожаловать в PinkLeak ✨\n\nКоллекция эксклюзивного контента ждёт тебя 😈\nДля ознакомления с нашим контентом, выберите вариант ниже из списка.",
    },
    "menu_ready": {
        "en": "Menu",
        "ru": "Меню",
    },
    "faq_welcome": {
        "en": "Choose which FAQ you want to open.",
        "ru": "Выберите, какой FAQ хотите открыть.",
    },
    "choose_payment_method": {
        "en": "Choose your payment method.",
        "ru": "Выберите способ оплаты.",
    },
    "back_to_products": {
        "en": "Back to products",
        "ru": "Назад к продуктам",
    },
    "back_to_menu": {
        "en": "Back to menu",
        "ru": "Назад в меню",
    },
    "i_paid": {
        "en": "I paid ✅",
        "ru": "Я оплатил ✅",
    },
    "start_payment": {
        "en": "Start payment ✅",
        "ru": "Начать оплату ✅",
    },
    "cancel_payment": {
        "en": "Cancel payment ❌",
        "ru": "Отменить оплату ❌",
    },
    "buy_access": {
        "en": "Buy access 🔒",
        "ru": "Купить доступ 🔒",
    },
    "content_preview": {
        "en": "Content Preview ✅",
        "ru": "Превью контента ✅",
    },
    "get_access": {
        "en": "Get Access 🔑",
        "ru": "Получить доступ 🔑",
    },
    "enter_hash": {
        "en": "Enter your transaction hash.",
        "ru": "Введите хеш вашей транзакции.",
    },
    "hash_used": {
        "en": "This hash has already been used.",
        "ru": "Этот хеш уже был использован.",
    },
    "hash_not_found": {
        "en": "Can't find this deposit.",
        "ru": "Не удалось найти этот депозит.",
    },
    "hash_pending": {
        "en": "Transaction is still in process. Please wait.",
        "ru": "Транзакция ещё обрабатывается. Пожалуйста, подождите.",
    },
    "hash_invalid": {
        "en": "Invalid transaction hash. Try again.",
        "ru": "Некорректный хеш транзакции. Попробуйте ещё раз.",
    },
    "currency_mismatch": {
        "en": "Currency mismatch. Expected {expected}, but received {actual}.",
        "ru": "Валюта не совпадает. Ожидалась {expected}, но получена {actual}.",
    },
    "payment_cancelled": {
        "en": "Payment cancelled.",
        "ru": "Оплата отменена.",
    },
    "no_subscription": {
        "en": "You don’t have any active subscriptions yet 😔",
        "ru": "У вас пока нет активных подписок 😔",
    },
    "my_subscriptions_intro": {
        "en": "You have active subscriptions ✅:",
        "ru": "У вас есть активные подписки ✅:",
    },
    "subscription_until": {
        "en": "🔹 {product}: active until {date}",
        "ru": "🔹 {product}: активно до {date}",
    },
    "subscription_lifetime": {
        "en": "🔹 {product}: lifetime access ♾️",
        "ru": "🔹 {product}: пожизненный доступ ♾️",
    },
    "manual_payment": {
        "en": (
            "<b>Payment method:</b> Via Telegram\n"
            "<b>Product:</b> {product}\n"
            "<b>Plan:</b> {plan}\n"
            "<b>Cost:</b> {price}$\n"
            "<b>Your ID:</b> {user_id}\n\n"
            "Contact me here to complete the payment manually:\n"
            f"{SUPPORT_URL}"
        ),
        "ru": (
            "<b>Способ оплаты:</b> Через Telegram\n"
            "<b>Продукт:</b> {product}\n"
            "<b>Тариф:</b> {plan}\n"
            "<b>Стоимость:</b> {price}$\n"
            "<b>Ваш ID:</b> {user_id}\n\n"
            "Напишите мне сюда, чтобы завершить оплату вручную:\n"
            f"{SUPPORT_URL}"
        ),
    },
    "donation_alerts": {
        "en": (
            "<b>💳 Payment method:</b> Donation Alerts\n"
            "<b>🔞 Product:</b> {product}\n"
            "<b>💎 Plan:</b> {plan}\n"
            "<b>💰 Cost:</b> {price}$\n"
            "<b>Your ID:</b> {user_id}\n\n"
            "1. Open the link below:\n"
            f"{DONATION_ALERTS_URL}\n\n"
            "2. Send the exact amount shown above.\n"
            "3. Put your Telegram ID into the message field.\n"
            "4. After payment, wait for transaction approval ✅\n\n"
            "If you have questions, contact support : https://t.me/PinkLeakSupport"
        ),
        "ru": (
            "<b>Способ оплаты:</b> Donation Alerts\n"
            "<b>Продукт:</b> {product}\n"
            "<b>Тариф:</b> {plan}\n"
            "<b>Стоимость:</b> {price}$\n"
            "<b>Ваш ID:</b> {user_id}\n\n"
            "1. Откройте ссылку ниже:\n"
            f"{DONATION_ALERTS_URL}\n\n"
            "2. Отправьте точную сумму, указанную выше.\n"
            "3. В поле сообщения укажите ваш Telegram ID.\n"
            "4. После оплаты дождитесь окончания транзакции ✅\n\n"
            "Если у Вас остались какие-то вопросы, напишите в поддержку : https://t.me/PinkLeakSupport"
        ),
    },
}

def format_usd_amount(amount: float | int) -> str:
    numeric = float(amount)
    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:.2f}".rstrip("0").rstrip(".")


def load_pricing_config() -> dict[str, float | int]:
    config = {
        "usd_to_rub_rate": USD_TO_RUB_RATE,
        "rub_rounding_step": RUB_ROUNDING_STEP,
    }
    try:
        file_config = json.loads(PRICING_CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return config

    rate = file_config.get("usd_to_rub_rate")
    rounding_step = file_config.get("rub_rounding_step")
    if isinstance(rate, (int, float)) and rate > 0:
        config["usd_to_rub_rate"] = rate
    if isinstance(rounding_step, (int, float)) and rounding_step > 0:
        config["rub_rounding_step"] = int(rounding_step)
    return config


def round_rub_amount(amount: float, rounding_step: int | None = None) -> int:
    if amount <= 0:
        return 0
    step = rounding_step or RUB_ROUNDING_STEP
    return int(((amount + step / 2) // step) * step)


def format_integer_amount(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


def price_text(language: str, price_usd: float | int) -> str:
    if language == "ru":
        pricing_config = load_pricing_config()
        rub_amount = round_rub_amount(
            float(price_usd) * float(pricing_config["usd_to_rub_rate"]),
            int(pricing_config["rub_rounding_step"]),
        )
        return f"{format_integer_amount(rub_amount)} ₽"
    return f"{format_usd_amount(price_usd)}$"


def prices_text(language: str, *prices_usd: float | int) -> str:
    return " / ".join(price_text(language, price_usd) for price_usd in prices_usd)


def usdt_amount_text(price_usd: float | int) -> str:
    return f"{format_usd_amount(price_usd)} USDT"


def tr(language: str, key: str) -> str:
    return UI_TEXT[key].get(language, UI_TEXT[key][DEFAULT_LANGUAGE])


def menu_text(language: str, key: str) -> str:
    return MENU_TEXT[key].get(language, MENU_TEXT[key][DEFAULT_LANGUAGE])


def product_name(product_code: str, language: str) -> str:
    product = PRODUCTS[product_code]
    return product["name"].get(language, product["name"][DEFAULT_LANGUAGE])


def plan_name(product_code: str, plan_code: str, language: str) -> str:
    if language == "ru" and product_code in {"coomeet", "mandy_rose"}:
        overrides = {
            "quarterly": "Премиум на 3 месяца (выгодно)💎",
            "monthly": "Премиум на 1 месяц",
            "yearly": "Премиум на 12 месяцев",
            "lifetime_request": "Пожизненный доступ 👑",
        }
        if plan_code in overrides:
            return overrides[plan_code]

    plan = PRODUCTS[product_code]["plans"][plan_code]
    return plan["title"].get(language, plan["title"][DEFAULT_LANGUAGE])


def payment_method_name(method_code: str, language: str) -> str:
    method = PAYMENT_METHOD_TEXT[method_code]
    return method.get(language, method[DEFAULT_LANGUAGE])
