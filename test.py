# check_kkiapay_account.py
import requests

def check_kkiapay_account_status():
    """Check if your KKIAPAY account and keys are valid"""
    
    # Your current key
    TEST_KEY = "tsk_d48fcdb2739911f09c1b2959c8c0e008"
    
    # Test different base URLs
    base_urls = [
        "https://api.kkiapay.me",
        "https://api-sandbox.kkiapay.me",  # Sandbox environment
        "https://api.kkiapay.com",
    ]
    
    endpoints = [
        "/api/v1/merchant",
        "/api/v1/transactions/zLdYdWYX1",
        "/v1/merchant",
        "/merchant",
    ]
    
    headers = {
        "Accept": "application/json",
        "X-API-KEY": TEST_KEY,
    }
    
    for base_url in base_urls:
        print(f"\n🔍 Testing base URL: {base_url}")
        
        for endpoint in endpoints:
            url = base_url + endpoint
            print(f"   📡 Trying: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code != 404:
                    print(f"   💡 Different response! Headers: {dict(response.headers)}")
                    print(f"   📝 Body: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    check_kkiapay_account_status()