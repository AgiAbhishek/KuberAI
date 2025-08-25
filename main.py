
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
gold_price_per_gram = 65.50  # Hardcoded gold price in USD

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
            model="mixtral-8x7b-32768",
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
            'investing in gold', 'gold portfolio', 'gold trading'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in gold_keywords)

def generate_ai_response(message: str) -> str:
    """Generate intelligent responses using Groq AI"""
    try:
        system_prompt = f"""You are Kuber AI, a professional gold investment assistant. You are knowledgeable about gold markets, investment strategies, and digital gold platforms.

Current gold price: ${gold_price_per_gram}/gram

Guidelines:
- Provide accurate, helpful information about gold investment
- Be professional and encouraging about gold investment opportunities
- Always mention that digital gold is available for purchase
- Keep responses concise but informative
- Include relevant market insights when appropriate
- End responses with a subtle encouragement to invest

If asked about current prices, use the provided gold price above."""

        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Add purchase encouragement
        ai_response += "\n\n💰 Ready to start your gold investment journey? Our platform offers secure digital gold purchases with instant transactions!"
        
        return ai_response
    
    except Exception as e:
        print(f"Groq API error: {e}")
        # Fallback response
        return f"I'm here to help with your gold investment questions! Current gold price is ${gold_price_per_gram} per gram. Digital gold investment is a great way to diversify your portfolio. Would you like to make a purchase today?"

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
    
    if is_gold_related:
        response = generate_ai_response(request.message)
        
        return ChatResponse(
            response=response,
            is_gold_related=True,
            user_id=user_id,
            purchase_encouraged=True
        )
    else:
        return ChatResponse(
            response="I'm Kuber AI, your specialized gold investment assistant. I'm here to help you with gold investment strategies, market insights, and digital gold purchases. Please ask me about gold-related topics!",
            is_gold_related=False,
            user_id=user_id,
            purchase_encouraged=False
        )

@app.post("/purchase", response_model=PurchaseResponse)
def purchase_gold(request: PurchaseRequest):
    try:
        # Validate input
        if request.amount_usd <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if request.amount_usd < 10:
            raise HTTPException(status_code=400, detail="Minimum purchase amount is $10")
        
        # Calculate gold amount
        gold_grams = request.amount_usd / gold_price_per_gram
        
        # Generate transaction ID
        transaction_id = f"KUBER-{uuid.uuid4().hex[:8].upper()}"
        
        # Create user record
        user_record = {
            "user_id": request.user_id,
            "name": request.user_name,
            "email": request.email,
            "transaction_id": transaction_id,
            "gold_grams": round(gold_grams, 4),
            "amount_paid": request.amount_usd,
            "gold_price_per_gram": gold_price_per_gram,
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
            message=f"🎉 Congratulations! Kuber AI has successfully processed your purchase of {round(gold_grams, 4)} grams of digital gold for ${request.amount_usd}. Transaction ID: {transaction_id}"
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
        "price_per_gram_usd": gold_price_per_gram,
        "last_updated": datetime.now().isoformat(),
        "currency": "USD"
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
