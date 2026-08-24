
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


# ============================================================
# 2. GEMINI API FUNCTION WITH RETRY
# ============================================================

def safe_generate_content(prompt, delay=1, max_retries=3):
    """Generate content with model fallback and retry logic."""
    
    for attempt in range(max_retries):
        for model in MODEL_POOL:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
            except Exception as error:
                print(f"⚠️ {model} error (attempt {attempt+1}): {error}")
                time.sleep(delay)
    
    raise Exception("❌ All models failed after multiple retries.")


# ============================================================
# 3. DATABASE FUNCTIONS
# ============================================================

def create_knowledge_base(db_path=DB_PATH):
    """Create and populate the inventory knowledge base."""
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                expiry_days INTEGER NOT NULL,
                storage TEXT NOT NULL,
                action TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if data exists
        count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
        
        if count == 0:
            products = [
                (1, "Fresh Milk 1L", "Dairy", 2.50, 45, 2, "Refrigerated", "Apply discount and move to promotional section"),
                (2, "Ribeye Steak 500g", "Meat", 15.00, 10, 1, "Refrigerated", "Urgent discount and priority sale"),
                (3, "White Bread 500g", "Bakery", 1.80, 30, 3, "Room temperature", "Apply medium discount"),
                (4, "Greek Yogurt 500g", "Dairy", 4.50, 20, 5, "Refrigerated", "Monitor and prepare promotion"),
                (5, "Chicken Breast 1kg", "Meat", 8.00, 15, 7, "Refrigerated", "Monitor expiry and consider promotion"),
                (6, "Orange Juice 1L", "Beverages", 3.50, 25, 10, "Refrigerated", "Normal monitoring"),
                (7, "Cheddar Cheese 500g", "Dairy", 6.50, 12, 14, "Refrigerated", "Normal monitoring"),
                (8, "Eggs 12 Pack", "Dairy", 3.20, 50, 12, "Cool storage", "Normal monitoring"),
                (9, "Beef Sausages 500g", "Meat", 5.50, 18, 4, "Refrigerated", "Prepare medium discount"),
                (10, "Fresh Yoghurt 250ml", "Dairy", 1.50, 35, 2, "Refrigerated", "Urgent promotion"),
                (11, "Fresh Tomatoes 1kg", "Produce", 2.00, 40, 3, "Cool storage", "Promote quickly"),
                (12, "Bananas 1kg", "Produce", 1.70, 35, 2, "Room temperature", "Apply discount and promote"),
                (13, "Fresh Fish 500g", "Seafood", 10.00, 8, 1, "Refrigerated", "Urgent discount and priority sale"),
                (14, "Potatoes 2kg", "Produce", 3.00, 60, 20, "Cool dry place", "Normal monitoring"),
                (15, "Chocolate Bar 100g", "Snacks", 1.20, 80, 30, "Room temperature", "Normal monitoring"),
                (16, "Cooking Cream 250ml", "Dairy", 2.80, 16, 6, "Refrigerated", "Prepare promotion"),
                (17, "Minced Beef 500g", "Meat", 6.50, 12, 2, "Refrigerated", "Urgent discount"),
                (18, "Apple Juice 1L", "Beverages", 3.00, 22, 18, "Room temperature", "Normal monitoring"),
                (19, "Strawberries 250g", "Produce", 4.00, 14, 3, "Refrigerated", "Promote quickly"),
                (20, "Ice Cream 1L", "Frozen", 5.50, 25, 25, "Frozen", "Normal monitoring")
            ]
            
            conn.executemany("""
                INSERT INTO inventory (id, product, category, price, stock, expiry_days, storage, action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, products)
            conn.commit()


def view_inventory(db_path=DB_PATH):
    """Display all inventory items."""
    
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("""
            SELECT product, category, price, stock, expiry_days, storage, action
            FROM inventory
            ORDER BY expiry_days ASC
        """).fetchall()
    
    print("\n" + "=" * 80)
    print(f"{'PRODUCT':<25} {'CATEGORY':<12} {'PRICE':<8} {'STOCK':<8} {'EXPIRY':<8} {'STORAGE':<15} {'ACTION'}")
    print("-" * 80)
    
    for row in rows:
        print(f"{row[0]:<25} {row[1]:<12} ${row[2]:<7.2f} {row[3]:<8} {row[4]:<8} {row[5]:<15} {row[6]}")
    
    print("=" * 80)


def add_product(db_path=DB_PATH):
    """Add a new product to inventory."""
    
    print("\n📦 ADD NEW PRODUCT")
    print("-" * 40)
    
    product = input("Product name: ").strip()
    category = input("Category: ").strip()
    price = float(input("Price: ").strip())
    stock = int(input("Stock quantity: ").strip())
    expiry_days = int(input("Expiry days: ").strip())
    storage = input("Storage condition: ").strip()
    action = input("Recommended action: ").strip()
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO inventory (product, category, price, stock, expiry_days, storage, action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product, category, price, stock, expiry_days, storage, action))
        conn.commit()
    
    print(f"✅ '{product}' added successfully!")


