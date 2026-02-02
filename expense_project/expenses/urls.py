from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (ExpenseViewSet, RegisterUserView, ExpenseSummaryView, MonthlyExpenseSummaryView)

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('expenses/summary/<int:user_id>/', ExpenseSummaryView.as_view(), name='expense-summary'),
    path('expenses/summary/monthly/', MonthlyExpenseSummaryView.as_view(), name='monthly-expense-summary'),
]

urlpatterns += router.urls