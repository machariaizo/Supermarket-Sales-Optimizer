
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


# ============================================================
# 4. STAGE 1 AI — R-T-C-C-O
# ============================================================

def stage_1(user_input):
    """Analyze user input and generate structured JSON."""
    
    prompt = f"""
ROLE: You are an AI Supermarket Inventory Assistant.

TASK: Convert the user's supermarket question into structured JSON.

CONTEXT: The supermarket knowledge base contains product names, categories, prices, stock, expiry days, storage, and recommended actions.

USER QUESTION: {user_input}

CONSTRAINTS:
1. Return ONLY valid JSON.
2. Do not use markdown or code fences.
3. If unrelated to supermarket, set validity to "Irrelevant_Input".
4. For expiry questions use "expiry_check".
5. For stock questions use "stock_check".
6. For discount questions use "discount_recommendation".
7. For promotion questions use "promotion".
8. If no expiry period specified, use 7 days.
9. High urgency = 1-2 days, Medium = 3-7 days, Low = >7 days.

OUTPUT JSON:
{{
    "validity": "Relevant_Input",
    "intent": "expiry_check",
    "product": null,
    "category": null,
    "urgency": "High",
    "max_expiry_days": 7,
    "needs_discount": true,
    "timestamp": "{datetime.now().isoformat()}"
}}
"""
    
    raw_response = safe_generate_content(prompt)
    raw_response = raw_response.replace("json", "").replace("", "").strip()
    
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        raise ValueError("❌ Stage 1 returned invalid JSON.")

# ============================================================
# 5. RAG RETRIEVAL
# ============================================================

def retrieve_inventory(analysis, db_path=DB_PATH):
    """Retrieve products from knowledge base based on analysis."""
    
    max_expiry_days = analysis.get("max_expiry_days", 7)
    product = analysis.get("product")
    category = analysis.get("category")
    intent = analysis.get("intent")
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        if product:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE product LIKE ? ORDER BY expiry_days ASC",
                (f"%{product}%",)
            ).fetchall()
        elif category:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE category LIKE ? ORDER BY expiry_days ASC",
                (f"%{category}%",)
            ).fetchall()
        elif intent == "expiry_check":
            rows = conn.execute(
                "SELECT * FROM inventory WHERE expiry_days <= ? ORDER BY expiry_days ASC",
                (max_expiry_days,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM inventory ORDER BY expiry_days ASC").fetchall()
        
        return [dict(row) for row in rows]
# ============================================================
# 6. STAGE 2 AI — ACTION PLAN
# ============================================================

def stage_2(analysis, retrieved_products):
    """Generate action plan from analysis and retrieved products."""
    
    prompt = f"""
ROLE: You are an AI Supermarket Merchandising and Pricing Specialist.

TASK: Create a practical action plan to reduce losses from products approaching expiry.

CONTEXT:
STAGE 1 ANALYSIS: {json.dumps(analysis, indent=2)}
RETRIEVED PRODUCTS: {json.dumps(retrieved_products, indent=2)}

CONSTRAINTS:
1. Recommend ONLY products in the retrieved list.
2. Never invent products or prices.
3. 1-2 days = HIGH urgency (max 40% discount)
4. 3-7 days = MEDIUM urgency (max 20% discount)
5. >7 days = LOW urgency (max 10% discount)
6. Show exact discount math: Original × discount% = discount amount
7. Keep response under 150 words.
8. Use bullet points.
9. If no products match, say so.

OUTPUT FORMAT:
1. Diagnosis
2. Placement Strategy
3. Pricing & Bundles
"""
    
    return safe_generate_content(prompt)
# ============================================================
# 6. STAGE 2 AI — ACTION PLAN
# ============================================================

def stage_2(analysis, retrieved_products):
    """Generate action plan from analysis and retrieved products."""
    
    prompt = f"""
ROLE: You are an AI Supermarket Merchandising and Pricing Specialist.

TASK: Create a practical action plan to reduce losses from products approaching expiry.

CONTEXT:
STAGE 1 ANALYSIS: {json.dumps(analysis, indent=2)}
RETRIEVED PRODUCTS: {json.dumps(retrieved_products, indent=2)}

CONSTRAINTS:
1. Recommend ONLY products in the retrieved list.
2. Never invent products or prices.
3. 1-2 days = HIGH urgency (max 40% discount)
4. 3-7 days = MEDIUM urgency (max 20% discount)
5. >7 days = LOW urgency (max 10% discount)
6. Show exact discount math: Original × discount% = discount amount
7. Keep response under 150 words.
8. Use bullet points.
9. If no products match, say so.

OUTPUT FORMAT:
1. Diagnosis
2. Placement Strategy
3. Pricing & Bundles
"""
    
    return safe_generate_content(prompt)


# ============================================================
# 7. SAVE ACTION PLAN
# ============================================================

def save_action_plan(plan_text, filename=OUTPUT_FILE):
    """Save the action plan to a file."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write("=" * 70 + "\n")
        file.write("     🛒 SUPERMARKET ACTION PLAN\n")
        file.write(f"     Generated: {timestamp}\n")
        file.write("=" * 70 + "\n\n")
        file.write(plan_text)
        file.write("\n\n" + "=" * 70 + "\n")
    
    print(f"\n💾 Saved to: {filename}")
# ============================================================
# 8. CHAT FUNCTION
# ============================================================

def chat():
    """Interactive chatbot loop."""
    
    print("\n" + "=" * 60)
    print(" HELLO, WELCOME TO 🛒SUPERMARKET SALES OPTIMIZER")
    print("=" * 60)
    print("\n💡 Ask about stock, expiry, discounts, or promotions.")
    print("💡 Type 'view' to see inventory.")
    print("💡 Type 'add' to add a product.")
    print("💡 Type 'exit' to quit.\n")
    
    create_knowledge_base()
    
    while True:
        user_input = input("\n🧑 You: ").strip().lower()
        
        if not user_input:
            continue
        
        if user_input in ("exit", "quit"):
            print("👋 Goodbye! thank you for your time")
            break
        
        if user_input == "view":
            view_inventory()
            continue
        
        if user_input == "add":
            add_product()
            continue
        try:
            print("🤔 [Stage 1] Analyzing...")
            analysis = stage_1(user_input)
            
            # Guardrail
            if analysis.get("validity") == "Irrelevant_Input":
                print("👋 Please ask about supermarket stock, expiry, pricing, or promotions.")
                continue
            
            # RAG
            print("🔍 [RAG] Searching knowledge base...")
            retrieved = retrieve_inventory(analysis)
            print(f"✅ Found {len(retrieved)} products.")
            
            # Stage 2
            print("📝 [Stage 2] Creating action plan...")
            plan = stage_2(analysis, retrieved)
            
            # Display
            print("\n" + "=" * 60)
            print("                 ACTION PLAN")
            print("=" * 60)
            print(plan)
            print("=" * 60)
            
            # Save
            save_action_plan(plan)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")


# ============================================================
# 9. MAIN
# ============================================================

if _name_ == "_main_":
    chat()