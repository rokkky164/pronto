import requests
import json

AVAILABLE_COUNTRIES_LISTING_URL = 'https://api.thekyb.com/api/readKycCountries'

AVAILABLE_LANGUAGES_LISTING_URL = 'https://api.thekyb.com/api/readKycLanguages'

SEARCH_DOCUMENTATION_URL = 'https://api.thekyb.com/api/search'

READ_KYC_DETAIL = 'https://api.thekyb.com/api/readKycResponse?kyc_request_id=KYC_REQUEST_ID'


payload={}
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'token': 'YOUR_SECRET_KEY'
}

response = requests.request("GET", AVAILABLE_COUNTRIES_LISTING_URL, headers=headers, data=payload)

print(response.text)