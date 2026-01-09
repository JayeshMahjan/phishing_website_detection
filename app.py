"""
Phishing Website Detection - Flask Backend
===========================================
This Flask application provides a REST API for phishing detection.
It extracts features from URLs and uses a trained ML model for prediction.
"""

from flask import Flask, render_template, request, jsonify
import joblib
import re
from urllib.parse import urlparse
import os

# ===============================================
# FLASK APP INITIALIZATION
# ===============================================
app = Flask(__name__)

# Load the trained ML model
MODEL_PATH = 'model/phishing_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None

# ===============================================
# FEATURE EXTRACTION FUNCTIONS
# ===============================================

def extract_features(url):
    """
    Extract security features from a URL for phishing detection.
    
    IMPORTANT: Features must match the training dataset format!
    - urlLen is the FULL URL length (domain + path + query)
    - domainLen is just the domain length
    - isredirect checks for // in PATH only (not protocol)
    
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


# ===============================================
# FLASK ROUTES
# ===============================================

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


# ===============================================
# MAIN EXECUTION
# ===============================================

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
