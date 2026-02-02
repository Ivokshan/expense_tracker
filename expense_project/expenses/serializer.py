from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Expense, UserSalary

class ExpenseSuccessSerializer(serializers.Serializer):
    username = serializers.CharField()
    date = serializers.DateField()
    category = serializers.CharField()
    remaining_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    message = serializers.CharField()

class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    payment_method_name = serializers.CharField(
        source="payment_method.name",
        read_only=True
    )

    remaining_salary = serializers.SerializerMethodField()
    remaining_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "user",
            "amount",
            "category",
            "expense_date",
            "payment_method",        
            "payment_method_name",
            "image",
            "created_at",
            "remaining_salary",
            "remaining_percentage",
        ]
        read_only_fields = ["id", "created_at"]

    def get_remaining_salary(self, obj):
        try:
            salary = obj.user.salary.amount
        except UserSalary.DoesNotExist:
            return None

        month_start = obj.expense_date.replace(day=1)

        spent = (
            Expense.objects.filter(
                user=obj.user,
                expense_date__year=month_start.year,
                expense_date__month=month_start.month
            )
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        return float(salary - spent)

    def get_remaining_percentage(self, obj):
        remaining = self.get_remaining_salary(obj)

        if remaining is None:
            return None

        salary = obj.user.salary.amount

        if salary <= 0:
            return 0

        return round((remaining / float(salary)) * 100, 2)
    
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True
    )
    email = serializers.EmailField(
        required=True,
        allow_null=False,
        allow_blank=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'salary']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data):
        salary_amount = validated_data.pop("salary")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        UserSalary.objects.create(
            user=user,
            amount=salary_amount
        )

        return user
