import requests
import sys

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJyb2xlIjoic3VwZXJfYWRtaW4iLCJleHAiOjE3ODM3NzI0OTh9._Y-nTRsWmDnDLyyJ_jxyaoUWZP29c8o5O2QJ3JqC_8A"

def test():
    try:
        url = "http://127.0.0.1:8000/admin/users/1/edit"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "age": 25,
            "gender": "Male",
            "homeAddress": "123 Test St"
        }
        r = requests.put(url, headers=headers, json=payload)
        print("Status:", r.status_code)
        print("Response:", r.text)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test()
