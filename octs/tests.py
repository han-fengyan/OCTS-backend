from django.test import TestCase

# Create your tests here.


class MyTest(TestCase):
    def setUp(self) -> None:
        self.data = 1

    def test_fslls(self):
        self.assertTrue(self.data == 1)
