from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

class ActingUserMixin:
    def get_acting_user(self, request):
        user_id = (
            request.data.get("user_id")
            or request.query_params.get("user_id")
        )

        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError(
                    {"user_id": "User with this ID does not exist"}
                )

        return request.user