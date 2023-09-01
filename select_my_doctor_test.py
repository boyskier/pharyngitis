import requests
import json

url = "http://localhost:5000/give_doctor_permission"  # Replace with your actual server URL

data = {
    "patient_id": "patient2",
    "doctor_id": "이경언"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", json.loads(response.text))
