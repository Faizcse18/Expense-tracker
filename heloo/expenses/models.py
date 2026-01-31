from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= False)
    CURRENCY_CHOICES = [
        ('INR', '₹ Indian Rupee'),
        ('USD', '$ US Dollar'),
        ('EUR', '€ Euro'),
        ('GBP', '£ British Pound'),
    ]
    
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20, 
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        blank=True,
        null=True
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')

    def __str__(self):
        return f"{self.category} - {self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= False)
    category = models.CharField(max_length=100)
    limit = models.FloatField()
    period = models.CharField(
        max_length=20, 
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'
    )
    currency = models.CharField(max_length=3, choices=Expense.CURRENCY_CHOICES, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.limit}"

class SavingsGoal(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= False)
    name = models.CharField(max_length=100)
    target_amount = models.FloatField()
    current_amount = models.FloatField(default=0)
    deadline = models.DateField()
    currency = models.CharField(max_length=3, choices=Expense.CURRENCY_CHOICES, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank= False)
    currency = models.CharField(max_length=3, choices=Expense.CURRENCY_CHOICES, default='INR')
    theme = models.CharField(max_length=20, choices=[('dark', 'Dark'), ('light', 'Light')], default='dark')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)