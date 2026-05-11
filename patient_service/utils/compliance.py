from decouple import config
from requests import request
from fastapi import HTTPException, status
from .logger import logger

def youverify_kyb(data: dict):
    url = config('YOUVERIFY_API_URL')
    headers = {'Content-Type': 'application/json', 'token': config('YOUVERIFY_API_KEY')}
    payload = {
        "registrationNumber": f"RC{data.registration_number}",
        "isConsent": data.is_consent
    }
    try:
        response = request("POST", url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"YouVerify API error: {str(e)}")
        raise

def dojah_kyb(data: dict):
    url = config('DOJAH_API_URL')
    headers = {'Content-Type': 'application/json', 'AppId': config('DOJAH_APP_ID'), 'Authorization': config("DOJAH_API_KEY")}
    payload = {
        "rc_number": data.registration_number,
        "company_type": data.business_name
    }
    try:
        response = request("GET", url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Dojah API error: {str(e)}")
        raise

def verify_company(user_data: dict) -> dict:
    try:
        main_verification = youverify_kyb(user_data)
        if main_verification.get("success") is False:
            logger.error("YouVerify verification failed, trying Dojah backup")
            raise Exception("YouVerify verification failed")
        if main_verification.get("data", {}).get("companyStatus") == "ACTIVE":
            logger.info(f"{main_verification.get('data', {}).get('name')} is active according to YouVerify")
            return {"success": True, "provider": "YouVerify"}
        else:
            logger.error(f"{main_verification.get('data', {}).get('name')} is not active according to YouVerify")
            return {"success": False, "provider": "YouVerify"}
    except Exception:
        try:
            backup_verification = dojah_kyb(user_data)
            if backup_verification.get("entity", {}).get("status") == "Active":
                logger.info(f"{backup_verification.get('entity', {}).get('company_name')} is active according to Dojah")
                return {"success": True, "provider": "Dojah"}
            else:
                logger.error(f"{backup_verification.get('entity', {}).get('company_name')} is not active according to Dojah")
                return {"success": False, "provider": "Dojah"}
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Verification service is currently unavailable, please try again later.")
