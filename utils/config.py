import os
import json
from dotenv import load_dotenv # type: ignore

load_dotenv()

API_USERNAME = os.getenv('API_USERNAME')
API_PASSWORD = os.getenv('API_PASSWORD')
API_IP = os.getenv('API_IP')
API_PORT = os.getenv('API_PORT')
API_PATH = os.getenv('API_PATH')
API_USERNAME_SSH = os.getenv('API_USERNAME_SSH')
API_PASSWORD_SSH = os.getenv('API_PASSWORD_SSH')
API_PRIVATE_KEY_SSH = os.getenv('API_PRIVATE_KEY_SSH')
API_PORT_SSH = int(os.getenv('API_PORT_SSH'))
API_INBOUND_ID = int(os.getenv('API_INBOUND_ID'))

BOT_TG_ID = os.getenv('BOT_TG_ID')
BOT_API = os.getenv('BOT_API')
BOT_TEST_PROVIDER_TOKEN = os.getenv('BOT_TEST_PROVIDER_TOKEN')
BOT_LIVE_PROVIDER_TOKEN = os.getenv('BOT_LIVE_PROVIDER_TOKEN')
BOT_ADMIN_IDS = json.loads(os.getenv('BOT_ADMIN_IDS'))
PHOTO_subscriptions = os.getenv('PHOTO_subscriptions')
PHOTO_instructions = os.getenv('PHOTO_instructions')
PHOTO_menu = os.getenv('PHOTO_menu')
PHOTO_my_subscription = os.getenv('PHOTO_my_subscription')
PHOTO_help = os.getenv('PHOTO_help')
PHOTO_referral_program = os.getenv('PHOTO_referral_program')

DB_PORT = int(os.getenv('DB_PORT'))
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')