import requests
import json

AVAILABLE_COUNTRIES_LISTING_URL = 'https://api.thekyb.com/api/readKycCountries'

AVAILABLE_LANGUAGES_LISTING_URL = 'https://api.thekyb.com/api/readKycLanguages'

SEARCH_DOCUMENTATION_URL = 'https://api.thekyb.com/api/search'

READ_KYC_DETAIL = 'https://api.thekyb.com/api/readKycResponse?kyc_request_id=KYC_REQUEST_ID'

#################URLS####################################
# Business Information
ALL_QUESTIONS_URL = 'https://api.thekyb.com/api/getAllQuestionnaires'
CREATE_QUESTIONNAIRE_URL = 'https://api.thekyb.com/api/createQuestionnaireUrl?questionnaire_id=QUESTIONNAIRE_ID&ttl=60'
QUESTIONNAIRE_SUBMISSION_URL = 'https://api.thekyb.com/api/search'
SERVICE_DETAILS_URL = 'https://api.thekyb.com/api/readServiceDetail?service_id=SERVICE_ID'
QUESTIONNAIRE_RESPONSE_URL = 'https://api.thekyb.com/api/readQuestionnaireResponse?questionnaire_request_id=QUESTIONNAIRE_REQUEST_ID'
OCR_RESPONSE_URL = 'https://api.thekyb.com/api/readOcrResponse?ocr_request_id=OCR_REQUEST_ID'
# KYB Check
AVAILABLE_COUNTRIES_LISTING_KYB_URL = 'https://api.thekyb.com/api/countries/read'
RETRIEVE_COMPANIES_PROFILES = 'https://api.thekyb.com/api/readKybResponse?request_id=REQUEST_ID&page=PAGE&limit=LIMIT'
ENHANCED_COMPANY_PROFILE = 'https://api.thekyb.com/api/companies/read?company_id=COMPANY_ID&request_id=REQUEST_ID'
AML_FOR_COMPANY = 'https://api.thekyb.com/api/performCompanyAml'
AML_FOR_PERSON = 'https://api.thekyb.com/api/performOfficersAml'

# Others
GET_COUNTRY_PAID_DOCUMENTS = 'https://api.thekyb.com/api/getCountryPaidDocuments'
BUY_DOCUMENTS = 'https://api.thekyb.com/api/buyDocuments'
# Document Based KYB
questionnaire_submission_payload = {
  
}

payload={}
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'token': 'WMSEVUo8QbuBwz9GjjL5t0amKPzSstS4t05zPF7fOswBAnOZs0pAN0NG5phtEnCWhkqAUqDHTpbIyO1UIeSKtCwhNuWg7jLgi3PpnE19MGATCneFUfk6gXWQ1725762521'
}

response = requests.request("GET", AVAILABLE_COUNTRIES_LISTING_URL, headers=headers, data=payload)

print(response.text)

"""

Get All Questionnaires
Create Questionnaire Url
Get All Questions
Questionnaire Submission
Read Service Detail
Read Questionnaire Response
Read OCR Response

"""


import requests
import json

url = "https://api.thekyb.com/api/search"

payload = json.dumps({
  "search": "Testing company",
  "country_names": [
    "united_kingdom"
  ],
  "search_type": "start_with",
  "services": [
    "kyb_check"
  ],
  "ttl": 120
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'token': 'YOUR_SECRET_KEY'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
