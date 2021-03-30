from django.test import TestCase

# Create your tests here.


class GoodsTest(TestCase):
    def setUp(self) -> None:
        self.data = 1

    def test_fslls(self):
        self.assertTrue(self.data == 1)

    def unit_test(self):
        pass
