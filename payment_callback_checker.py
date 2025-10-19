import requests
    
    
    
#https://afraid-sides-follow.loca.lt/payment/callback/?transaction_id=zLdYdWYX1
#https://api.kkiapay.me/api/v1/transactions/zLdYdWYX1/verify

# Verify transaction with KKIAPAY
verify_url = f"https://sandbox-api.kkiapay.me/api/v1/transactions/zLdYdWYX1/verify"
headers = {
    'Accept': 'application/json',
    'X-API-KEY': "tsk_d48fcdb2739911f09c1b2959c8c0e008",
    'X-SECRET-KEY': "tsk_d48fcdb2739911f09c1b2959c8c0e008",
    'X-PRIVATE-KEY': "tpk_d48fcdb1739911f09c1b2959c8c0e008"
}



response = requests.get(verify_url, headers=headers)

print(response)

if response.status_code == 200:
    data = response.json()
    status = data.get('status')
    amount = data.get('amount')
