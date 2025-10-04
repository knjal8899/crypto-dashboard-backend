from unittest.mock import patch
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class TestCoinsApi(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pass12345")
        # login to get token
        resp = self.client.post("/api/auth/login", {"username": "u1", "password": "pass12345"}, format="json")
        self.access = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    @patch("coins.services.fetch_top_coins")
    def test_top_coins(self, mock_fetch):
        mock_fetch.return_value = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 50000},
        ]
        resp = self.client.get("/api/coins/top?limit=1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    @patch("coins.services.fetch_coin_history")
    def test_coin_history(self, mock_hist):
        mock_hist.return_value = {"prices": [[1730000000000, 50000.0]]}
        resp = self.client.get("/api/coins/bitcoin/history?days=1")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) >= 1)

# Create your tests here.
