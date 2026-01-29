from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Expense, Budget, SavingsGoal, UserSettings
from .serializers import ExpenseSerializer, BudgetSerializer, SavingsGoalSerializer, UserSettingsSerializer
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Avg, Q

def home(request):
    return render(request, 'index.html')

# Expense endpoints
@api_view(['GET', 'POST'])
def expense_list(request):
    if request.method == 'GET':
        expenses = Expense.objects.all().order_by('-date')
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            expenses = expenses.filter(category__icontains=category)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def expense_detail(request, id):
    expense = get_object_or_404(Expense, id=id)

    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        expense.delete()
        return Response(status=204)

# Analytics endpoint
@api_view(['GET'])
def analytics(request):
    expenses = Expense.objects.all()
    
    # Date range filter
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    # Overall stats
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    count = expenses.count()
    average = (total / count) if count > 0 else 0
    
    # Category breakdown
    category_breakdown = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Daily breakdown for trend
    daily = expenses.extra(select={'date': 'DATE(date)'}).values('date').annotate(total=Sum('amount')).order_by('date')
    
    # Weekly breakdown
    weekly = {}
    for exp in expenses:
        week = exp.date.isocalendar()[1]
        if week not in weekly:
            weekly[week] = 0
        weekly[week] += exp.amount
    
    return Response({
        'total': total,
        'count': count,
        'average': round(average, 2),
        'category_breakdown': list(category_breakdown),
        'daily_trend': list(daily),
        'weekly_breakdown': weekly
    })

# Budget endpoints
@api_view(['GET', 'POST'])
def budget_list(request):
    if request.method == 'GET':
        budgets = Budget.objects.all()
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def budget_detail(request, id):
    budget = get_object_or_404(Budget, id=id)
    
    if request.method == 'GET':
        serializer = BudgetSerializer(budget)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = BudgetSerializer(budget, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    if request.method == 'DELETE':
        budget.delete()
        return Response(status=204)

@api_view(['GET'])
def budget_status(request):
    budgets = Budget.objects.all()
    budget_status_data = []
    
    for budget in budgets:
        expenses = Expense.objects.filter(category=budget.category)
        spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        remaining = budget.limit - spent
        percentage = (spent / budget.limit * 100) if budget.limit > 0 else 0
        
        budget_status_data.append({
            'id': budget.id,
            'category': budget.category,
            'limit': budget.limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': round(percentage, 2),
            'is_exceeded': spent > budget.limit
        })
    
    return Response(budget_status_data)

# Goals endpoints
@api_view(['GET', 'POST'])
def goal_list(request):
    if request.method == 'GET':
        goals = SavingsGoal.objects.all()
        serializer = SavingsGoalSerializer(goals, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = SavingsGoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def goal_detail(request, id):
    goal = get_object_or_404(SavingsGoal, id=id)
    
    if request.method == 'GET':
        serializer = SavingsGoalSerializer(goal)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = SavingsGoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    if request.method == 'DELETE':
        goal.delete()
        return Response(status=204)

# Settings endpoints
@api_view(['GET', 'PUT'])
def user_settings(request):
    try:
        settings = UserSettings.objects.first()
    except:
        settings = UserSettings.objects.create()
    
    if request.method == 'GET':
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = UserSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
