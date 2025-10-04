from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class TestAuth(APITestCase):
    def test_register_login_me(self):
        # register
        url = "/api/auth/register"
        payload = {"username": "tester", "email": "t@example.com", "password": "StrongPass123!"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

        # login
        url = "/api/auth/login"
        resp = self.client.post(url, {"username": "tester", "password": "StrongPass123!"}, format="json")
        self.assertEqual(resp.status_code, 200)
        access = resp.data.get("access")
        self.assertTrue(access)

        # me
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("username"), "tester")

# Create your tests here.
