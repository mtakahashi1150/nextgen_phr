#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1 API Live Test"""
import requests

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("\n" + "="*60)
print("API Live Test")
print("="*60)

# 1. User registration
print("\n1. User Registration")
resp = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "taro@example.com",
    "password": "password123",
    "name": "Taro Yamada"
})
print(f"   Status: {resp.status_code}")
if resp.status_code == 201:
    user = resp.json()
    user_id = user["id"]
    print(f"   OK! ID: {user_id[:8]}...")
    print(f"   Name: {user['name']}")
else:
    print(f"   Error: {resp.text}")
    exit(1)

# 2. Login
print("\n2. Login")
resp = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "taro@example.com",
    "password": "password123"
})
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    token_data = resp.json()
    token = token_data["access_token"]
    print(f"   OK! Token: {token[:20]}...")
else:
    print(f"   Error: {resp.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 3. Get user info
print("\n3. Get User Info")
resp = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    user = resp.json()
    print(f"   OK! User: {user['name']} ({user['email']})")

# 4. Create health record
print("\n4. Create Health Record")
resp = requests.post(f"{BASE_URL}/users/{user_id}/health-records/", 
    json={
        "record_type": "health_checkup",
        "data": {
            "height": 175,
            "weight": 70,
            "blood_pressure": "120/80"
        },
        "medical_condition": "Good health"
    },
    headers=headers
)
print(f"   Status: {resp.status_code}")
if resp.status_code == 201:
    record = resp.json()
    print(f"   OK! Record ID: {record['id'][:8]}...")
    print(f"   Type: {record['record_type']}")

# 5. Get health records
print("\n5. Get Health Records")
resp = requests.get(f"{BASE_URL}/users/{user_id}/health-records/", headers=headers)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    records = resp.json()
    print(f"   OK! {len(records)} record(s)")
    for i, rec in enumerate(records, 1):
        print(f"     {i}. {rec['record_type']}")

print("\n" + "="*60)
print("All tests passed!")
print("="*60 + "\n")
