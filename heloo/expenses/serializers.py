from rest_framework import serializers
from .models import Expense, Budget, SavingsGoal, UserSettings

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'notes', 'date', 'is_recurring', 'recurring_frequency', 'currency']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'limit', 'period', 'currency']

class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = ['id', 'name', 'target_amount', 'current_amount', 'deadline', 'currency']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['id', 'currency', 'theme']