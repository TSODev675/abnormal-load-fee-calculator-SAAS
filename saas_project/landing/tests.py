from django.test import TestCase
from .calculations import calculate_fees

class FeeCalculationTest(TestCase):

    def test_standard_load(self):
        data = {
            'actual_mass': 18000,
            'total_distance': 500,
            'distance_escorted': 100,
            'engineer_fee': True
        }
        result = calculate_fees(data)
        self.assertEqual(result['total_fee'], 1440.00)

    def test_oversized_load(self):
        data = {
            'actual_mass': 32000,
            'total_distance': 1200,
            'distance_escorted': 500,
            'engineer_fee': True
        }
        result = calculate_fees(data)
        self.assertEqual(result['total_fee'], 2460.00)

    def test_lightweight_load(self):
        data = {
            'actual_mass': 14000,
            'total_distance': 200,
            'distance_escorted': 50,
            'engineer_fee': False
        }
        result = calculate_fees(data)
        self.assertEqual(result['total_fee'], 915.00)
