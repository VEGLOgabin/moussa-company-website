

import requests
import json

def verify_kkiapay_transaction(transaction_id):
    """
    Verify a Kkiapay transaction using the correct API endpoint.
    """
    # Correct endpoint - use this one
    verify_url = "https://api.kkiapay.me/api/v1/transactions/verify"
    
    # Your secret key
    KKIAPAY_SECRET_KEY = "tsk_d48fcdb2739911f09c1b2959c8c0e008"
    
    headers = {
        "Accept": "application/json",
        "X-API-KEY": KKIAPAY_SECRET_KEY,
        "X-SECRET-KEY": KKIAPAY_SECRET_KEY,
        "X-PRIVATE-KEY": "your_private_key_here"  # Add if you have it
    }
    
    # For GET request with transaction_id in URL
    get_url = f"https://api.kkiapay.me/api/v1/transactions/{transaction_id}/verify"
    
    try:
        # Method 1: GET request (recommended)
        print("🔄 Trying GET method...")
        response = requests.get(get_url, headers=headers)
        
        print(f"🔹 GET Status Code: {response.status_code}")
        print(f"🔹 GET Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GET Request Successful!")
            print(json.dumps(data, indent=2))
            return data
        
        # Method 2: POST request (alternative)
        print("🔄 GET failed, trying POST method...")
        post_url = "https://api.kkiapay.me/api/v1/transactions/status"
        payload = {
            "transactionId": transaction_id
        }
        
        response = requests.post(post_url, headers=headers, json=payload)
        print(f"🔹 POST Status Code: {response.status_code}")
        print(f"🔹 POST Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ POST Request Successful!")
            print(json.dumps(data, indent=2))
            return data
            
        print("❌ Both GET and POST methods failed")
        return None

    except Exception as e:
        print(f"❌ Error verifying transaction: {e}")
        return None

# Test with your transaction ID
verify_kkiapay_transaction("zLdYdWYX1")
















# import requests
# import json

# def verify_kkiapay_transaction(transaction_id):
#     """
#     Verify a Kkiapay transaction using the new API format.
#     """

#     verify_url = "https://api.kkiapay.me/v1/transactions/verify"  # Correct endpoint

#     # Use your real keys here (Secret key only)
#     KKIAPAY_SECRET_KEY = "tsk_d48fcdb2739911f09c1b2959c8c0e008"

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {KKIAPAY_SECRET_KEY}",  # Bearer token auth
#     }

#     payload = {
#         "transactionId": transaction_id  # Send in request body
#     }

#     try:
#         response = requests.post(verify_url, headers=headers, json=payload)

#         print(f"🔹 Status Code: {response.status_code}")
#         print("🔹 Raw Response Text:")
#         print(response.text)

#         # If valid JSON response
#         if response.status_code == 200:
#             data = response.json()
#             print("🔹 Parsed JSON:")
#             print(json.dumps(data, indent=4))

#             if data.get("status") == "success":
#                 print(f"✅ Transaction {transaction_id} verified successfully.")
#                 print(f"Amount: {data.get('amount')}")
#             else:
#                 print(f"⚠️ Verification failed: {data.get('message', 'Unknown error')}")

#         else:
#             print("❌ API request failed. Response code:", response.status_code)

#     except Exception as e:
#         print("❌ Error verifying transaction:", e)


# # Example usage
# verify_kkiapay_transaction("zLdYdWYX1")




























# import requests
    
    
    

# #https://app.kkiapay.me/api/v1/transactions/zLdYdWYX1/verify

# # Verify transaction with KKIAPAY
# verify_url = f"https://app.kkiapay.me/api/v1/transactions/zLdYdWYX1/verify"
# headers = {
#     'Accept': 'application/json',
#     'X-API-KEY': "tsk_d48fcdb2739911f09c1b2959c8c0e008",
#     'X-SECRET-KEY': "tsk_d48fcdb2739911f09c1b2959c8c0e008",
#     'X-PRIVATE-KEY': "tpk_d48fcdb1739911f09c1b2959c8c0e008"
# }



# response = requests.get(verify_url, headers=headers)

# print(response)

# if response.status_code == 200:
#     data = response.json()
#     status = data.get('status')
#     amount = data.get('amount')



# # ------------------------------------------------------------------------------
# import requests

# import json

# def handle_payment_verification(transaction_id):
#     # Use live API (sandbox no longer works)
#     verify_url = f"https://app.kkiapay.me/api/v1/transactions/{transaction_id}/verify"
#     "https://app.kkiapay.me/dashboard/transactions/"
#     # headers = {
#     #     "Accept": "application/json",
#     #     "X-API-KEY": "your_live_api_key",
#     #     "X-SECRET-KEY": "your_live_secret_key",
#     #     "X-PRIVATE-KEY": "your_live_private_key",
#     # }
    
    
    
    
#     KKIAPAY_PRIVATE_KEY = "tpk_d48fcdb1739911f09c1b2959c8c0e008"
#     KKIAPAY_SECRET_KEY = "tsk_d48fcdb2739911f09c1b2959c8c0e008"
#     KKIAPAY_PUBLIC_KEY = "d48fa6a0739911f09c1b2959c8c0e008"


    
#     headers = {
#         "Accept": "application/json",
#         "X-API-KEY": KKIAPAY_PUBLIC_KEY,
#         "X-SECRET-KEY": KKIAPAY_SECRET_KEY,
#         "X-PRIVATE-KEY": KKIAPAY_PRIVATE_KEY,
#     }

#     try:
#         response = requests.get(verify_url, headers=headers)
#         print(f"🔹 Kkiapay verification response status: {response.status_code}")

#         # Print everything returned by the API
#         print("🔹 Full response text:")
#         print(response.text)

#         if response.status_code == 200:
#             data = response.json()
#             print("🔹 Parsed JSON response:")
#             print(json.dumps(data, indent=4))  # Pretty print JSON

#             # Example fields
#             status = data.get("status")
#             amount = data.get("amount")
#             reason = data.get("reason")
#             print(f"✅ Payment status: {status}, Amount: {amount}, Reason: {reason}")

#             # TODO: Save payment status in your DB, etc.

#             # Example redirect after success
#             print(data)

#         else:
#             print("⚠️ Kkiapay verification failed with status")


#     except Exception as e:
#         print("❌ Error verifying payment:", e)



# handle_payment_verification("zLdYdWYX1")