from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Expense, UserSalary, PaymentMethod

admin.site.unregister(Group)
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'get_username',
        'amount',
        'category',
        'payment_method',
        'expense_date',
        'created_at',
    )
    list_filter = ('category', 'payment_method', 'expense_date', 'created_at')
    search_fields = ('user__username', 'category')

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "User"

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(UserSalary)
class UserSalaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount')
    search_fields = ('user__username',)