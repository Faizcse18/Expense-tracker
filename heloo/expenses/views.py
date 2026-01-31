# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense, Budget, SavingsGoal, UserSettings
from .serializers import ExpenseSerializer, BudgetSerializer, SavingsGoalSerializer, UserSettingsSerializer
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm  # Custom form with email
from django.contrib.auth.decorators import login_required



# ----------------- Frontend Home -----------------
@login_required(login_url= 'expenses:login')
def home(request):
    return render(request, 'index.html')


# ----------------- Auth Views -----------------
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can log in now.")
            return redirect('expenses:login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('expenses:home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('expenses:login')


# ----------------- Expenses -----------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expense_list(request):
    if request.method == 'GET':
        expenses = Expense.objects.filter(user=request.user).order_by('-date')

        category = request.query_params.get('category')
        if category:
            expenses = expenses.filter(category__icontains=category)

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
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)

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


# ----------------- Analytics -----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics(request):
    expenses = Expense.objects.filter(user=request.user)

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    count = expenses.count()
    average = (total / count) if count > 0 else 0

    category_breakdown = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    daily = expenses.extra(select={'date': 'DATE(date)'}).values('date').annotate(total=Sum('amount')).order_by('date')

    weekly = {}
    for exp in expenses:
        week = exp.date.isocalendar()[1]
        weekly[week] = weekly.get(week, 0) + exp.amount

    return Response({
        'total': total,
        'count': count,
        'average': round(average, 2),
        'category_breakdown': list(category_breakdown),
        'daily_trend': list(daily),
        'weekly_breakdown': weekly
    })


# ----------------- Budget -----------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def budget_list(request):
    if request.method == 'GET':
        budgets = Budget.objects.filter(user=request.user)
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def budget_detail(request, id):
    budget = get_object_or_404(Budget, id=id, user=request.user)

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
@permission_classes([IsAuthenticated])
def budget_status(request):
    budgets = Budget.objects.filter(user=request.user)
    budget_status_data = []

    for budget in budgets:
        expenses = Expense.objects.filter(user=request.user, category=budget.category)
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


# ----------------- Savings Goals -----------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def goal_list(request):
    if request.method == 'GET':
        goals = SavingsGoal.objects.filter(user=request.user)
        serializer = SavingsGoalSerializer(goals, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = SavingsGoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def goal_detail(request, id):
    goal = get_object_or_404(SavingsGoal, id=id, user=request.user)

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


# ----------------- User Settings -----------------
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = UserSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)