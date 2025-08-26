
# Kuber AI - Gold Investment Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)](https://www.mongodb.com/)

A professional AI-powered gold investment chatbot built with FastAPI, MongoDB, and Groq AI. Kuber AI helps users make informed gold investment decisions and provides digital gold purchasing capabilities.

## 🌟 Features

- **AI-Powered Chat**: Intelligent gold investment advice using Groq AI
- **Digital Gold Trading**: Buy and sell digital gold with real-time pricing
- **Portfolio Management**: Track your gold investments and transactions
- **Analytics Dashboard**: View investment performance and platform metrics
- **Secure Database**: MongoDB Atlas integration for data persistence
- **Real-time Gold Prices**: Updated market pricing in Indian Rupees (₹)
- **GST Calculations**: Automatic 3% GST calculation on purchases
- **Transaction History**: Complete record of all gold transactions

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- MongoDB Atlas account (free tier available)
- Groq API key (free at groq.com)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd kuber-ai-gold-investment
```

#### 2. Install Dependencies
```bash
# Install using pip
pip install -r requirements.txt

# OR using Poetry (if you have it installed)
poetry install
```

#### 3. Environment Setup
Create a `.env` file in the root directory:
```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your credentials:
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# MongoDB Configuration  
MONGODB_URL=your_mongodb_connection_string_here

# Application Configuration
APP_NAME=Kuber AI
APP_VERSION=1.0.0

# Currency Configuration (Optional)
USD_TO_INR_RATE=83.50
GOLD_PRICE_USD=65.50
```

#### 4. Get Your API Keys

**Groq API Key:**
1. Visit [groq.com](https://groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it in your `.env` file

**MongoDB Atlas Setup:**
1. Visit [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (free tier: M0 Sandbox)
4. Create a database user with read/write permissions
5. Whitelist your IP address (or use 0.0.0.0/0 for development)
6. Get your connection string and update `.env` file

#### 5. Run the Application
```bash
# Method 1: Direct Python execution
python main.py

# Method 2: Using Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Using FastAPI CLI (if installed)
fastapi dev main.py
```

#### 6. Access the Application
Open your browser and navigate to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

## 📁 Project Structure

```
kuber-ai-gold-investment/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Poetry configuration
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
├── static/               # Static files (CSS, JS)
│   ├── style.css        # Application styling
│   └── script.js        # Frontend JavaScript
└── templates/           # HTML templates
    └── index.html       # Main web interface
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Your Groq AI API key | Yes | - |
| `MONGODB_URL` | MongoDB Atlas connection string | Yes | - |
| `APP_NAME` | Application name | No | Kuber AI |
| `APP_VERSION` | Application version | No | 1.0.0 |
| `USD_TO_INR_RATE` | Currency conversion rate | No | 83.50 |
| `GOLD_PRICE_USD` | Gold price in USD | No | 65.50 |

### Gold Pricing

- **Current Rate**: ₹5,469.25 per gram (hardcoded, can be made dynamic)
- **Minimum Purchase**: ₹830
- **GST**: 3% automatically added to all purchases
- **Currency**: Indian Rupees (₹)

## 🎯 API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `POST /chat` - Chat with AI assistant
- `POST /purchase` - Purchase digital gold
- `GET /gold-price` - Current gold pricing
- `GET /analytics` - Platform analytics

### User Management
- `GET /users` - List all users
- `GET /users/{user_id}` - Get specific user data

### Testing
- `GET /api` - API information
- `GET /test/chat-examples` - Example chat queries

## 💡 Usage Examples

### Chat with AI
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the current gold price?", "user_id": "user123"}'
```

### Purchase Gold
```bash
curl -X POST "http://localhost:8000/purchase" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "amount_inr": 5000,
       "user_name": "John Doe",
       "email": "john@example.com"
     }'
```

### Get Analytics
```bash
curl -X GET "http://localhost:8000/analytics"
```

## 🛠️ Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# With specific log level
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### Testing
```bash
# Test the application
python -c "import requests; print(requests.get('http://localhost:8000/api').json())"

# Test MongoDB connection
python -c "from main import mongo_client; print('MongoDB connected:', mongo_client.admin.command('ismaster'))"
```

## 🔐 Security Features

- Environment variable configuration for sensitive data
- MongoDB connection with authentication
- Input validation using Pydantic models
- CORS protection (can be configured)
- Secure transaction ID generation

## 📊 Database Schema

### Users Collection
```json
{
  "user_id": "kuber_xyz123",
  "name": "John Doe",
  "email": "john@example.com",
  "last_updated": "2024-01-15T10:30:00"
}
```

### Transactions Collection
```json
{
  "user_id": "kuber_xyz123",
  "transaction_id": "KUBER-ABC12345",
  "gold_grams": 0.9138,
  "amount_paid_inr": 5000.00,
  "gst_amount": 150.00,
  "total_amount_with_gst": 5150.00,
  "gold_price_per_gram_inr": 5469.25,
  "purchase_date": "2024-01-15T10:30:00",
  "status": "completed"
}
```

## 🚀 Deployment

The application is ready for deployment on various platforms:

- **Heroku**: Add `Procfile` with `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Works out of the box
- **DigitalOcean**: Use App Platform or Droplets
- **AWS**: Deploy on EC2, ECS, or Lambda

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection Failed**
```
Solution: Check your MongoDB URL and network whitelist settings
```

**Groq API Error**
```
Solution: Verify your API key is correct and has sufficient credits
```

**Port Already in Use**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`

---

**Made with ❤️ for gold investors everywhere**
