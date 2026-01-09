"""
Test the Flask API to verify predictions are working correctly
"""
import requests
import json

API_URL = "http://127.0.0.1:5000/predict"

def test_url(url, expected_type):
    """Test a URL and display results"""
    print(f"\nTesting: {url}")
    print(f"Expected: {expected_type}")
    print("-" * 60)
    
    try:
        response = requests.post(API_URL, json={"url": url})
        data = response.json()
        
        if data['status'] == 'success':
            prediction = data['prediction']
            confidence = data['confidence']
            features = data['features']
            
            print(f"Prediction: {prediction.upper()}")
            print(f"Confidence: {confidence:.2f}%")
            print(f"Features: {features}")
            
            # Check if prediction matches expectation
            if prediction == expected_type.lower():
                print("✅ CORRECT PREDICTION!")
            else:
                print("❌ WRONG PREDICTION!")
        else:
            print(f"Error: {data['message']}")
    except Exception as e:
        print(f"Error: {e}")

print("=" * 60)
print("TESTING PHISHING DETECTOR API")
print("=" * 60)

# Test legitimate websites
print("\n\n🟢 TESTING LEGITIMATE WEBSITES:")
print("=" * 60)
test_url("https://google.com", "safe")
test_url("https://github.com", "safe")
test_url("https://microsoft.com", "safe")
test_url("https://amazon.com", "safe")

# Test suspicious patterns
print("\n\n🔴 TESTING SUSPICIOUS PATTERNS:")
print("=" * 60)
test_url("http://192.168.1.1/login", "should_be_detected")
test_url("https://paypal-secure-login.suspicious.com", "might_be_phishing")
test_url("https://login.secure.bank-account.verify.com", "might_be_phishing")

print("\n\n" + "=" * 60)
print("TESTING COMPLETE!")
print("=" * 60)
print("\nNote: The model may not catch all phishing patterns.")
print("It depends on the training data distribution.")
print("Focus on checking if legitimate sites are marked as SAFE.")
