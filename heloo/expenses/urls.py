from django.urls import path
from .views import (
    home, signup_view, login_view, logout_view,
    expense_list, expense_detail, analytics, 
    budget_list, budget_detail, budget_status,
    goal_list, goal_detail, user_settings
)

app_name = 'expenses'

urlpatterns = [
    # Frontend pages & auth
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Expenses API
    path('expenses/', expense_list, name='expense-list'),
    path('expenses/<int:id>/', expense_detail, name='expense-detail'),
    
    # Analytics API
    path('analytics/', analytics, name='analytics'),
    
    # Budgets API
    path('budgets/', budget_list, name='budget-list'),
    path('budgets/<int:id>/', budget_detail, name='budget-detail'),
    path('budget-status/', budget_status, name='budget-status'),
    
    # Goals API
    path('goals/', goal_list, name='goal-list'),
    path('goals/<int:id>/', goal_detail, name='goal-detail'),
    
    # Settings API
    path('settings/', user_settings, name='user-settings'),
]