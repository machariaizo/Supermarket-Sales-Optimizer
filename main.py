
import os
import json
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env file")

client = genai.Client(api_key=API_KEY)

MODEL_POOL = [
    "gemini-3.6-flash",
    "gemini-1.5-flash"
]

DB_PATH = "inventory.db"
OUTPUT_FILE = "supermarket_action_plan.txt"


