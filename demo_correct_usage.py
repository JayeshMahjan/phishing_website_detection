"""
Demonstration of correct usage after the fix
Shows how to use the phishing detector properly
"""

import requests
import json
from time import sleep

API_URL = "http://127.0.0.1:5000/predict"

def test_url(url, description):
    """Test a URL and display formatted results"""
    print(f"\n{'='*70}")
    print(f"📝 {description}")
    print(f"🔗 URL: {url}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(API_URL, json={"url": url}, timeout=5)
        data = response.json()
        
        if data['status'] == 'success':
            prediction = data['prediction']
            confidence = data['confidence']
            features = data['features']
            
            # Display result with emoji
            if prediction == 'safe':
                print(f"✅ Result: SAFE WEBSITE")
                print(f"🟢 Confidence: {confidence:.2f}%")
            else:
                print(f"⚠️  Result: PHISHING DETECTED")
                print(f"🔴 Confidence: {confidence:.2f}%")
            
            # Show key features
            print(f"\n📊 Key Features:")
            print(f"   • URL Length: {features['urlLen']} chars")
            print(f"   • Domain Length: {features['domainLen']} chars")
            print(f"   • Subdomains: {features['nosOfSubdomain']}")
            print(f"   • Has Dash: {'Yes ⚠️' if features['haveDash'] else 'No ✓'}")
            print(f"   • Is IP Address: {'Yes ⚠️' if features['isIp'] else 'No ✓'}")
            print(f"   • Has @ Symbol: {'Yes ⚠️' if features['is@'] else 'No ✓'}")
            
        else:
            print(f"❌ Error: {data['message']}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure 'python app.py' is running!")
    except Exception as e:
        print(f"❌ Error: {e}")

print("=" * 70)
print("🔐 PHISHING DETECTOR - CORRECT USAGE DEMONSTRATION")
print("=" * 70)
print("\n⚠️  IMPORTANT: Make sure the Flask server is running!")
print("   Run in another terminal: python app.py")
print("\n" + "=" * 70)

# Check if server is running
try:
    response = requests.get("http://127.0.0.1:5000/health", timeout=2)
    print("✅ Server is running and healthy!")
except:
    print("❌ Server is not running. Please start it with: python app.py")
    print("   Then run this script again.")
    exit(1)

print("\n\n" + "#" * 70)
print("# CORRECT WAY: Use FULL URLs with paths")
print("#" * 70)

print("\n\n🟢 Testing LEGITIMATE websites (with paths):")
print("-" * 70)

test_url(
    "https://www.google.com/search?q=python+programming",
    "Google Search - Popular legitimate site"
)
sleep(0.5)

test_url(
    "https://github.com/explore/trending",
    "GitHub Explore - Developer platform"
)
sleep(0.5)

test_url(
    "https://stackoverflow.com/questions/tagged/python",
    "Stack Overflow - Q&A platform"
)
sleep(0.5)

test_url(
    "https://www.amazon.com/s?k=laptops",
    "Amazon Search - E-commerce site"
)

print("\n\n🔴 Testing SUSPICIOUS patterns:")
print("-" * 70)

test_url(
    "http://192.168.1.1/admin/login.php",
    "IP Address - Often used by phishing"
)
sleep(0.5)

test_url(
    "https://paypal-security-update.suspicious-domain.com/verify.php",
    "Suspicious Domain - Multiple red flags"
)
sleep(0.5)

test_url(
    "http://secure-login.bank-account.verify-now.com/update.html",
    "Multiple Subdomains - Phishing pattern"
)

print("\n\n" + "#" * 70)
print("# INCORRECT WAY: Domain-only URLs (may not work well)")
print("#" * 70)
print("\n⚠️  These might be incorrectly flagged due to model limitations:")
print("-" * 70)

test_url(
    "https://google.com",
    "Google (no path) - Too short, model may flag as phishing"
)
sleep(0.5)

test_url(
    "https://github.com",
    "GitHub (no path) - Too short, model may flag as phishing"
)

print("\n\n" + "=" * 70)
print("📚 KEY LEARNINGS:")
print("=" * 70)
print("""
1. ✅ ALWAYS use complete URLs with paths for accurate results
   Example: https://example.com/page/file.html

2. ❌ AVOID testing with domain-only URLs
   Example: https://example.com (too short, may be misclassified)

3. 📊 The model relies heavily on URL length (51.8% importance)
   - Legitimate URLs in dataset: 35-50+ characters
   - Short URLs (<25 chars) may be flagged as phishing

4. 🎯 For best results, test URLs as they appear in real scenarios:
   - With paths: /search, /products, /login, etc.
   - With parameters: ?q=test, ?id=123, etc.

5. 🚀 This is a demonstration project showing ML deployment
   - Real-world phishing detection needs more sophisticated features
   - Consider: SSL certificates, WHOIS data, content analysis, etc.
""")

print("=" * 70)
print("🎉 DEMONSTRATION COMPLETE!")
print("=" * 70)
print("\n💡 TIP: Open http://127.0.0.1:5000 in your browser for the web interface!")
