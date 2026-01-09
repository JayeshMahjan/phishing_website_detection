"""
Quick test to verify feature extraction matches training data format
"""

from urllib.parse import urlparse
import re

def extract_features(url):
    """Extract features matching the dataset format"""
    features = {}
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        # Feature extraction
        ip_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        features['isIp'] = 1 if ip_pattern.search(domain) else 0
        
        # Build the full URL without protocol
        url_without_protocol = domain + path
        if query:
            url_without_protocol += '?' + query
        
        features['urlLen'] = len(url_without_protocol)  # FULL URL length
        features['is@'] = 1 if '@' in url else 0
        
        # Check for // in path/query only (not protocol)
        path_and_query = path + '?' + query if query else path
        features['isredirect'] = 1 if '//' in path_and_query else 0
        
        features['haveDash'] = 1 if '-' in domain else 0
        features['domainLen'] = len(domain)
        features['nosOfSubdomain'] = domain.count('.') if domain else 0
        
        return features
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test with legitimate websites
print("Testing LEGITIMATE websites:")
print("=" * 60)

test_urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://amazon.com"
]

for url in test_urls:
    features = extract_features(url)
    print(f"\nURL: {url}")
    print(f"Domain: {urlparse(url).netloc}")
    print(f"Features: {features}")

print("\n\n" + "=" * 60)
print("Testing SUSPICIOUS patterns:")
print("=" * 60)

suspicious_urls = [
    "http://192.168.1.1/login",
    "https://paypal-secure-login.suspicious.com",
    "http://amazon@fake-site.com",
    "https://login.secure.bank-account.verify.com"
]

for url in suspicious_urls:
    features = extract_features(url)
    print(f"\nURL: {url}")
    print(f"Domain: {urlparse(url).netloc}")
    print(f"Features: {features}")

print("\n\n" + "=" * 60)
print("Comparison with dataset example:")
print("=" * 60)
print("Dataset row: www.voting-yahoo.com")
print("Expected: urlLen=20, isIp=0, is@=0, isredirect=0, haveDash=1, domainLen=20, nosOfSubdomain=2")

url_test = "https://www.voting-yahoo.com"
features = extract_features(url_test)
print(f"\nExtracted from '{url_test}':")
print(f"urlLen={features['urlLen']}, isIp={features['isIp']}, is@={features['is@']}, "
      f"isredirect={features['isredirect']}, haveDash={features['haveDash']}, "
      f"domainLen={features['domainLen']}, nosOfSubdomain={features['nosOfSubdomain']}")

if (features['urlLen'] == 20 and features['haveDash'] == 1 and 
    features['domainLen'] == 20 and features['nosOfSubdomain'] == 2):
    print("\n✅ FEATURE EXTRACTION MATCHES DATASET FORMAT!")
else:
    print("\n❌ MISMATCH DETECTED - Need to adjust extraction logic")
