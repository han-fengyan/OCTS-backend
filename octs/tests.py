from django.test import TestCase
from .models import User
# Create your tests here.


class MyTest(TestCase):
    def setUp(self) -> None:
        self.data = 1
        alice = User.objects.create(name="Alice",password = "123456")
        bob = User.objects.create(name = "Bob", password = "123456")
    def test_add_new_user(self):
        pass
