import requests


url = 'https://api.customer.io/v1/send/email'

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer APP-API-TOKEN'}

message = {
  "to": "sarah@example.io",
  "transactional_message_id": 3,
  "message_data": {
    "first_name": "Sarah",
    "passwordResetURL": "https://www.example.io/password?token=12345"
  },
  "identifiers": {  
    "id":"1234" 
  }
}

response = requests.post(url, headers=headers, data=message)

# https://backoffice.thekyb.com/