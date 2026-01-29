from django.urls import path
from .views import (
    expense_list, expense_detail, analytics, 
    budget_list, budget_detail, budget_status,
    goal_list, goal_detail,
    user_settings
)

urlpatterns = [
    # Expenses
    path('expenses/', expense_list),
    path('expenses/<int:id>/', expense_detail),
    
    # Analytics
    path('analytics/', analytics),
    
    # Budgets
    path('budgets/', budget_list),
    path('budgets/<int:id>/', budget_detail),
    path('budget-status/', budget_status),
    
    # Goals
    path('goals/', goal_list),
    path('goals/<int:id>/', goal_detail),
    
    # Settings
    path('settings/', user_settings),
]
