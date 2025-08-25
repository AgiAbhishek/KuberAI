
from typing import Union, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import re
import uuid
from datetime import datetime

app = FastAPI()

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

# Simple LLM simulation for gold investment detection
def is_gold_investment_query(message: str) -> bool:
    gold_keywords = [
        'gold', 'investment', 'precious metal', 'bullion', 'gold price',
        'digital gold', 'buy gold', 'gold market', 'gold investment',
        'investing in gold', 'gold portfolio', 'gold trading'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in gold_keywords)

def generate_gold_investment_response(message: str) -> str:
    responses = {
        "general": "Gold is considered a safe-haven investment that can help diversify your portfolio and protect against inflation. Digital gold offers the convenience of owning gold without physical storage concerns.",
        "price": f"The current gold price is ${gold_price_per_gram} per gram. Gold prices fluctuate based on market conditions, economic factors, and global events.",
        "investment": "Gold investment can be a smart way to hedge against economic uncertainty. Digital gold platforms make it easy to start investing with small amounts.",
        "buying": "You can purchase digital gold instantly through our platform. It's backed by physical gold stored in secure vaults and can be bought or sold 24/7."
    }
    
    message_lower = message.lower()
    if any(word in message_lower for word in ['price', 'cost', 'expensive']):
        return responses["price"]
    elif any(word in message_lower for word in ['buy', 'purchase', 'invest']):
        return responses["buying"]
    elif any(word in message_lower for word in ['investment', 'portfolio', 'diversify']):
        return responses["investment"]
    else:
        return responses["general"]

@app.get("/")
def read_root():
    return {"message": "Gold Investment Chatbot API", "endpoints": ["/chat", "/purchase", "/users"]}

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Generate user ID if not provided
    user_id = request.user_id or str(uuid.uuid4())
    
    # Check if message is gold-related
    is_gold_related = is_gold_investment_query(request.message)
    
    if is_gold_related:
        response = generate_gold_investment_response(request.message)
        # Add purchase encouragement
        response += "\n\nWould you like to purchase some digital gold today? Our platform offers secure and instant transactions!"
        
        return ChatResponse(
            response=response,
            is_gold_related=True,
            user_id=user_id,
            purchase_encouraged=True
        )
    else:
        return ChatResponse(
            response="I'm specialized in gold investment advice. Please ask me questions about gold investment, digital gold, or precious metals trading.",
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
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
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
            message=f"Congratulations! You have successfully purchased {round(gold_grams, 4)} grams of digital gold for ${request.amount_usd}. Transaction ID: {transaction_id}"
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

# Test endpoints for demonstration
@app.get("/test/chat-examples")
def get_chat_examples():
    return {
        "gold_related_queries": [
            "What is the current gold price?",
            "Should I invest in gold?",
            "How do I buy digital gold?",
            "Is gold a good investment for my portfolio?"
        ],
        "non_gold_queries": [
            "What's the weather today?",
            "How do I cook pasta?",
            "Tell me about stocks"
        ]
    }

@app.get("/test/purchase-example")
def get_purchase_example():
    return {
        "example_request": {
            "user_id": "user123",
            "amount_usd": 100.0,
            "user_name": "John Doe",
            "email": "john@example.com"
        },
        "note": "POST this to /purchase endpoint"
    }
