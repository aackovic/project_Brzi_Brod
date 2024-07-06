# Zlatko Golubović 0089/2021
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Student

class CardNumberAuthBackend(BaseBackend):
    def authenticate(self, request, card_number=None, password=None, **kwargs):
        if card_number is None or password is None:
            return None
        
        try:
            student = Student.objects.get(brojstudkartice=card_number)
        except Student.DoesNotExist:
            return None
        
        if student.idstu.idkor.check_password(password):
            return student.idstu.idkor
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None