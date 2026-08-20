import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Bot trigger names (all lowercase)
BOT_NAMES = ["idol", "asisten", "assistant", "bot", "babu"]

# Max conversation history messages per chat
MAX_HISTORY = 20

# AI Model on Groq
AI_MODEL = "llama-3.3-70b-versatile"

# Database file path
DB_PATH = os.getenv("DB_PATH", "data/idol.db")
