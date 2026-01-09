/**
 * ============================================
 * PHISHING DETECTOR - FRONTEND JAVASCRIPT
 * ============================================
 * Handles form submission, API communication,
 * and dynamic UI updates without page reload.
 * ============================================
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 PhishGuard AI - Initialized');
    
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
     * Escape HTML to prevent XSS
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
