import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

CARD_NUMBER = os.getenv("CARD_NUMBER")

PANEL_URL = os.getenv("PANEL_URL")
PANEL_USERNAME = os.getenv("PANEL_USERNAME")
PANEL_PASSWORD = os.getenv("PANEL_PASSWORD")

DATABASE = os.getenv("DATABASE", "zeus.db")
