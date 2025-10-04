from unittest.mock import patch
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class TestQaApi(APITestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(username="u2", password="pass12345")
        resp = self.client.post("/api/auth/login", {"username": "u2", "password": "pass12345"}, format="json")
        self.access = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    @patch("coins.services.fetch_coin_market_by_id")
    def test_price_question(self, mock_price):
        mock_price.return_value = {"current_price": 123.45}
        resp = self.client.get("/api/chat/query?text=What%20is%20the%20price%20of%20Bitcoin%3F")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("price_usd", resp.data)

    @patch("coins.services.fetch_coin_history")
    def test_trend_question(self, mock_hist):
        mock_hist.return_value = {"prices": [[1730000000000, 100.0]]}
        resp = self.client.get("/api/chat/query?text=Show%20me%20the%207-day%20trend%20of%20Ethereum")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("prices", resp.data)

# Create your tests here.
