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
                        "⚠️ The price of this video on her OnlyFans was $30. After some time, Anxieest completely cleared her OnlyFans, and the content is no longer available there. For more detailed information, please read the FAQ."
                        ),
                    "ru": (
                        "В приватном канале с Anxieest есть :\n"
                        "• 2 фото её попки\n"
                        "• видео с анальной пробкой и трах дилдо 🔞\n"
                        "💰<b>Стоимость</b>: 10$\n"
                        "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
                        "⏳<b>Длительность</b> : Навсегда ✅\n\n"
                        "⚠️ Стоимость данного видео на её OnlyFans - было 30$. Спустя какое-то время Anxieest очистила OnlyFans полностью и контента там нет. Для более подробной информации прочтите FAQ."
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
                        "• 1000+ videos from Coomeet with a wide variety of content\n"
                        "• All content is exclusive — you won’t find it anywhere else\n\n"
                        "⚠️ <b>Important:</b>\n"
                        "Content is updated weekly. Private channel subscribers can take part in regular polls to decide which model will be featured next.\n\n\n"
                        "💰<b>Price</b>: 6$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 1 month ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 1000+ видео слитых девушек Coomeet с абсолютно разным контентом.\n"
                        "• Контент куплен мной поэтому найти его где-то ещё Вы не сможете.\n\n"
                        "⚠️ <b>Важно:</b>\n"
                        "Контент обновляется еженедельно. Для подписчиков приватного канала регулярно проводятся опросы, где вы можете выбрать, с какой моделью будет следующий контент.\n\n\n"
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
                        "• 1000+ videos from Coomeet with a wide variety of content\n"
                        "• All content is exclusive — you won’t find it anywhere else\n\n"
                        "⚠️ <b>Important:</b>\n"
                        "Content is updated weekly. Private channel subscribers can take part in regular polls to decide which model will be featured next.\n\n\n"
                        "💰<b>Price</b>: 14$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 3 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 1000+ видео слитых девушек Coomeet с абсолютно разным контентом.\n"
                        "• Контент куплен мной поэтому найти его где-то ещё Вы не сможете.\n\n"
                        "⚠️ <b>Важно:</b>\n"
                        "Контент обновляется еженедельно. Для подписчиков приватного канала регулярно проводятся опросы, где вы можете выбрать, с какой моделью будет следующий контент.\n\n\n"
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
                        "• 1000+ videos from Coomeet with a wide variety of content\n"
                        "• All content is exclusive — you won’t find it anywhere else\n\n"
                        "⚠️ <b>Important:</b>\n"
                        "Content is updated weekly. Private channel subscribers can take part in regular polls to decide which model will be featured next.\n\n\n"
                        "💰<b>Price</b>: 49$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 12 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• 1000+ видео слитых девушек Coomeet с абсолютно разным контентом.\n"
                        "• Контент куплен мной поэтому найти его где-то ещё Вы не сможете.\n\n"
                        "⚠️ <b>Важно:</b>\n"
                        "Контент обновляется еженедельно. Для подписчиков приватного канала регулярно проводятся опросы, где вы можете выбрать, с какой моделью будет следующий контент.\n\n\n"
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
                    "ru": "Пожизненный доступ доступен по индивидуальному запросу.\nДля получения подробной информации обратитесь в поддержку.",
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
                        "⚠️ <b>Important:</b>\n"
                        "Mandy does not have any other adult platform besides OF, but this channel combines her previous materials from different sources in one place.\n\n\n"
                        "💰<b>Price</b>: 5$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 1 month ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
	                    "• Удалённый контент с Fantime 🔞\n"
                        "⚠️ <b>Важно:</b>\n"
                        "У Mandy нет других платформ кроме OF, но в этом канале собраны её прошлые материалы из разных источников в одном месте.\n\n\n"
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
                        "⚠️ <b>Important:</b>\n"
                        "Mandy does not have any other adult platform besides OF, but this channel combines her previous materials from different sources in one place.\n\n\n"
                        "💰<b>Price</b>: 12$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 3 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
	                    "• Удалённый контент с Fantime 🔞\n"
                        "⚠️ <b>Важно:</b>\n"
                        "У Mandy нет других платформ кроме OF, но в этом канале собраны её прошлые материалы из разных источников в одном месте.\n\n\n"
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
                        "⚠️ <b>Important:</b>\n"
                        "Mandy does not have any other adult platform besides OF, but this channel combines her previous materials from different sources in one place.\n\n\n"
                        "💰<b>Price</b>: 39$\n"
                        "🔗 After purchase, you’ll receive access to a private channel\n"
                        "⏳<b>Duration</b> : 12 months ✅"
                    ),
                    "ru": (
                        "В приватном канале есть :\n"
                        "• Весь контент с её OnlyFans 🔞\n"
                        "• Удалённый контент с Fantime 🔞\n"
                        "⚠️ <b>Важно:</b>\n"
                        "У Mandy нет других платформ кроме OF, но в этом канале собраны её прошлые материалы из разных источников в одном месте.\n\n\n"
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
                    "ru": "Пожизненный доступ доступен по индивидуальному запросу.\nДля получения подробной информации обратитесь в поддержку.",
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
        "On official platforms (OnlyFans, Coomeet, etc.), content is often overpriced.\n"
        "Our goal is to give you the best content without unnecessary overpaying or limitations.\n"
        "Your support helps us grow and improve the service.\n\n"
        "<b>2. Payment issues</b> 💳\n\n"
        "Having trouble with your payment?\n\n"
        "Did you complete a payment but something went wrong?\n"
        "Send us a direct message — we’ll quickly help you sort it out. Our support is available 24/7.\n\n"
        "<b>3. No convenient payment method</b> ⚙️\n\n"
        "Can’t find a suitable payment method?\n\n"
        "If you’re experiencing difficulties with payment (for example, using cryptocurrency) or couldn’t find a convenient option, feel free to message us.\n"
        "We’ll do our best to find a solution that works for you. Support is available 24/7. 🟢\n\n"
        "<b>4. Content samples</b> 👀\n\n"
        "Go to Subscriptions and open any product you want. You’ll see a “Content Preview” button where you can preview the content before purchasing.\n\n"
        "<b>5. Will there be more content?</b> 📈\n\n"
        "Yes, we are continuously expanding our library and adding new models. Upcoming updates include content featuring Laisey Evans, Dana Brooke(WWE) and careful_i_bite(bongacams).\n"
        "We also welcome your suggestions and take user requests into account.\n\n\n"
        "<b>Need more help?</b> 🤝\n"
        f"If you read the all answers above and still need help, contact support: {SUPPORT_URL}\n\n\n\n"
        "Privacy policy: https://telegra.ph/Privacy-Policy-06-09-143\n"
        "User agreement: https://telegra.ph/User-Agreement-06-09-57"
    ),
    "ru": (
        "<b>1. Почему PinkLeak — это выгодно?</b>\n\n"
        "Мы собираем контент с разных платформ и от разных моделей, чтобы предоставить его вам по доступным и удобным ценам.\n\n"
        "На официальных площадках (OnlyFans, Coomeet и др.) стоимость контента часто завышена, а также могут возникать сложности с оплатой и пополнением баланса.\n\n"
        "Наша цель - дать вам лучший контент без лишних переплат и ограничений.\n"
        "Ваша поддержка помогает нам развиваться и делать сервис ещё лучше.\n\n"
        "<b>2. Возникли проблемы при оплате</b>\n\n"
        "Оплатили, но платёж не прошёл или возникла ошибка?\n"
        "Напишите нам в личные сообщения - мы быстро поможем разобраться. Поддержка работает 24/7.\n\n"
        "<b>3. Не нашли удобный способ оплаты</b>\n\n"
        "Если у вас возникли сложности с оплатой (например, при использовании криптовалюты) или не нашли подходящий способ, напишите нам в личные сообщения.\n"
        "Мы постараемся подобрать для вас удобное решение. Поддержка доступна 24/7.\n\n"
        "<b>4. Примеры контента</b>\n\n"
        "Зайдите в Подписки, далее выберите любой интересующий вас продукт и там выберите 'Превью контента'.\n\n"
        "<b>5. Будут ли пополнения контента?</b>\n\n"
        "Да, мы постоянно работаем над расширением контента и добавлением новых моделей.\n\n"
        "Уже запланированы обновления с участием Laisey Evans, Dana Brooke (WWE), а так же careful_i_bite(bongacams).\n"
        "Также мы открыты к вашим предложениям и учитываем пожелания пользователей.\n\n"
        f"Если вы прочитали ответы на вопросы выше, но не нашли решение, напишите в поддержку: {SUPPORT_URL}\n\n\n\n"
        "Политика конфиденциальности: https://telegra.ph/Politika-konfidencialnosti-04-01-26\n"
        "Пользовательское соглашение: https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19"
    ),
}

FAQ_TEXT = {
    "anxieest": {
        "en": (
            "<b>Anxieest</b> is known for her funny and corny jokes that she posts on TikTok and Instagram.\n\n"
            "At one point, she created an OnlyFans “just for fun,” as she explained it herself — and that’s pretty much how it turned out: for a long time, there was no content posted there at all. <b>BUT!</b>\n"
            "One day I was surprised when I checked her OF — she started posting some kind of lifestyle content there: selfies, everyday moments, lifestyle and similar stuff that obviously doesn’t really attract people on OF.\n"
            "With understanding of the whole situation, she posted 2 photos of her juicy ass and then she made a video with ass plug and masturbation. I immediately purchased this content. It costs me 30$ for 1 video.\n\n"
            "After some time, it seems like she got worried about her career or had other reasons, and ended up deleting EVERYTHING from her OnlyFans. Now it’s completely empty, and that content can’t be found anywhere.\n\n"
            "So, I have an offer for you! 🔥\n"
            "In my private channel : 2 photos of her ass + that 1 dirty video 🔞\n"
            "💰<b>Price</b>: 10$\n"
            "🔗 After your purchase, private channel link will be sent to you.\n"
            "⏳<b>Duration</b> : Forever ✅"

        ),
        "ru": (
            "<b>Anxieest</b> известна благодаря своим смешным и пошлым шуткам, которые она выкладывает в тик-ток/инстаграм. \n\n"
            "Однажды она создала OnlyFans <b>'по приколу'</b> как она это объяснила и впринципе так оно и оказалось : постов там вообще никаких не было долгое время. <b>НО ТУТ СЛУЧИЛОСЬ ЧУДО!</b>\n\n"
            "Однажды я охуел когда зашёл к ней в один из прекрасных солнечных дней : она начала постить туда какой-то лайф контент, лицо, и всякую такую хуйню которая очевидно никому на Онлике не сдалась. С пониманием этого Настюша сначала запостила 2 фотографии своей сладкой попки, а после планета вообще охуела : Настя запостила видео с пробкой в попке и мастурбацией ещё и с дилдо. \n"
            "Я конечно же не долго думая, всё это дело купил. За видос Настюша попросила аж целые <b>30$</b>, от чего я конечно же знатно прихуел. \n\n"
            "Спустя какое-то время Настюша видимо испугалась что может загубить свою карьеру либо ещё по каким-то причинам удалила ВСЁ, что было на Онлике. Сейчас там пусто и этого контента нигде нет. Ну может у каких-нибудь американцев разве что. \n\n"
            "Поэтому у меня есть предложение для Вас! 🔥\n"
            "В приватном канале с Anxieest есть :\n"
            "2 фото её попки + то самое 1 видео 🔞\n"
            "💰<b>Стоимость</b>: 10$\n"
            "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
            "⏳<b>Длительность</b> : Навсегда ✅"
            
        ),
    },
    "coomeet": {
        "en": (
            "Coomeet is a dating platform with its own pros and cons.\n"
            "The main downside? You need a solid budget.\n"
            "To get any real content, you usually have to:\n"
            "1. Start a call (which already requires high balance)\n"
            "2. And right after the call, send a gift (some really hot girls even asking for 50 minutes and more)\n\n"
            "Many girls won’t even do anything until you’ve spent a decent amount — some expect long calls and expensive gifts before showing anything at all. If you know the platform, you know what I mean.\n"
            "But there’s also a big advantage: There are a lot of different girls, with completely different styles of content and pricing.\n"
            "I tried to find content online — but it’s simply not there.\n"
            "A lot of Coomeet content is unavailable on sites like camwhores and others where videos are only visible to admins or the person who uploaded them.\n"
            "So I decided to collect my own exclusive content.\n"
            "I’ve gathered a large collection of interesting material — all recorded and compiled personally. The collection will continue to grow: more videos and call recordings will be added soon.\n"
            "I also made sure to select the best content possible, because Coomeet is full of total nonsense, grannies, and all sorts of other weird stuff.\n\n\n"
            "So here’s my offer for you! 🔥\n"
            "Inside the private channel you’ll get:\n"
            "• 1000+ videos from Coomeet with a wide variety of content\n"
            "• All content is exclusive — you won’t find it anywhere else\n"
            "💰<b>Price</b>: 6$ / 14$ / 49$\n"
            "🔗 After purchase, you’ll receive access to a private channel\n"
            "⏳<b>Duration</b> : 1 / 3 / 12 months ✅"
        ),
        "ru": (
            "<b>Coomeet</b> - сайт для знакомств. У площадки есть много минусов и плюсов. Минусы - быть богатым. Для того, чтобы получить хоть какой-то контент, ты должен (так говорят куметовские(охуевшие) девочки): \n"
            "1. Созвониться (иметь норм баланс) \n2. После созвона сразу же сделать подарок (некоторые вообще просят по 50 минут и больше, кто знает площадку тот поймёт о чем я) и только потом они разденутся или хотя бы встанут со стула. Плюсы - много девушек с абсолютно разным контентом и разными ценниками.\n\n"
            "Пытался искать какой-нибудь контент в гугле - но его просто нет. Куча контента с Coomeet просто недоступно на сайтах типа camwhores и остальных, где видео доступны только админам либо пользователю, кто сам и добавил видео. \n\n"
            "Я собрал для Вас много <b>СВОЕГО</b> интересного эксклюзивного контента. Весь контент будет пополняться, скоро будет больше видео + записей звонков. \n\n"
            "Девушек старался выбирать самых нормальных, потому что в Coomeet очень много пиздеца, бабушек и всяких других приколов.\n\n\n"
            "Поэтому у меня есть предложение для Вас! 🔥\n"
            "В приватном канале есть :\n"
            "1000+ видео слитых девушек Coomeet с абсолютно разным контентом. Контент куплен мной поэтому найти его где-то ещё Вы не сможете.\n"
            "💰<b>Стоимость</b>: 6$ / 14$ / 49$\n"
            "🔗 После покупки Вам будет отправлена ссылка в приватный канал.\n"
            "⏳<b>Длительность</b> : 1 / 3 / 12 месяцев ✅"
        ),
    },
    "mandy_rose": {
        "en": (
            "<b>Mandy Rose</b> is an American professional wrestler best known for her work in WWE and NXT. I don’t think she needs any introduction, but I’ll give a brief overview.\n\n"
            "Mandy Rose spent a long time performing in the ring, and that was her main job. Then Mandy created a Fantime account and started posting juicy and dirty content. \n\n"
            "At first, the content was “relatively mild” and Mandy didn’t show much + the angles and content were super shitty compared to regular models on OnlyFans. But later, she loosened up and created an OnlyFans account from Fantime, starting to post more professional content and showing off her amazing forms 😏.\n"
            "Fantime was eventually deleted, and she switched completely to OnlyFans. Now she’s doing collabs with Laisey Evans (also a wrestler friend) and other models.\n\n"
            "! ! ! Mandy has also started posting content with her husband. The content there is pretty good.\n\n"
            "Her monthly subscription cost: $8. 3 months: $20.\n"
            "I have a proposal for you! 🔥"
            "In the private channel :\n"
            "• All content from her OnlyFans 🔞\n"
	        "• Deleted content from Fantime 🔞\n"
            "💰<b>Price</b>: $5 / $12 / $39\n"
            "🔗 After purchase, you will be sent a link to the private channel.\n"
            "⏳<b>Duration</b>: 1 / 3 / 12 months ✅"
            
        ),
        "ru": (
            "<b>Mandy Rose</b> - американская рестлерша, более известная благодаря WWE а так же NXT. Думаю данную персону представлять не стоит, но минимально расскажу.\n\n"
            "Mandy Rose долгое время выступала на ринге и это было её основной деятельностью. Далее Mandy захотела поискать дополнительный доход, потому что Урус нужно было чем-то заправлять и она создала площадку Fantime и начала выкладывать сочный и грязный контент. Большинство людей охуело, потому что такого ожидать никто не мог. Ранее WWE очень серьёзно относились к подобным вещам и запрещали рестлершам иметь OnlyFans или подобные площадки. \n"
            "Сначала контент был 'аккуратным' и Mandy много чего не показывала + ракурсы и контент был супер хуёвым если сравнивать с нормальными моделями с Онлика. Но позже дама раскрепостилась и уже из Fantime создала OnlyFans и начала постить уже более профессиональный контент + светить своими огромными прелестями. Fantime в последствии был удалён и она полностью перешла на Онлик. Сейчас делает коллабы с Laisey Evans(тоже подружка-рестлерша) и другими моделями потому что запросики уже стали серьёзные и от второго Уруса отказываться не хочется.\n\n"
            "! ! ! Так же Mandy начала постить контент со своим огромным мужиком (мужем). Контент там весьма неплохой.\n\n"
            "Стоимость её подписки в месяц : 8$. 3 месяца : 20$.\n"
            "+ В СНГ сейчас депозит на OF стал проблемным, поэтому у меня есть предложение для Вас! 🔥"
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
        "en": "Welcome to PinkLeak ✨\n\nA private collection of exclusive content, carefully selected for you 😈\nTo explore the content, please choose an option below or visit the FAQ section.",
        "ru": "Добро пожаловать в PinkLeak ✨\n\nКоллекция эксклюзивного контента ждёт тебя 😈\nДля ознакомления с нашим контентом, выберите вариант ниже из списка, либо перейдите в FAQ.",
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
        return f"{format_integer_amount(rub_amount)} RUB"
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
    plan = PRODUCTS[product_code]["plans"][plan_code]
    return plan["title"].get(language, plan["title"][DEFAULT_LANGUAGE])


def payment_method_name(method_code: str, language: str) -> str:
    method = PAYMENT_METHOD_TEXT[method_code]
    return method.get(language, method[DEFAULT_LANGUAGE])
