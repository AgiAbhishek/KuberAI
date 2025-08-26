
class KuberAI {
    constructor() {
        this.userId = this.generateUserId();
        this.goldPriceINR = 5469.25; // Will be updated from API
        this.currentSection = 'chat';
        this.initializeElements();
        this.bindEvents();
        this.setupNavigation();
        
        // Initialize gold price and then update calculation
        this.updateGoldPrice().then(() => {
            if (this.amountInput) {
                this.updateGoldCalculation();
            }
        });
        this.updateAnalytics();
    }

    generateUserId() {
        return 'kuber_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.quickButtons = document.querySelectorAll('.quick-btn');
        
        // Modal elements
        this.purchaseModal = document.getElementById('purchaseModal');
        this.successModal = document.getElementById('successModal');
        this.purchaseForm = document.getElementById('purchaseForm');
        this.amountInput = document.getElementById('amount');
        this.goldAmountSpan = document.getElementById('goldAmount');
        
        // Price elements
        this.sidebarGoldPrice = document.getElementById('sidebarGoldPrice');
        
        // Navigation elements
        this.navItems = document.querySelectorAll('.nav-item');
        this.contentSections = document.querySelectorAll('.content-section');
        this.sectionTitle = document.getElementById('sectionTitle');
        this.sectionSubtitle = document.getElementById('sectionSubtitle');
        
        // Analytics elements
        this.totalUsers = document.getElementById('totalUsers');
        this.totalTransactions = document.getElementById('totalTransactions');
        this.totalGoldSold = document.getElementById('totalGoldSold');
        this.totalRevenue = document.getElementById('totalRevenue');
    }

    bindEvents() {
        // Chat events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Quick action buttons
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

        // Navigation events
        this.navItems.forEach(item => {
            item.addEventListener('click', () => {
                const section = item.getAttribute('data-section');
                this.switchSection(section);
            });
        });

        // Add Investment button event
        const addInvestmentBtn = document.querySelector('.add-investment-btn');
        if (addInvestmentBtn) {
            addInvestmentBtn.addEventListener('click', () => {
                this.showPurchaseModal();
            });
        }
    }

    setupNavigation() {
        const sectionData = {
            chat: {
                title: 'AI Assistant',
                subtitle: 'Get intelligent gold investment advice powered by advanced AI'
            },
            analytics: {
                title: 'Analytics Dashboard',
                subtitle: 'Track your investment performance and platform metrics'
            },
            portfolio: {
                title: 'Portfolio Management',
                subtitle: 'Monitor your gold holdings and investment performance'
            },
            market: {
                title: 'Market Intelligence',
                subtitle: 'Real-time gold market data and insights'
            }
        };

        this.sectionData = sectionData;
    }

    switchSection(sectionName) {
        // Update navigation
        this.navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-section') === sectionName) {
                item.classList.add('active');
            }
        });

        // Update content sections
        this.contentSections.forEach(section => {
            section.classList.remove('active');
            if (section.id === `${sectionName}-section`) {
                section.classList.add('active');
            }
        });

        // Update header
        const data = this.sectionData[sectionName];
        this.sectionTitle.textContent = data.title;
        this.sectionSubtitle.textContent = data.subtitle;

        this.currentSection = sectionName;

        // Load section-specific data
        if (sectionName === 'analytics') {
            this.updateAnalytics();
        }
    }

    async updateGoldPrice() {
        try {
            const response = await fetch('/gold-price');
            const data = await response.json();
            this.goldPriceINR = data.price_per_gram_inr;
            if (this.sidebarGoldPrice) {
                this.sidebarGoldPrice.textContent = `₹${this.goldPriceINR.toFixed(2)}/g`;
            }
            // Update price display in modal if elements exist
            const priceElement = document.getElementById('pricePerGram');
            if (priceElement) {
                priceElement.textContent = `₹${this.goldPriceINR.toFixed(2)}`;
            }
        } catch (error) {
            console.error('Error fetching gold price:', error);
            this.goldPriceINR = 5469.25; // Ensure fallback price is set
        }
    }

    async updateAnalytics() {
        try {
            const response = await fetch('/analytics');
            const data = await response.json();
            
            if (this.totalUsers) this.totalUsers.textContent = data.total_users;
            if (this.totalTransactions) this.totalTransactions.textContent = data.total_transactions;
            if (this.totalGoldSold) this.totalGoldSold.textContent = `${data.total_gold_sold_grams}g`;
            if (this.totalRevenue) this.totalRevenue.textContent = `₹${data.total_revenue_inr.toLocaleString('en-IN', {maximumFractionDigits: 2})}`;
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    }

    updateGoldCalculation() {
        console.log('updateGoldCalculation called');
        
        // Ensure elements exist
        if (!this.amountInput) {
            console.log('Amount input not found');
            return;
        }
        
        // Always ensure we have a valid gold price
        if (!this.goldPriceINR || this.goldPriceINR <= 0 || isNaN(this.goldPriceINR)) {
            console.log('Setting default gold price');
            this.goldPriceINR = 5469.25; // Hardcoded fallback price
        }
        
        console.log('Current gold price INR:', this.goldPriceINR);
        
        const inputValue = this.amountInput.value.trim();
        console.log('Input value:', inputValue);
        
        // Get calculation elements
        const gstElement = document.getElementById('gstAmount');
        const totalElement = document.getElementById('totalAmount');
        const priceElement = document.getElementById('pricePerGram');
        
        // Always update price per gram display
        if (priceElement) {
            priceElement.textContent = `₹${this.goldPriceINR.toFixed(2)}`;
            console.log('Updated price per gram display');
        }
        
        // Handle empty or invalid input
        if (inputValue === '' || isNaN(parseFloat(inputValue))) {
            console.log('Empty or invalid input, resetting displays');
            if (this.goldAmountSpan) this.goldAmountSpan.textContent = '0 grams (₹0.00)';
            if (gstElement) gstElement.textContent = '₹0.00';
            if (totalElement) totalElement.textContent = '₹0.00';
            return;
        }
        
        const amountINR = parseFloat(inputValue);
        console.log('Parsed amount INR:', amountINR);
        
        // Handle zero or negative amounts
        if (amountINR <= 0) {
            console.log('Zero or negative amount, resetting displays');
            if (this.goldAmountSpan) this.goldAmountSpan.textContent = '0 grams (₹0.00)';
            if (gstElement) gstElement.textContent = '₹0.00';
            if (totalElement) totalElement.textContent = '₹0.00';
            return;
        }
        
        // Perform calculations
        const gstRate = 0.03; // 3% GST
        const gstAmount = amountINR * gstRate;
        const totalAmount = amountINR + gstAmount;
        const goldGrams = amountINR / this.goldPriceINR;
        
        console.log('Calculations:', {
            amountINR,
            goldPriceINR: this.goldPriceINR,
            goldGrams,
            gstAmount,
            totalAmount
        });
        
        // Validate calculations before displaying
        if (isNaN(goldGrams) || !isFinite(goldGrams) || isNaN(gstAmount) || isNaN(totalAmount)) {
            console.error('Invalid calculation results:', { goldGrams, gstAmount, totalAmount });
            if (this.goldAmountSpan) this.goldAmountSpan.textContent = 'Calculation Error';
            if (gstElement) gstElement.textContent = '₹0.00';
            if (totalElement) totalElement.textContent = '₹0.00';
            return;
        }
        
        // Update displays with valid data
        if (this.goldAmountSpan) {
            this.goldAmountSpan.textContent = `${goldGrams.toFixed(4)} grams (₹${amountINR.toFixed(2)})`;
            console.log('Updated gold amount span');
        }
        if (gstElement) {
            gstElement.textContent = `₹${gstAmount.toFixed(2)}`;
            console.log('Updated GST element');
        }
        if (totalElement) {
            totalElement.textContent = `₹${totalAmount.toFixed(2)}`;
            console.log('Updated total element');
        }
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
            this.addMessage('I apologize, but I encountered a technical issue. Please try again in a moment.', 'bot');
            console.error('Error:', error);
        }
    }

    addMessage(text, sender, showPurchaseButton = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.innerHTML = `
            <span class="sender-name">${sender === 'bot' ? 'Kuber AI' : 'You'}</span>
            <span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        `;

        const textP = document.createElement('p');
        textP.innerHTML = text.replace(/\n/g, '<br>');

        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textP);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        if (showPurchaseButton && sender === 'bot') {
            const purchaseDiv = document.createElement('div');
            purchaseDiv.className = 'purchase-suggestion';
            purchaseDiv.innerHTML = `
                <p>🏆 Ready to build your golden portfolio with Kuber AI?</p>
                <button onclick="kuberAI.showPurchaseModal()">
                    <i class="fas fa-coins"></i>
                    Start Investment
                </button>
            `;
            contentDiv.appendChild(purchaseDiv);
        }

        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(contentDiv);
        
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
        
        // Force initialize gold price before showing modal
        if (!this.goldPriceINR || this.goldPriceINR <= 0 || isNaN(this.goldPriceINR)) {
            this.goldPriceINR = 5469.25;
            console.log('Initialized gold price for modal:', this.goldPriceINR);
        }
        
        // Ensure all elements are properly initialized
        this.setupPurchaseModal();
        
        // Update calculation immediately and after a delay
        this.updateGoldCalculation();
        setTimeout(() => {
            this.updateGoldCalculation();
        }, 100);
    }

    async processPurchase() {
        const formData = new FormData(this.purchaseForm);
        const userName = formData.get('userName');
        const userEmail = formData.get('userEmail');
        const amount = formData.get('amount');
        const amountINR = parseFloat(amount);
        
        // Validate form data
        if (!userName || userName.trim() === '') {
            alert('Please enter your full name');
            return;
        }
        
        if (!userEmail || userEmail.trim() === '') {
            alert('Please enter your email address');
            return;
        }
        
        if (!amount || isNaN(amountINR) || amountINR <= 0) {
            alert('Please enter a valid investment amount');
            return;
        }
        
        if (amountINR < 830) {
            alert('Minimum investment amount is ₹830');
            return;
        }
        
        const purchaseData = {
            user_id: this.userId,
            user_name: userName.trim(),
            email: userEmail.trim(),
            amount_inr: amountINR
        };

        console.log('Sending purchase data:', purchaseData);

        try {
            const response = await fetch('/purchase', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(purchaseData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Purchase failed:', errorData);
                alert(`Investment processing failed: ${errorData.detail || 'Unknown error'}`);
                return;
            }

            const result = await response.json();

            if (result.success) {
                this.purchaseModal.style.display = 'none';
                this.showSuccessModal(result);
                this.addMessage(`🎉 ${result.message}`, 'bot');
                this.updateAnalytics(); // Refresh analytics after purchase
                // Reset form
                this.purchaseForm.reset();
                this.updateGoldCalculation();
            } else {
                alert(`Investment processing failed: ${result.message || 'Unknown error'}`);
            }

        } catch (error) {
            console.error('Purchase error:', error);
            alert('Investment processing failed. Please check your connection and try again.');
        }
    }

    showSuccessModal(result) {
        const successDetails = document.getElementById('successDetails');
        const amountINR = parseFloat(document.getElementById('amount').value);
        const gstAmount = amountINR * 0.03;
        const totalWithGST = amountINR + gstAmount;
        
        successDetails.innerHTML = `
            <div class="calc-row"><strong>Transaction ID:</strong> <span>${result.transaction_id}</span></div>
            <div class="calc-row"><strong>Gold Purchased:</strong> <span>${result.gold_grams} grams</span></div>
            <div class="calc-row"><strong>Investment Amount:</strong> <span>₹${amountINR.toLocaleString('en-IN', {maximumFractionDigits: 2})}</span></div>
            <div class="calc-row"><strong>GST (3%):</strong> <span>₹${gstAmount.toLocaleString('en-IN', {maximumFractionDigits: 2})}</span></div>
            <div class="calc-row"><strong>Total Paid:</strong> <span>₹${totalWithGST.toLocaleString('en-IN', {maximumFractionDigits: 2})}</span></div>
            <div class="calc-row"><strong>Price per gram:</strong> <span>₹${this.goldPriceINR.toFixed(2)}</span></div>
        `;
        this.successModal.style.display = 'block';
    }
}

// Initialize Kuber AI when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.kuberAI = new KuberAI();
    
    // Auto-refresh analytics every 30 seconds
    setInterval(() => {
        if (window.kuberAI.currentSection === 'analytics') {
            window.kuberAI.updateAnalytics();
        }
        window.kuberAI.updateGoldPrice();
    }, 30000);
});

// Add some helpful global functions
window.switchToChat = () => window.kuberAI.switchSection('chat');
window.showPurchaseModal = () => window.kuberAI.showPurchaseModal();
