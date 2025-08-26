
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
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Kuber AI - Gold Investment Assistant", description="Professional AI-powered gold investment chatbot")

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize MongoDB client
try:
    mongodb_url = os.getenv("MONGODB_URL")
    if mongodb_url:
        mongo_client = MongoClient(mongodb_url)
        # Test the connection
        mongo_client.admin.command('ismaster')
        db = mongo_client.KuberAI
        users_collection = db.users
        transactions_collection = db.transactions
        print("✅ MongoDB connected successfully")
    else:
        print("❌ MongoDB URL not found in environment variables")
        mongo_client = None
        db = None
        users_collection = None
        transactions_collection = None
except ConnectionFailure as e:
    print(f"❌ MongoDB connection failed: {e}")
    mongo_client = None
    db = None
    users_collection = None
    transactions_collection = None

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Fallback in-memory database for demonstration
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
    amount_inr: float = None
    user_name: str
    email: str

class PurchaseResponse(BaseModel):
    success: bool
    transaction_id: str
    gold_grams: float
    total_cost: float
    message: str

def is_gold_investment_query(message: str) -> bool:
    """Enhanced gold investment detection using Groq AI with improved examples"""
    try:
        system_prompt = """You are Kuber AI, a specialized gold investment assistant. Your job is to determine if a user's message is related to gold investment, precious metals, or financial topics related to gold.

Return only 'TRUE' if the message is about:
- Gold investment, buying, selling, or trading: "Should I invest in gold?", "Is digital gold safe?", "Buy gold now", "How to purchase digital gold?", "Gold price today?"
- Gold prices, market trends, or analysis
- Digital gold, gold ETFs, or gold-backed investments
- Precious metals investment advice
- Gold portfolio management
- Economic factors affecting gold

Return only 'FALSE' if the message is about other topics like:
- "Golden retriever care", "Gold medal stats", "Golden gate bridge", "Gold color paint"

Focus on INVESTMENT and FINANCIAL context. If the word "gold" appears but is not about investment/finance, return FALSE.

Respond with only TRUE or FALSE."""

        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
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
        # Enhanced fallback with negative keywords
        gold_investment_keywords = [
            'gold investment', 'buy gold', 'sell gold', 'gold price', 'gold market',
            'digital gold', 'gold trading', 'invest in gold', 'gold portfolio',
            'precious metal investment', 'gold bullion', 'gold etf', 'sona investment'
        ]
        
        # Keywords that should NOT trigger gold investment intent
        negative_keywords = [
            'golden retriever', 'gold medal', 'golden gate', 'gold color',
            'gold paint', 'gold jewelry design', 'gold teeth', 'golden hour',
            'gold fish', 'golden rule', 'gold standard test'
        ]
        
        message_lower = message.lower()
        
        # Check for negative keywords first
        if any(neg_keyword in message_lower for neg_keyword in negative_keywords):
            return False
            
        # Then check for positive investment keywords
        return any(keyword in message_lower for keyword in gold_investment_keywords)

def generate_ai_response(message: str, is_gold_related: bool = True) -> str:
    """Generate intelligent responses using Groq AI with improved nudge templates"""
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
6. ONLY add the nudge template if the user is asking about investment, buying, or purchasing

Nudge template to use ONLY for purchase-related queries:
"🏆 Ready to build your golden portfolio with Kuber AI? Start Investment"

Examples:
- If asked about prices: "Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram. Gold prices fluctuate based on global market conditions and economic factors."
- If asked about benefits: "Gold historically serves as a hedge against inflation and currency devaluation. Digital gold offers the convenience of fractional ownership without storage concerns."
- If asked about digital gold: "Digital gold allows you to buy, sell and store gold electronically with 24/7 liquidity and no storage costs."
- If asked about buying/investing: Add the nudge template at the end.

Answer the user's question specifically, don't give generic responses. Only add the purchase nudge if they express interest in buying or investing."""
        else:
            system_prompt = """You are Kuber AI, a helpful and knowledgeable assistant. You can answer questions on various topics while being friendly and informative. 

Guidelines:
1. Answer the user's question directly and helpfully
2. Be concise and informative
3. Be friendly and professional
4. Do not mention gold investment unless the question is specifically about investments or finance

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
                return f"Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram. Gold prices fluctuate based on global market conditions and demand. If you'd like, I can help you purchase digital gold now and record it to your account."
            elif any(word in message.lower() for word in ['benefit', 'advantage', 'why']):
                return f"Gold serves as a hedge against inflation and provides portfolio diversification. Digital gold offers the convenience of buying small quantities without storage concerns. If you'd like, I can help you purchase digital gold now and record it to your account."
            else:
                return f"Current gold price is ₹{gold_price_per_gram_inr:.2f} per gram. Digital gold allows you to invest in gold electronically with the convenience of instant transactions. If you'd like, I can help you purchase digital gold now and record it to your account."
        else:
            return "I'm Kuber AI, and I'm happy to help you with that question! While I specialize in gold investment advice, I'm here to assist you with various topics. Is there anything specific you'd like to know?"

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
def read_root():
    return {"message": "Kuber AI - Gold Investment Assistant", "endpoints": ["/chat", "/purchase", "/users"]}

def detect_purchase_consent(message: str) -> bool:
    """Detect if user is giving consent to purchase"""
    consent_keywords = [
        'yes', 'confirm', 'buy', 'purchase', 'proceed', 'go ahead',
        'sure', 'okay', 'ok', 'agree', 'start investment', 'lets do it'
    ]
    message_lower = message.lower().strip()
    return any(keyword in message_lower for keyword in consent_keywords)

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Generate user ID if not provided
    user_id = request.user_id or str(uuid.uuid4())
    
    # Check if user is giving consent for purchase
    is_consent = detect_purchase_consent(request.message)
    
    if is_consent:
        # If user gives consent, provide purchase guidance
        response = "Perfect! I'm ready to help you invest in digital gold. Please click the 'Start Investment' button below to proceed with your purchase. You'll need to provide your name, email, and investment amount."
        return ChatResponse(
            response=response,
            is_gold_related=True,
            user_id=user_id,
            purchase_encouraged=True
        )
    
    # Check if message is gold-related using AI
    is_gold_related = is_gold_investment_query(request.message)
    
    # Generate AI response for both gold-related and general queries
    response = generate_ai_response(request.message, is_gold_related)
    
    # Check if user is showing purchase intent (not just asking general gold questions)
    purchase_intent_keywords = ['buy', 'purchase', 'invest', 'want to', 'how to buy', 'start investing']
    has_purchase_intent = any(keyword in request.message.lower() for keyword in purchase_intent_keywords)
    
    return ChatResponse(
        response=response,
        is_gold_related=is_gold_related,
        user_id=user_id,
        purchase_encouraged=is_gold_related and has_purchase_intent
    )

@app.post("/purchase", response_model=PurchaseResponse)
def purchase_gold(request: PurchaseRequest):
    try:
        # Use INR amount if provided, otherwise convert from USD
        amount_inr = request.amount_inr if request.amount_inr else request.amount_usd * usd_to_inr
        
        # Calculate GST (3%)
        gst_rate = 0.03
        gst_amount = amount_inr * gst_rate
        total_amount_with_gst = amount_inr + gst_amount
        
        # Validate input
        if amount_inr <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if amount_inr < 830:  # Minimum ₹830
            raise HTTPException(status_code=400, detail="Minimum purchase amount is ₹830")
        
        # Calculate gold amount using INR pricing (before GST)
        gold_grams = amount_inr / gold_price_per_gram_inr
        
        # Generate transaction ID
        transaction_id = f"KUBER-{uuid.uuid4().hex[:8].upper()}"
        
        # Create comprehensive user record
        user_record = {
            "user_id": request.user_id,
            "name": request.user_name,
            "email": request.email,
            "transaction_id": transaction_id,
            "gold_grams": round(gold_grams, 4),
            "amount_paid_usd": request.amount_usd,
            "amount_paid_inr": round(amount_inr, 2),
            "gst_amount": round(gst_amount, 2),
            "total_amount_with_gst": round(total_amount_with_gst, 2),
            "gst_rate": gst_rate,
            "gold_price_per_gram_inr": round(gold_price_per_gram_inr, 2),
            "purchase_date": datetime.now().isoformat(),
            "status": "completed",
            "currency": "INR"
        }
        
        # Ensure MongoDB storage with better error handling
        mongodb_success = False
        try:
            if mongo_client is not None and users_collection is not None and transactions_collection is not None:
                # Test MongoDB connection
                mongo_client.admin.command('ismaster')
                
                # Store user info
                user_result = users_collection.update_one(
                    {"user_id": request.user_id},
                    {"$set": {
                        "user_id": request.user_id,
                        "name": request.user_name,
                        "email": request.email,
                        "last_updated": datetime.now().isoformat()
                    }},
                    upsert=True
                )
                
                # Store transaction
                transaction_result = transactions_collection.insert_one(user_record.copy())
                
                if transaction_result.inserted_id:
                    mongodb_success = True
                    print(f"✅ Transaction {transaction_id} successfully stored in MongoDB")
                    print(f"✅ User record updated: {user_result.modified_count or user_result.upserted_id}")
                else:
                    raise Exception("Failed to insert transaction record")
                    
            else:
                raise Exception("MongoDB client or collections not available")
                
        except Exception as e:
            print(f"❌ MongoDB storage failed: {e}")
            print(f"⚠️ Falling back to in-memory storage for transaction {transaction_id}")
            # Fallback to in-memory storage
            users_db[request.user_id] = user_record
        
        # Return success response
        success_message = f"🎉 Congratulations! Kuber AI has successfully processed your purchase of {round(gold_grams, 4)} grams of digital gold for ₹{amount_inr:.2f} (Total with GST: ₹{total_amount_with_gst:.2f}). Transaction ID: {transaction_id}"
        
        if mongodb_success:
            success_message += " Your transaction has been securely recorded in our database."
        
        return PurchaseResponse(
            success=True,
            transaction_id=transaction_id,
            gold_grams=round(gold_grams, 4),
            total_cost=request.amount_usd,
            message=success_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Purchase processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@app.get("/users/{user_id}")
def get_user_record(user_id: str):
    try:
        if transactions_collection is not None:
            user_transactions = list(transactions_collection.find({"user_id": user_id}, {"_id": 0}))
            if not user_transactions:
                raise HTTPException(status_code=404, detail="User not found")
            return {"user_id": user_id, "transactions": user_transactions}
        else:
            # Fallback to in-memory database
            if user_id not in users_db:
                raise HTTPException(status_code=404, detail="User not found")
            return users_db[user_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/users")
def get_all_users():
    try:
        if transactions_collection is not None:
            all_transactions = list(transactions_collection.find({}, {"_id": 0}))
            unique_users = {}
            for transaction in all_transactions:
                user_id = transaction.get("user_id")
                if user_id not in unique_users:
                    unique_users[user_id] = []
                unique_users[user_id].append(transaction)
            
            return {
                "total_users": len(unique_users), 
                "total_transactions": len(all_transactions),
                "users": unique_users
            }
        else:
            # Fallback to in-memory database
            return {"total_users": len(users_db), "users": list(users_db.values())}
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "total_users": len(users_db), "users": list(users_db.values())}

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
    try:
        if transactions_collection is not None:
            # Get data from MongoDB
            all_transactions = list(transactions_collection.find({"status": "completed"}))
            unique_users = set(transaction.get("user_id") for transaction in all_transactions)
            
            total_users = len(unique_users)
            total_transactions = len(all_transactions)
            total_gold_sold = sum(transaction.get("gold_grams", 0) for transaction in all_transactions)
            total_revenue_usd = sum(transaction.get("amount_paid_usd", 0) for transaction in all_transactions)
            total_revenue_inr = sum(transaction.get("amount_paid_inr", 0) for transaction in all_transactions)
        else:
            # Fallback to in-memory database
            total_users = len(users_db)
            total_transactions = sum(1 for user in users_db.values() if user.get("status") == "completed")
            total_gold_sold = sum(user.get("gold_grams", 0) for user in users_db.values())
            total_revenue_usd = sum(user.get("amount_paid_usd", 0) for user in users_db.values())
            total_revenue_inr = sum(user.get("amount_paid_inr", 0) for user in users_db.values())
        
        return {
            "total_users": total_users,
            "total_transactions": total_transactions,
            "total_gold_sold_grams": round(total_gold_sold, 4),
            "total_revenue_usd": round(total_revenue_usd, 2),
            "total_revenue_inr": round(total_revenue_inr, 2),
            "average_transaction_size": round(total_revenue_usd / max(total_transactions, 1), 2),
            "database_status": "MongoDB" if transactions_collection is not None else "In-Memory"
        }
    except Exception as e:
        return {"error": f"Analytics error: {str(e)}"}

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
