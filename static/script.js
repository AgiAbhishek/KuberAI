
class GoldChatBot {
    constructor() {
        this.userId = this.generateUserId();
        this.goldPrice = 65.50;
        this.initializeElements();
        this.bindEvents();
        this.updateGoldPrice();
    }

    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.quickButtons = document.querySelectorAll('.quick-btn');
        this.purchaseModal = document.getElementById('purchaseModal');
        this.successModal = document.getElementById('successModal');
        this.purchaseForm = document.getElementById('purchaseForm');
        this.amountInput = document.getElementById('amount');
        this.goldAmountSpan = document.getElementById('goldAmount');
        this.currentPriceSpan = document.getElementById('current-price');
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        this.quickButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.messageInput.value = message;
                this.sendMessage();
            });
        });

        // Modal events
        document.querySelector('.close').addEventListener('click', () => {
            this.purchaseModal.style.display = 'none';
        });

        document.getElementById('closeSuccess').addEventListener('click', () => {
            this.successModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === this.purchaseModal) {
                this.purchaseModal.style.display = 'none';
            }
            if (e.target === this.successModal) {
                this.successModal.style.display = 'none';
            }
        });

        // Purchase form events
        this.amountInput.addEventListener('input', () => {
            this.updateGoldCalculation();
        });

        this.purchaseForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.processPurchase();
        });
    }

    async updateGoldPrice() {
        try {
            const response = await fetch('/gold-price');
            const data = await response.json();
            this.goldPrice = data.price_per_gram_usd;
            this.currentPriceSpan.textContent = `Gold: $${this.goldPrice.toFixed(2)}/g`;
        } catch (error) {
            console.error('Error fetching gold price:', error);
        }
    }

    updateGoldCalculation() {
        const amount = parseFloat(this.amountInput.value) || 0;
        const goldGrams = amount / this.goldPrice;
        this.goldAmountSpan.textContent = `${goldGrams.toFixed(4)} grams`;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();
            this.addMessage(data.response, 'bot', data.purchase_encouraged);

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('Error:', error);
        }
    }

    addMessage(text, sender, showPurchaseButton = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<p>${text}</p>`;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);

        if (showPurchaseButton && sender === 'bot') {
            const purchaseDiv = document.createElement('div');
            purchaseDiv.className = 'purchase-suggestion';
            purchaseDiv.innerHTML = `
                <p>💰 Ready to invest in digital gold?</p>
                <button onclick="chatBot.showPurchaseModal()">Start Purchase</button>
            `;
            messageDiv.appendChild(purchaseDiv);
        }

        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showPurchaseModal() {
        this.purchaseModal.style.display = 'block';
        this.updateGoldCalculation();
    }

    async processPurchase() {
        const formData = new FormData(this.purchaseForm);
        const purchaseData = {
            user_id: this.userId,
            user_name: formData.get('userName'),
            email: formData.get('userEmail'),
            amount_usd: parseFloat(formData.get('amount'))
        };

        try {
            const response = await fetch('/purchase', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(purchaseData)
            });

            const result = await response.json();

            if (result.success) {
                this.purchaseModal.style.display = 'none';
                this.showSuccessModal(result);
                this.addMessage(`🎉 Purchase completed! Transaction ID: ${result.transaction_id}. You now own ${result.gold_grams} grams of digital gold!`, 'bot');
            } else {
                alert('Purchase failed. Please try again.');
            }

        } catch (error) {
            console.error('Purchase error:', error);
            alert('Purchase failed. Please check your details and try again.');
        }
    }

    showSuccessModal(result) {
        const successDetails = document.getElementById('successDetails');
        successDetails.innerHTML = `
            <div class="calc-row"><strong>Transaction ID:</strong> <span>${result.transaction_id}</span></div>
            <div class="calc-row"><strong>Gold Purchased:</strong> <span>${result.gold_grams} grams</span></div>
            <div class="calc-row"><strong>Total Paid:</strong> <span>$${result.total_cost.toFixed(2)}</span></div>
            <div class="calc-row"><strong>Price per gram:</strong> <span>$${this.goldPrice.toFixed(2)}</span></div>
        `;
        this.successModal.style.display = 'block';
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.chatBot = new GoldChatBot();
});
