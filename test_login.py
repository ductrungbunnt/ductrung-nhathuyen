import requests
import json

url = "http://localhost:8000/auth/login"
headers = {
    "Content-Type": "application/json"
}
data = {
    "username": "admin",
    "password": "Ductrung19@"
}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response:", response.text) 