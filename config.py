import os
from dotenv import load_dotenv

load_dotenv()

URL = "https://pewneauto.pl"

TOKEN = os.getenv("TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")