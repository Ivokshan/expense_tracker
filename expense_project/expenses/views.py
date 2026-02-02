from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ExpenseSerializer, UserRegisterSerializer, ExpenseSuccessSerializer
from django.db.models import Sum, Avg
from django.db.models.functions import TruncMonth
from rest_framework.exceptions import ValidationError
from datetime import date
from .models import UserSalary, Expense
from .base import ActingUserMixin
from django.contrib.auth.models import User 

class ExpenseViewSet(ActingUserMixin, ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.get_acting_user(self.request)
        return Expense.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.get_acting_user(self.request)

        amount = serializer.validated_data["amount"]
        expense_date = serializer.validated_data.get("expense_date", date.today())
        month_start = expense_date.replace(day=1)

        try:
            salary = user.salary.amount
        except UserSalary.DoesNotExist:
            raise ValidationError({
                "error": "Salary not set for this user. Please contact admin."
            })

        monthly_spent = (
            Expense.objects.filter(
                user=user,
                expense_date__year=month_start.year,
                expense_date__month=month_start.month
            )
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        if monthly_spent + amount > salary:
            raise ValidationError({
                "error": "Expense exceeds monthly salary limit"
            })

        expense = serializer.save(user=user)

        remaining = salary - (monthly_spent + amount)

        self.success_response = {
            "username": expense.user.username,
            "date": expense.expense_date,
            "category": expense.category,
            "remaining_amount": remaining,
            "message": "Payment made successfully"
        }

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            ExpenseSuccessSerializer(self.success_response).data,
            status=status.HTTP_201_CREATED
        )
    
class RegisterUserView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"user_id": "User does not exist"})

        expenses = Expense.objects.filter(user=user)

        category_summary = (
            expenses.values("category")
            .annotate(total=Sum("amount"))
        )

        categories = {i["category"]: i["total"] for i in category_summary}

        monthly_totals = (
            expenses
            .annotate(month=TruncMonth("expense_date"))
            .values("month")
            .annotate(month_total=Sum("amount"))
        )

        monthly_average = (
            monthly_totals.aggregate(avg=Avg("month_total"))["avg"] or 0
        )

        try:
            salary = user.salary.amount
        except UserSalary.DoesNotExist:
            salary = None

        today = date.today()
        month_start = today.replace(day=1)

        spent_this_month = (
            expenses.filter(
                expense_date__year=month_start.year,
                expense_date__month=month_start.month
            )
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        if salary:
            remaining_salary = salary - spent_this_month
            remaining_percentage = round(
                (remaining_salary / salary) * 100, 2
            )
        else:
            remaining_salary = None
            remaining_percentage = None

        return Response({
            "user_id": user.id,
            "user_name": user.username,
            "categories": categories,
            "monthly_average": monthly_average,
            "salary": salary,
            "remaining_salary": remaining_salary,
            "remaining_salary_percentage": remaining_percentage
        })

class MonthlyExpenseSummaryView(ActingUserMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.get_acting_user(request)
        expenses = Expense.objects.filter(user=user)

        monthly_summary = (
            expenses
            .annotate(month=TruncMonth('expense_date'))
            .values('month')
            .annotate(total_spent=Sum('amount'))
            .order_by('month')
        )

        if not monthly_summary.exists():
            return Response(
                {"message": "No expense data available"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "monthly_summary": list(monthly_summary)
        })