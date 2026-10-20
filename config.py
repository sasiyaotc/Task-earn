import os
BOT_TOKEN = os.getenv("8893273268:AAEMjiQa6_De7az_EUeGYFu3jsyjH9ttgGs")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8886499198")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@Zess_kyc")
USDT_BEP20_ADDRESS = "0x52824938de138886fdf6f7a80262e5c0a173d92c"
CHANNEL_1 = os.getenv("CHANNEL_1", "@mini_earing_bot")
CHANNEL_2 = os.getenv("CHANNEL_2", "@earn_mini_pay")
CHANNEL_1_LINK = os.getenv("CHANNEL_1_LINK", "https://t.me/mini_earing_bot")
CHANNEL_2_LINK = os.getenv("CHANNEL_2_LINK", "https://t.me/earn_mini_pay")
WEB_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
if WEB_URL and not WEB_URL.startswith("http"):
    WEB_URL = f"https://{WEB_URL}"
ADSBITVEX_APP_ID = "000530"
AD_REWARD_USER = 0.005
AD_PROFIT_OWNER = 0.0034
ADS_PER_DAY = 30
TASK_JOIN_USER = 0.003
TASK_JOIN_OWNER = 0.007
REF_REWARD = 0.02
MIN_WITHDRAW = 1.0
MIN_REFS = 5
TASK_PRICE_2000 = 4
TASK_PRICE_UNLIMITED = 6
