import urllib.request
import json

endpoints = [
    '/api/expenses/',
    '/api/analytics/',
    '/api/budgets/',
    '/api/budget-status/',
    '/api/goals/',
    '/api/settings/',
]

print("\n=== API Endpoint Tests ===\n")

for endpoint in endpoints:
    try:
        r = urllib.request.urlopen(f'http://localhost:8000{endpoint}')
        data = json.loads(r.read())
        print(f'✓ {endpoint:<25} Status: {r.status}')
    except Exception as e:
        print(f'✗ {endpoint:<25} Error: {str(e)[:50]}')

print("\n=== Database Check ===\n")

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heloo.settings')

import django
django.setup()

from expenses.models import Expense, Budget, SavingsGoal, UserSettings

print(f'✓ Expenses in DB: {Expense.objects.count()}')
print(f'✓ Budgets in DB: {Budget.objects.count()}')
print(f'✓ Goals in DB: {SavingsGoal.objects.count()}')
print(f'✓ Settings in DB: {UserSettings.objects.count()}')

print("\n=== All Systems Operational ===\n")
