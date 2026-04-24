/**
 * ============================================
 * PHISHING DETECTOR - FRONTEND JAVASCRIPT
 * ============================================
 * Handles form submission, API communication,
 * and dynamic UI updates without page reload.
 * ============================================
 */

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 PhishGuard AI - Initialized');
    
    // Password toggle functionality (for login/register pages)
    const togglePasswordBtn = document.getElementById('togglePassword');
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const passwordInput = this.parentElement.querySelector('input[type="password"], input[type="text"]');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15.3689 4.6311L13.8895 6.1105C12.7895 5.4105 11.4389 5 10 5C6.5 5 3.25 7.5 1.5 11C2.33333 12.6667 3.66667 14 5.28893 14.7889L6.70583 13.372C5.82583 13.012 5.08583 12.392 4.56583 11.572C5.98583 9.752 8.18583 8.5 10.6658 8.5C11.1458 8.5 11.6158 8.542 12.0658 8.612L13.4758 7.202C12.4158 6.892 11.2858 6.752 10.1258 6.792L15.3689 4.6311ZM10 11.5C9.17157 11.5 8.5 10.8284 8.5 10C8.5 9.17157 9.17157 8.5 10 8.5C10.8284 8.5 11.5 9.17157 11.5 10C11.5 10.8284 10.8284 11.5 10 11.5Z" fill="currentColor"/>
                        <path d="M10 4C6.5 4 3.25 6.5 1.5 10C3.25 13.5 6.5 16 10 16C13.5 16 16.75 13.5 18.5 10C18.38 9.76 18.25 9.52 18.11 9.29L16.76 10.64C16.24 12.36 14.78 13.65 13 13.92L14.42 12.5C14.78 12.14 14.78 11.54 14.42 11.18C14.06 10.82 13.46 10.82 13.1 11.18L11.68 12.6C11.22 12.85 10.64 12.85 10.18 12.6C9.72 12.35 9.72 11.77 10.18 11.31L15.37 6.12C16.09 6.84 16.69 7.68 17.15 8.6C17.61 9.52 17.85 10.52 17.85 11.5C17.85 14.54 15.04 17 11.5 17C10.78 17 10.09 16.89 9.44 16.68L8.02 18.1C8.86 18.37 9.72 18.5 10.6 18.5C14.5 18.5 18.09 15.96 19.69 12.31C19.89 11.85 19.89 11.33 19.69 10.87C18.09 7.21 14.5 4.68 10.6 4.68C10.4 4.68 10.2 4.68 10 4.68V4Z" fill="currentColor"/>
                    </svg>
                `;
            } else {
                passwordInput.type = 'password';
                this.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 4C6.5 4 3.25 6.5 1.5 10C3.25 13.5 6.5 16 10 16C13.5 16 16.75 13.5 18.5 10C16.75 6.5 13.5 4 10 4ZM10 14C7.5 14 5.33333 12.3333 4.33333 10C5.33333 7.66667 7.5 6 10 6C12.5 6 14.6667 7.66667 15.6667 10C14.6667 12.3333 12.5 14 10 14Z" fill="currentColor"/>
                        <circle cx="10" cy="10" r="2.5" fill="currentColor"/>
                    </svg>
                `;
            }
        });
    }
    
    // Password strength indicator (for register page)
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('passwordStrength');
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 'weak';
            let message = '';
            
            if (password.length >= 12) {
                strength = 'strong';
                message = '✓ Strong password';
            } else if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) {
                strength = 'strong';
                message = '✓ Strong password';
            } else if (password.length >= 8) {
                strength = 'medium';
                message = '⚠ Medium strength - add numbers and uppercase letters';
            } else {
                strength = 'weak';
                message = '✗ Password too short (min 8 characters)';
            }
            
            passwordStrength.className = `password-strength ${strength}`;
            passwordStrength.textContent = message;
        });
    }
    
    // Password match validation (for register page)
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordMatch = document.getElementById('passwordMatch');
    if (passwordInput && confirmPasswordInput && passwordMatch) {
        confirmPasswordInput.addEventListener('input', function() {
            if (this.value === passwordInput.value) {
                passwordMatch.className = 'password-match success';
                passwordMatch.textContent = '✓ Passwords match';
            } else {
                passwordMatch.className = 'password-match error';
                passwordMatch.textContent = '✗ Passwords do not match';
            }
        });
    }
    
    // Get DOM elements
    const form = document.getElementById('phishingForm');
    const urlInput = document.getElementById('urlInput');
    const checkButton = document.getElementById('checkButton');
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');
    const btnText = checkButton.querySelector('.btn-text');
    const btnLoader = checkButton.querySelector('.btn-loader');
    
    // Example buttons
    const exampleButtons = document.querySelectorAll('.example-btn');
    
    /**
     * Handle form submission
     */
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        
        // Validate URL
        if (!url) {
            showError('Please enter a URL');
            return;
        }
        
        // Check if URL starts with http:// or https://
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            showError('URL must start with http:// or https://');
            urlInput.focus();
            return;
        }
        
        // Start analysis
        await analyzeURL(url);
    });
    
    /**
     * Handle example button clicks
     */
    exampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exampleUrl = this.getAttribute('data-url');
            urlInput.value = exampleUrl;
            urlInput.focus();
            
            // Optionally auto-submit
            form.dispatchEvent(new Event('submit'));
        });
    });
    
    /**
     * Analyze URL using Flask API
     * @param {string} url - The URL to analyze
     */
    async function analyzeURL(url) {
        try {
            // Show loading state
            setLoadingState(true);
            hideResult();
            
            // Make API request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            // Hide loading state
            setLoadingState(false);
            
            // Handle response
            if (data.status === 'success') {
                displayResult(data);
            } else {
                showError(data.message || 'An error occurred during analysis');
            }
            
        } catch (error) {
            console.error('Error:', error);
            setLoadingState(false);
            showError('Failed to connect to the server. Please try again.');
        }
    }
    
    /**
     * Display analysis result
     * @param {Object} data - Result data from API
     */
    function displayResult(data) {
        const isSafe = data.prediction === 'safe';
        const statusClass = isSafe ? 'safe' : 'danger';
        const statusIcon = isSafe ? '✅' : '⚠️';
        const statusText = isSafe ? 'SAFE WEBSITE' : 'PHISHING DETECTED';
        const statusMessage = isSafe 
            ? 'This website appears to be legitimate and safe to visit.'
            : 'This website shows signs of phishing. Proceed with extreme caution!';
        
        // Build result HTML
        const resultHTML = `
            <div class="result-box ${statusClass}">
                <div class="result-header">
                    <div class="result-icon">${statusIcon}</div>
                    <div class="result-title">
                        <h3>${statusMessage}</h3>
                        <span class="result-badge ${statusClass}">${statusText}</span>
                    </div>
                </div>
                
                <div class="result-url">
                    <strong>URL:</strong> ${escapeHtml(data.url)}
                </div>
                
                <div class="result-details">
                    <div class="detail-item">
                        <span class="detail-label">Confidence Level</span>
                        <span class="detail-value">${data.confidence.toFixed(2)}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill ${statusClass}" style="width: 0%;" data-width="${data.confidence}%"></div>
                    </div>
                </div>
                
                <div class="result-details">
                    <div class="detail-item">
                        <span class="detail-label">Legitimacy Score</span>
                        <span class="detail-value" style="color: var(--success)">${data.details.legitimacy_score.toFixed(2)}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Phishing Score</span>
                        <span class="detail-value" style="color: var(--danger)">${data.details.phishing_score.toFixed(2)}%</span>
                    </div>
                </div>
                
                <div class="result-details">
                    <div class="detail-item">
                        <span class="detail-label">URL Length</span>
                        <span class="detail-value">${data.features.urlLen} chars</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Domain Length</span>
                        <span class="detail-value">${data.features.domainLen} chars</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Subdomains</span>
                        <span class="detail-value">${data.features.nosOfSubdomain}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Contains IP</span>
                        <span class="detail-value">${data.features.isIp ? '⚠️ Yes' : '✓ No'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Has @ Symbol</span>
                        <span class="detail-value">${data.features['is@'] ? '⚠️ Yes' : '✓ No'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Has Redirect</span>
                        <span class="detail-value">${data.features.isredirect ? '⚠️ Yes' : '✓ No'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Has Dash</span>
                        <span class="detail-value">${data.features.haveDash ? '⚠️ Yes' : '✓ No'}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Insert result HTML
        resultContent.innerHTML = resultHTML;
        
        // Show result with animation
        resultSection.style.display = 'block';
        
        // Animate confidence bar
        setTimeout(() => {
            const confidenceFill = resultContent.querySelector('.confidence-fill');
            if (confidenceFill) {
                confidenceFill.style.width = confidenceFill.getAttribute('data-width');
            }
        }, 100);
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        const errorHTML = `
            <div class="result-box danger">
                <div class="result-header">
                    <div class="result-icon">❌</div>
                    <div class="result-title">
                        <h3>Error</h3>
                    </div>
                </div>
                <div class="result-url">
                    ${escapeHtml(message)}
                </div>
            </div>
        `;
        
        resultContent.innerHTML = errorHTML;
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Hide result section
     */
    function hideResult() {
        resultSection.style.display = 'none';
    }
    
    /**
     * Set loading state for the form
     * @param {boolean} isLoading - Whether to show loading state
     */
    function setLoadingState(isLoading) {
        if (isLoading) {
            checkButton.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'flex';
            urlInput.disabled = true;
        } else {
            checkButton.disabled = false;
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            urlInput.disabled = false;
        }
    }
    
    /**
     * Add input animation
     */
    urlInput.addEventListener('input', function() {
        if (this.value.length > 0) {
            this.style.borderColor = 'var(--primary)';
        } else {
            this.style.borderColor = 'var(--border)';
        }
    });
    
    /**
     * Handle Enter key on example buttons
     */
    exampleButtons.forEach(button => {
        button.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.click();
            }
        });
    });
    
    console.log('✅ Event listeners attached successfully');
});

// ============================================
// CHATBOT FUNCTIONALITY
// ============================================

// Chatbot state
let isChatOpen = false;
let isTyping = false;

// Chatbot toggle button
document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    const chatbotBadge = document.getElementById('chatbotBadge');
    
    // Toggle chat window
    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', function() {
            toggleChat();
        });
    }
    
    // Close chat window
    if (chatbotClose) {
        chatbotClose.addEventListener('click', function() {
            closeChat();
        });
    }
    
    // Send message on button click
    if (chatSend) {
        chatSend.addEventListener('click', function() {
            sendMessage();
        });
    }
    
    // Send message on Enter key
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    /**
     * Toggle chat window visibility
     */
    function toggleChat() {
        isChatOpen = !isChatOpen;
        if (isChatOpen) {
            chatbotWindow.style.display = 'flex';
            chatbotWindow.classList.add('chat-open');
            setTimeout(() => {
                chatInput.focus();
            }, 300);
            // Hide badge when opening chat
            chatbotBadge.style.display = 'none';
        } else {
            closeChat();
        }
    }
    
    /**
     * Close chat window
     */
    function closeChat() {
        isChatOpen = false;
        chatbotWindow.classList.remove('chat-open');
        setTimeout(() => {
            chatbotWindow.style.display = 'none';
        }, 300);
    }
    
    /**
     * Send message to chatbot API
     */
    async function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message || isTyping) {
            return;
        }
        
        // Add user message to chat
        addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Send to backend API
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            hideTypingIndicator();
            
            if (data.status === 'success') {
                addMessage(data.response, 'bot');
            } else {
                addMessage('Sorry, I encountered an error. Please make sure the OpenAI API key is configured correctly.', 'bot');
                console.error('Chat error:', data.message);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            hideTypingIndicator();
            addMessage('Sorry, I couldn\'t connect to the server. Please check your connection and try again.', 'bot');
        }
    }
    
    /**
     * Add message to chat display
     * @param {string} text - Message text
     * @param {string} sender - 'user' or 'bot'
     */
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    /**
     * Show typing indicator
     */
    function showTypingIndicator() {
        isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    function hideTypingIndicator() {
        isTyping = false;
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Scroll chat to bottom
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    console.log('💬 Chatbot initialized');
});
