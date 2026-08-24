# 🛒 AI Supermarket Sales Optimizer

### Enhanced Version | End of Module Project — AI-Class-S11

An AI-powered supermarket inventory and sales optimization assistant designed to help supermarkets make data-driven decisions around stock, expiry, pricing, and promotions.

## 🔄 AI Pipeline

```text
User
  ↓
Stage 1 AI
  ↓
Structured JSON
  ↓
SQLite Knowledge Base
  ↓
RAG Retrieval
  ↓
Stage 2 AI
  ↓
Action Plan
```

## ✨ Key Features

* 🤖 Natural-language supermarket queries using Google Gemini
* 🗄️ SQLite inventory knowledge base
* 🔎 Retrieval-Augmented Generation (RAG) workflow
* 📦 Stock and expiry analysis
* 💰 Discount recommendations based on expiry urgency
* 📣 Promotion and product-placement recommendations
* 🧠 Two-stage AI processing
* 📄 Automatic action-plan generation and saving
* ➕ Ability to add new products to the inventory

## 🧠 How It Works

The system converts a supermarket manager's natural-language question into structured information, retrieves relevant inventory records from SQLite, and then sends the grounded information to a second AI stage to generate a practical action plan.

### Stage 1 — AI Analysis

Gemini identifies the user's intent and converts the question into structured JSON, including information such as product, category, urgency, expiry range, and discount requirements.

### Knowledge Base — SQLite

The system stores product information including:

* Product name
* Category
* Price
* Stock quantity
* Expiry period
* Storage condition
* Recommended action

### RAG Retrieval

The structured Stage 1 result is used to retrieve relevant products from the inventory knowledge base. This grounds the second AI stage in actual database information instead of relying only on general AI knowledge.

### Stage 2 — Action Planning

The retrieved products and Stage 1 analysis are provided to Gemini, which generates a concise action plan for merchandising, pricing, promotion, and expiry management.

## 💰 Discount Logic

The current prototype uses the following urgency rules:

| Expiry Period    | Urgency   | Maximum Discount |
| ---------------- | --------- | ---------------: |
| 1–2 days         | 🔴 High   |              40% |
| 3–7 days         | 🟠 Medium |              20% |
| More than 7 days | 🟢 Low    |              10% |

The AI is instructed to show the discount calculation and to recommend only products retrieved from the knowledge base.

## 🛠️ Technologies

* Python
* Google Gemini API
* SQLite
* JSON
* python-dotenv

## 📁 Project Structure

```text
Supermarket-Sales-Optimizer/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── inventory.db
├── supermarket_action_plan.txt
└── README.md
```

> `inventory.db` and `supermarket_action_plan.txt` are generated/used by the application. API keys should be stored in `.env` and must never be committed to GitHub.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/machariaizo/Supermarket-Sales-Optimizer.git
cd Supermarket-Sales-Optimizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create a `.env` file in the project directory:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the application

```bash
python main.py
```

## 💬 Example Questions

The assistant can be used to ask questions such as:

```text
Which products expire within 3 days?
Which products need urgent attention?
What products should be discounted?
Which dairy products are approaching expiry?
Which products should I promote?
```

The application also supports:

```text
view   → Display inventory
add    → Add a new product
exit   → Exit the application
```

## 🛡️ AI Guardrails

The prototype includes basic safeguards to improve the reliability of AI-generated recommendations:

* Rejects questions unrelated to supermarket operations
* Grounds recommendations in retrieved database records
* Instructs the AI not to invent products or prices
* Applies predefined discount limits
* Uses API retry and model-fallback logic

## 👥 Project Team

This project was developed collaboratively by:

| Team Member        | Role                                 |
| ------------------ | ------------------------------------ |
| **Isaac Macharia** | AI Development & Project Lead        |
| **Dancan Mugo**    | AI Development & Project Team Member |

### 🤝 Collaboration

Isaac Macharia and Dancan Mugo are working together to develop **Supermarket Sales Optimizer** from an AI prototype into a practical supermarket management solution.

## 🎓 Academic Context

**End of Module Project — AI-Class-S11**

This project demonstrates the integration of AI, structured prompting, database management, and RAG principles into a practical business-use case.

## 🌱 Future Development

The long-term vision is to expand the prototype into a complete AI supermarket management platform with:

* Sales forecasting
* Demand prediction
* Low-stock alerts
* Automated reorder recommendations
* Fast- and slow-moving product analysis
* Profit-margin analysis
* Dynamic pricing recommendations
* Product bundling and cross-selling
* Web-based management dashboard
* Multi-branch supermarket support
* Automated business intelligence reports

The ultimate goal is simple:

> **Turn supermarket data into smarter business decisions.**

## 🔗 Repository

**GitHub:** https://github.com/machariaizo/Supermarket-Sales-Optimizer

## 📌 Project Status

**Version:** `0.1.0`
**Status:** 🚧 Active Development
**Project Type:** AI / RAG / Inventory Management / Business Automation

---

**Built with Python + Google Gemini + SQLite**

### 👨‍💻 Team

**Isaac Macharia & Dancan Mugo**

*Turning supermarket data into smarter decisions.*

### 🤝 Collaboration

Isaac Macharia and Dancan Mugo are working together to develop **Supermarket Sales Optimizer** from an AI prototype into a practical supermarket management solution.

The project combines:

* Artificial Intelligence
* Inventory Management
* Retrieval-Augmented Generation (RAG)
* Database Management
* Sales Optimization
* Pricing & Promotion Intelligence

---

## 🔗 Repository

**GitHub Repository:**
[github.com/machariaizo/Supermarket-Sales-Optimizer](https://github.com/machariaizo/Supermarket-Sales-Optimizer?utm_source=chatgpt.com)

---

## 🌱 Our Vision

We are building this project with the goal of demonstrating how **AI can turn supermarket data into practical business decisions**.

Rather than simply showing a manager what is in stock, the future system should help answer:

> **What should the supermarket do next?**

From identifying products approaching expiry to recommending promotions, pricing actions, stock replenishment, and eventually sales opportunities, our vision is to develop an intelligent assistant that supports better supermarket decision-making.

---

## 📌 Project Status

**Current Version:** `0.1.0`
**Status:** 🚧 Active Development
**Project Type:** AI / RAG / Inventory Management / Business Automation

This is an evolving project. New capabilities, improvements, testing, and business intelligence features will be added as development continues.

---

## ⭐ Support the Project

If you find the project interesting, consider giving the repository a ⭐ on GitHub and following its development.

**Built with Python + Google Gemini + SQLite**

### 👨‍💻 Team

**Isaac Macharia & Dancan Mugo**

*Turning supermarket data into smarter decisions.*
