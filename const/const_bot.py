#const/const_bot.py
PROFILE = '📝 Моя подписка'
HELP = '📞 Поддержка'
INSTRUCTIONS = '❓Инструкции'
GET_VLESS = '🔑 Получить ключик'
REFERRALS = '🎁 Реферальная программа'
SUBSCRIPTIONS = '🛒 Купить ключ'
REFERRAL_INFO = "📊 Баланс"
REFERRAL_LINK = '🔗 Реферальная ссылка'
REFERRAL_RULES = '❓ Как это работает?'
MAIN_MENU = "🏠 В главное меню"
BACK = '➡️ Назад'

MEOW_COINS_REFERRER_BONUS = 20
MEOW_COINS_FIRST_USE_REF_CODE = 20

ANDROID = f'Android'
INSTRUCTIONS_ANDROID = [ANDROID, 'https://telegra.ph/Nastrojka-Android-klienta-11-03']
IOS = f'IOS'
INSTRUCTIONS_IOS = [IOS, 'https://telegra.ph/Nastrojka-IOS-klienta-11-03']
MACOS = f'MacOS'
INSTRUCTIONS_MACOS = [MACOS, 'https://telegra.ph/Nastrojka-MacOS-klienta-11-03']
WINDOWS = f'Windows'
INSTRUCTIONS_WINDOWS = [WINDOWS, 'https://telegra.ph/Nastrojka-Windows-klienta-11-03']
NEKOBOX = f'Windows NekoBox'
INSTRUCTIONS_NEKOBOX = [NEKOBOX, 'https://telegra.ph/Nastrojka-NekoBox-Windows-01-27']

CURRENCY = 'RUB'
DAY_3_TIMESTAMP = 'day3'
TRIAL = '🐾🎈 3 Дня (пробная)'
MONTH_1_TIMESTAMP = 'month1'
MONTH1 = {'label' : '🐾 1 Месяц - 149 РУБ', 'amount' : 149*100,
          'description': 'Подписка на 1 месяц.',
          'payload' : MONTH_1_TIMESTAMP}
MONTH_3_TIMESTAMP = 'month3'
MONTH3 = {'label' : '🛡️ 3 Месяца - 390 РУБ', 'amount' : 390*100,
          'description': 'Подписка на 3 месяца.',
          'payload' : MONTH_3_TIMESTAMP}
MONTH_6_TIMESTAMP = 'month6'
MONTH6 = {'label' : '💻 6 Месяцев - 749 РУБ', 'amount' : 749*100,
          'description': 'Подписка на 6 месяцев.',
          'payload' : MONTH_6_TIMESTAMP}
YEAR_1_TIMESTAMP = 'year1'
YEAR1 = {'label' : '🎉 1 Год - 1290 РУБ', 'amount' : 1290*100,
         'description': 'Подписка на 1 год',
         'payload' : YEAR_1_TIMESTAMP}

EXPIRED = 0
LESS_THAN_HOUR = 1

BOT_NAME = 'test_meownow_bot'
PHOTO_PATH = 'bot/handlers/'
HANDLERS_JSON_PATH = 'bot/handlers/'
API_JSON_PATH = 'api/'
LOGGER_PRESET = '\n\n{username} -'
PAYMENT_STATE = {}
MINMUM_BONUS_PAYMENT = 60

PHOTO_subscriptions = 'AgACAgIAAxkDAAMaZ1tayr_pmYVe0LpBR_w5ei3j1akAAlfnMRuHddhKBcLY8CEuKCMBAAMCAAN3AAM2BA'
PHOTO_instructions = 'AgACAgIAAxkDAAMGZ1tTx6boCj77bYHoUecTdnDbntgAAhvnMRuHddhK83bQ2M5HKAIBAAMCAAN3AAM2BA'
PHOTO_menu = 'AgACAgIAAxkDAAMDZ1tSRTRxd_M7iMJyHoqC3AGI0woAAhjnMRuHddhKWR22W4fCakUBAAMCAAN3AAM2BA'
PHOTO_my_subscription = 'AgACAgIAAxkDAAICZGdpz84TD8nPHONHH9LEnr5PIsdKAALf6DEbDPlQS2pIfwKzLfC9AQADAgADdwADNgQ'
PHOTO_help = 'AgACAgIAAxkDAAMzZ11IQNAZRj_KTnMXA-Qm6a3RyzkAAj3kMRsyp-lKHAbB3mVdugcBAAMCAAN3AAM2BA'
PHOTO_referral_program = 'AgACAgIAAxkDAAICZmdpz9CAFiafVErb_R2UQPK3NfMfAALg6DEbDPlQS2234l0GLyQQAQADAgADdwADNgQ'