from decouple import config
from requests import request
from fastapi import HTTPException, status

def youverify_kyb(data: dict):
    url = config('YOUVERIFY_API_URL')
    headers = {'Content-Type': 'application/json', 'token': config('YOUVERIFY_API_KEY')}
    payload = {
        "registrationNumber": data.registration_number,
        "isConsent": data.is_consent
    }
    response = request("POST", url, headers=headers, json=payload)
    print(response.json())
    return response.json()

def dojah_kyb(data: dict):
    url = config('DOJAH_API_URL')
    headers = {'Content-Type': 'application/json', 'AppId': config('DOJAH_APP_ID'), 'Authorization': config("DOJAH_API_KEY")}
    payload = {
        "rc_number": data.registration_number,
        "company_type": data.business_name
    }
    response = request("POST", url, headers=headers, json=payload)
    print(response.json())
    return response.json()

def verify_company(user_data: dict) -> dict:
    try:
        main_verification = youverify_kyb(user_data)
        if main_verification.get("success"):
            return main_verification
        backup_verification = dojah_kyb(user_data)
        if backup_verification.get("success"):
            return backup_verification
        else:
            raise Exception("All verification providers failed")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Company verification failed: {str(e)}")
