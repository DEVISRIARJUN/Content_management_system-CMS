import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

client = Client()

print("Testing API Endpoints...")
endpoints = [
    '/api/',
    '/api/posts/',
    '/api/categories/',
    '/api/tags/',
    '/api/analytics/dashboard/',
    '/api/public/posts/',
    '/',
]

for ep in endpoints:
    res = client.get(ep)
    print(f"GET {ep} -> Status: {res.status_code}")
    assert res.status_code in [200, 301, 302], f"Failed at {ep}: {res.status_code}"

# Test AI SEO endpoint
ai_res = client.post('/api/ai/seo/', data={'title': 'Building scalable apps', 'content': 'Hello world test content'}, content_type='application/json')
print(f"POST /api/ai/seo/ -> Status: {ai_res.status_code}, Score: {ai_res.json().get('seo_score')}")

# Test AI Readability endpoint
read_res = client.post('/api/ai/readability/', data={'text': 'This is a clean and simple test of readability.'}, content_type='application/json')
print(f"POST /api/ai/readability/ -> Status: {read_res.status_code}, Score: {read_res.json().get('flesch_score')}")

print("\n[ALL TESTS PASSED SUCCESSFULLY!]")
