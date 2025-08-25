
from typing import Union, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import re
import uuid
import os
from datetime import datetime
from groq import Groq

app = FastAPI(title="Kuber AI - Gold Investment Assistant", description="Professional AI-powered gold investment chatbot")

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory database for demonstration
users_db = {}
gold_price_per_gram_usd = 65.50  # Hardcoded gold price in USD
usd_to_inr = 83.50  # Current USD to INR conversion rate
gold_price_per_gram_inr = gold_price_per_gram_usd * usd_to_inr  # Gold price in INR

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: str = None

class ChatResponse(BaseModel):
    response: str
    is_gold_related: bool
    user_id: str
    purchase_encouraged: bool = False

class PurchaseRequest(BaseModel):
    user_id: str
    amount_usd: float
    user_name: str
    email: str

class PurchaseResponse(BaseModel):
    success: bool
    transaction_id: str
    gold_grams: float
    total_cost: float
    message: str

def is_gold_investment_query(message: str) -> bool:
    """Enhanced gold investment detection using Groq AI"""
    try:
        system_prompt = """You are Kuber AI, a specialized gold investment assistant. Your job is to determine if a user's message is related to gold investment, precious metals, or financial topics related to gold.

Return only 'TRUE' if the message is about:
- Gold investment, buying, selling, or trading
- Gold prices, market trends, or analysis
- Digital gold, gold ETFs, or gold-backed investments
- Precious metals investment advice
- Gold portfolio management
- Economic factors affecting gold

Return only 'FALSE' if the message is about other topics.

Respond with only TRUE or FALSE."""

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Updated to working model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        return result == "TRUE"
    
    except Exception as e:
        print(f"Groq API error: {e}")
        # Fallback to keyword detection
        gold_keywords = [
            'gold', 'investment', 'precious metal', 'bullion', 'gold price',
            'digital gold', 'buy gold', 'gold market', 'gold investment',
            'investing in gold', 'gold portfolio', 'gold trading', 'sona'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in gold_keywords)

def generate_ai_response(message: str, is_gold_related: bool = True) -> str:
    """Generate intelligent responses using Groq AI"""
    try:
        if is_gold_related:
            system_prompt = f"""You are Kuber AI, a professional gold investment assistant for the Indian market. You provide factual information about gold and digital gold investment.

Current gold price: ₹{gold_price_per_gram_inr:.2f}/gram (${gold_price_per_gram_usd}/gram)

Guidelines:
1. Answer the user's specific question about gold investment factually
2. Be concise and informative (2-3 sentences max)
3. Use Indian Rupees (₹) for pricing
4. Provide relevant market insights when asked
5. DO NOT give investment advice, only factual information
6. End with a gentle invitation to purchase digital gold

Examples:
- If asked about prices: "Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram..."
- If asked about benefits: "Gold historically serves as a hedge against inflation and currency devaluation..."
- If asked about digital gold: "Digital gold allows you to buy, sell and store gold electronically..."

Always end with: "Would you like to explore purchasing digital gold today?"

Answer the user's question specifically, don't give generic responses."""
        else:
            system_prompt = """You are Kuber AI, a helpful and knowledgeable assistant. You can answer questions on various topics while being friendly and informative. 

Guidelines:
1. Answer the user's question directly and helpfully
2. Be concise and informative
3. Be friendly and professional
4. If the conversation naturally relates to investments or finance, you can mention your specialty in gold investment

Do not force gold investment topics if the user is asking about something completely unrelated."""

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Updated to working model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        ai_response = response.choices[0].message.content.strip()
        return ai_response
    
    except Exception as e:
        print(f"Groq API error: {e}")
        if is_gold_related:
            # Improved fallback response based on common queries
            if any(word in message.lower() for word in ['price', 'cost', 'rate']):
                return f"Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram. Gold prices fluctuate based on global market conditions and demand. Would you like to explore purchasing digital gold today?"
            elif any(word in message.lower() for word in ['benefit', 'advantage', 'why']):
                return f"Gold serves as a hedge against inflation and provides portfolio diversification. Digital gold offers the convenience of buying small quantities without storage concerns. Would you like to explore purchasing digital gold today?"
            else:
                return f"Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram. Digital gold allows you to invest in gold electronically with the convenience of instant transactions. Would you like to explore purchasing digital gold today?"
        else:
            return "I'm Kuber AI, and I'm happy to help you with that question! While I specialize in gold investment advice, I'm here to assist you with various topics. Is there anything specific you'd like to know?"

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
def read_root():
    return {"message": "Kuber AI - Gold Investment Assistant", "endpoints": ["/chat", "/purchase", "/users"]}

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Generate user ID if not provided
    user_id = request.user_id or str(uuid.uuid4())
    
    # Check if message is gold-related using AI
    is_gold_related = is_gold_investment_query(request.message)
    
    # Generate AI response for both gold-related and general queries
    response = generate_ai_response(request.message, is_gold_related)
    
    return ChatResponse(
        response=response,
        is_gold_related=is_gold_related,
        user_id=user_id,
        purchase_encouraged=is_gold_related
    )

@app.post("/purchase", response_model=PurchaseResponse)
def purchase_gold(request: PurchaseRequest):
    try:
        # Convert USD to INR for validation
        amount_inr = request.amount_usd * usd_to_inr
        
        # Validate input
        if request.amount_usd <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if amount_inr < 830:  # Minimum ₹830 (equivalent to $10)
            raise HTTPException(status_code=400, detail="Minimum purchase amount is ₹830")
        
        # Calculate gold amount using INR pricing
        gold_grams = amount_inr / gold_price_per_gram_inr
        
        # Generate transaction ID
        transaction_id = f"KUBER-{uuid.uuid4().hex[:8].upper()}"
        
        # Create user record
        user_record = {
            "user_id": request.user_id,
            "name": request.user_name,
            "email": request.email,
            "transaction_id": transaction_id,
            "gold_grams": round(gold_grams, 4),
            "amount_paid_usd": request.amount_usd,
            "amount_paid_inr": round(amount_inr, 2),
            "gold_price_per_gram_inr": round(gold_price_per_gram_inr, 2),
            "purchase_date": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Store in database
        users_db[request.user_id] = user_record
        
        return PurchaseResponse(
            success=True,
            transaction_id=transaction_id,
            gold_grams=round(gold_grams, 4),
            total_cost=request.amount_usd,
            message=f"🎉 Congratulations! Kuber AI has successfully processed your purchase of {round(gold_grams, 4)} grams of digital gold for ₹{amount_inr:.2f}. Transaction ID: {transaction_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@app.get("/users/{user_id}")
def get_user_record(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

@app.get("/users")
def get_all_users():
    return {"total_users": len(users_db), "users": list(users_db.values())}

@app.get("/gold-price")
def get_gold_price():
    return {
        "price_per_gram_inr": round(gold_price_per_gram_inr, 2),
        "price_per_gram_usd": gold_price_per_gram_usd,
        "usd_to_inr_rate": usd_to_inr,
        "last_updated": datetime.now().isoformat(),
        "primary_currency": "INR"
    }

@app.get("/analytics")
def get_analytics():
    total_users = len(users_db)
    total_transactions = sum(1 for user in users_db.values() if user.get("status") == "completed")
    total_gold_sold = sum(user.get("gold_grams", 0) for user in users_db.values())
    total_revenue = sum(user.get("amount_paid", 0) for user in users_db.values())
    
    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_gold_sold_grams": round(total_gold_sold, 4),
        "total_revenue_usd": round(total_revenue, 2),
        "average_transaction_size": round(total_revenue / max(total_transactions, 1), 2)
    }

# Test endpoints
@app.get("/test/chat-examples")
def get_chat_examples():
    return {
        "gold_related_queries": [
            "What is the current gold price?",
            "Should I invest in gold for my retirement?",
            "How does gold perform during inflation?",
            "What are the benefits of digital gold?",
            "Is now a good time to buy gold?"
        ],
        "non_gold_queries": [
            "What's the weather today?",
            "How do I cook pasta?",
            "Tell me about cryptocurrency"
        ]
    }
