from django.db import models
from django.conf import settings
from django.utils.timezone import now

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("food", "Food"),
        ("grocery", "Grocery"),
        ("travel", "Travel"),
        ("rent", "Rent"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="expenses"
    )

    expense_date = models.DateField(default=now)

    image = models.ImageField(
        upload_to="image/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    
class UserSalary(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount}"