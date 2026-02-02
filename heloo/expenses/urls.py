from django.urls import path
from .views import (
    home, signup_view, login_view, logout_view,
    expense_list, expense_detail, analytics, 
    budget_list, budget_detail, budget_status,
    goal_list, goal_detail, user_settings
)

app_name = 'expenses'

urlpatterns = [
    # ---------------- Frontend pages & Auth ----------------
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ---------------- Expenses API ----------------
    path('api/expenses/', expense_list, name='expense-list'),
    path('api/expenses/<int:id>/', expense_detail, name='expense-detail'),
    
    # ---------------- Analytics API ----------------
    path('api/analytics/', analytics, name='analytics'),
    
    # ---------------- Budgets API ----------------
    path('api/budgets/', budget_list, name='budget-list'),
    path('api/budgets/<int:id>/', budget_detail, name='budget-detail'),
    path('api/budget-status/', budget_status, name='budget-status'),
    
    # ---------------- Goals API ----------------
    path('api/goals/', goal_list, name='goal-list'),
    path('api/goals/<int:id>/', goal_detail, name='goal-detail'),
    
    # ---------------- User Settings API ----------------
    path('api/settings/', user_settings, name='user-settings'),
]