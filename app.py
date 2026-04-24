"""
Phishing Website Detection - Flask Backend
This Flask application provides a REST API for phishing detection.
It extracts features from URLs and uses a trained ML model for prediction.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
import joblib
import re
from urllib.parse import urlparse
import os
from groq import Groq
from dotenv import load_dotenv
from models import UserStorage, URLAnalysisStorage
import json

# Load environment variables from .env file
load_dotenv()

# FLASK APP INITIALIZATION
app = Flask(__name__)

# Load the trained ML model
MODEL_PATH = 'model/phishing_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None

# Secret key for flash messages (required even without sessions)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialize Groq API client
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("✓ Groq API key configured!")
    print("✓ Groq client initialized!")
else:
    print("⚠ Groq API key not set. Chatbot feature will be disabled.")
    print("  Set GROQ_API_KEY environment variable to enable chatbot.")
    groq_client = None

# FEATURE EXTRACTION FUNCTIONS

def extract_features(url):
    """
    
    Args:
        url (str): The URL to analyze
    
    Returns:
        dict: Dictionary containing all extracted features
    """
    
    features = {}
    
    try:
        # Parse the URL
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        # Build the full URL without protocol for length calculation
        # This matches how the dataset stores URLs (domain + path + query)
        url_without_protocol = domain + path
        if query:
            url_without_protocol += '?' + query
        
        # Feature 1: isIp - Check if URL contains an IP address instead of domain
        # Phishing sites often use IP addresses to avoid DNS tracking
        ip_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        features['isIp'] = 1 if ip_pattern.search(domain) else 0
        
        # Feature 2: urlLen - Length of FULL URL (domain + path + query)
        # This matches the dataset format where urlLen includes the path
        features['urlLen'] = len(url_without_protocol)
        
        # Feature 3: is@ - Check for @ symbol in URL
        # @ symbol can be used to hide the real domain (e.g., http://google.com@malicious.com)
        features['is@'] = 1 if '@' in url else 0
        
        # Feature 4: isredirect - Check for // in PATH only (not in protocol!)
        # Multiple slashes in path can indicate URL redirection attempts
        # We exclude the protocol part (https://) by checking path and query only
        path_and_query = path + '?' + query if query else path
        features['isredirect'] = 1 if '//' in path_and_query else 0
        
        # Feature 5: haveDash - Check for dash (-) in domain
        # Legitimate domains rarely use dashes; phishing sites use them for brand impersonation
        features['haveDash'] = 1 if '-' in domain else 0
        
        # Feature 6: domainLen - Length of the domain name only
        # Longer domains may indicate suspicious activity
        features['domainLen'] = len(domain)
        
        # Feature 7: nosOfSubdomain - Count number of subdomains
        # Multiple subdomains can be a sign of phishing (e.g., login.secure.paypal.fake.com)
        # Count the number of dots in domain (dots = subdomains + 1)
        if domain:
            features['nosOfSubdomain'] = domain.count('.')
        else:
            features['nosOfSubdomain'] = 0
        
        return features
    
    except Exception as e:
        print(f"Error extracting features: {e}")
        # Return default safe values if extraction fails
        return {
            'isIp': 0,
            'urlLen': 0,  # Domain length, not full URL
            'is@': 0,
            'isredirect': 0,
            'haveDash': 0,
            'domainLen': 0,
            'nosOfSubdomain': 0
        }


def validate_url(url):
    """
    Validate if the provided string is a proper URL.
    
    Args:
        url (str): URL to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not url or url.strip() == '':
        return False, "URL cannot be empty"
    
    # Check if URL has a scheme (http:// or https://)
    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"
    
    # Basic URL structure validation
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format"
        return True, None
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

# FLASK ROUTES

# AUTHENTICATION ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login - reads from Excel and sets simple cookie."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Find user in Excel file
        user_storage = UserStorage()
        user = user_storage.find_by_username_or_email(username)
        
        if user and user_storage.verify_password(user, password):
            # Set cookie with the actual USERNAME (not email)
            response = make_response(redirect(url_for('home')))
            response.set_cookie('username', user['username'], max_age=60*60*24*30)  # 30 days
            flash(f'Welcome back, {user["username"]}!', 'success')
            return response
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration - stores data in Excel."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms_accepted = request.form.get('terms') == 'on'
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not email or '@' not in email:
            errors.append('Please provide a valid email address.')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not terms_accepted:
            errors.append('You must accept the Terms of Service.')
        
        # Check if username or email already exists
        user_storage = UserStorage()
        if user_storage.find_by_username(username):
            errors.append('Username already taken. Please choose another.')
        
        if user_storage.find_by_email(email):
            errors.append('Email already registered. Please use another.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user in Excel
        try:
            new_user = user_storage.create_user(username, email, password)
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return render_template('register.html')
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Handle user logout - clear cookie."""
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('username')
    flash('You have been logged out successfully.', 'info')
    return response


@app.route('/profile')
def profile():
    """Display user profile and analysis history from Excel."""
    username = request.cookies.get('username')
    
    if not username:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('login'))
    
    # Get user data from Excel
    user_storage = UserStorage()
    user = user_storage.find_by_username(username)
    
    if not user:
        # Cookie has username but not found in Excel - clear cookie
        print(f"⚠️ WARNING: User '{username}' from cookie not found in Excel!")
        print(f"  Available users in Excel:")
        
        # List all users for debugging
        all_users = user_storage.get_all_users()
        for u in all_users:
            print(f"    - '{u['username']}'")
        
        flash(f'Error: User account "{username}" not found. Please login again.', 'error')
        response = make_response(redirect(url_for('login')))
        response.delete_cookie('username')  # Clear invalid cookie
        return response
    
    # Get user's analysis history from Excel
    analysis_storage = URLAnalysisStorage()
    analyses = analysis_storage.get_user_analyses(username, limit=50)  # Get more records
    
    # Debug: Print what we found
    print(f"✓ Profile accessed by: {username}")
    print(f"  User email: {user.get('email', 'N/A')}")
    print(f"  Number of analyses found: {len(analyses)}")
    if analyses:
        print(f"  Latest analysis: {analyses[0]['url'][:50]}")
    
    return render_template('profile.html', 
                         user=user,
                         analyses=analyses,
                         current_user=username)

# Helper function to get current user from cookie
def get_current_user():
    """Get current user from cookie."""
    username = request.cookies.get('username')
    if username:
        user_storage = UserStorage()
        return user_storage.find_by_username(username)
    return None

# MAIN APPLICATION ROUTES

@app.route('/')
def home():
    """
    Render the home page with the phishing detection interface.
    """
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    API endpoint to predict if a URL is phishing or legitimate.
    
    Expects JSON: {"url": "https://example.com"}
    Returns JSON: {"status": "success/error", "prediction": "safe/phishing", ...}
    """
    
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({
                'status': 'error',
                'message': 'ML model not loaded. Please train the model first.'
            }), 500
        
        # Get URL from request
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No URL provided'
            }), 400
        
        url = data['url'].strip()
        
        # Validate URL
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
        
        # Extract features from URL
        features = extract_features(url)
        
        # Prepare features for prediction (must match training order)
        feature_vector = [[
            features['isIp'],
            features['urlLen'],
            features['is@'],
            features['isredirect'],
            features['haveDash'],
            features['domainLen'],
            features['nosOfSubdomain']
        ]]
        
        # Make prediction
        prediction = model.predict(feature_vector)[0]
        probability = model.predict_proba(feature_vector)[0]
        
        # Prepare response
        result = {
            'status': 'success',
            'url': url,
            'prediction': 'phishing' if prediction == 1 else 'safe',
            'confidence': float(max(probability) * 100),
            'features': features,
            'details': {
                'legitimacy_score': float(probability[0] * 100),
                'phishing_score': float(probability[1] * 100)
            }
        }
        
        # Save analysis to Excel if user is logged in (via cookie)
        username = request.cookies.get('username')
        if username:
            try:
                analysis_storage = URLAnalysisStorage()
                analysis_storage.add_analysis(
                    username=username,
                    url=url,
                    prediction='phishing' if prediction == 1 else 'safe',
                    confidence=float(max(probability) * 100),
                    legitimacy_score=float(probability[0] * 100),
                    phishing_score=float(probability[1] * 100),
                    features=features,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:500]
                )
            except Exception as e:
                print(f"Error saving analysis to Excel: {e}")
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'An error occurred during prediction: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """
    Health check endpoint to verify API is running.
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    }), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    API endpoint for Groq-powered chatbot.
    
    Expects JSON: {"message": "user question"}
    Returns JSON: {"response": "chatbot answer"}
    """
    try:
        # Debug: Log API key status
        print(f"\n[CHAT] Groq API Key configured: {bool(GROQ_API_KEY)}")
        print(f"[CHAT] Groq Client available: {groq_client is not None}")
        
        # Check if Groq API key is configured
        if not GROQ_API_KEY or len(GROQ_API_KEY) < 10 or groq_client is None:
            print("[CHAT] ERROR: API key not configured properly")
            return jsonify({
                'status': 'error',
                'message': 'Groq API key not configured. Please set GROQ_API_KEY environment variable.'
            }), 503
        
        # Get message from request
        data = request.get_json()
        print(f"[CHAT] Received message: {data.get('message', '')[:50]}...")
        
        if not data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No message provided'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Message cannot be empty'
            }), 400
        
        # Create system prompt for phishing detection assistant
        system_prompt = """You are PhishGuard AI Assistant, a helpful security expert specializing in phishing detection and online safety. 
Your role is to:
1. Answer questions about phishing attacks and how to identify them
2. Explain how URL analysis works for detecting malicious websites
3. Provide tips on staying safe online
4. Help users understand security best practices
5. Explain common phishing tactics and red flags

Keep your responses concise, friendly, and informative. Focus on practical security advice.
If asked about specific URLs, recommend using the URL analysis tool for accurate detection."""
        
        # Call Groq API
        print("[CHAT] Calling Groq API...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        bot_response = response.choices[0].message.content.strip()
        print(f"[CHAT] Success! Response length: {len(bot_response)} chars")
        
        return jsonify({
            'status': 'success',
            'response': bot_response
        }), 200
        
    except Exception as e:
        error_type = type(e).__name__
        print(f"[CHAT] Error type: {error_type}")
        print(f"[CHAT] Error details: {e}")
        import traceback
        traceback.print_exc()
        
        # Handle specific errors based on exception type
        if 'AuthenticationError' in error_type or '401' in str(e):
            return jsonify({
                'status': 'error',
                'message': 'Invalid Groq API key. Please check your credentials.'
            }), 401
        elif 'RateLimitError' in error_type or '429' in str(e):
            return jsonify({
                'status': 'error',
                'message': 'API rate limit exceeded. Please try again later.'
            }), 429
        elif 'APIConnectionError' in error_type or 'Connection' in str(e):
            return jsonify({
                'status': 'error',
                'message': 'Cannot connect to Groq API. Check your internet connection.'
            }), 503
        else:
            return jsonify({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }), 500

# MAIN EXECUTION

if __name__ == '__main__':
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print("=" * 60)
        print("⚠ WARNING: Model file not found!")
        print("=" * 60)
        print(f"Expected location: {MODEL_PATH}")
        print("\nPlease run 'python train_model.py' first to train the model.")
        print("=" * 60)
    
    # Run Flask app
    print("\n" + "=" * 60)
    print("PHISHING DETECTOR - FLASK SERVER")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the app at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
