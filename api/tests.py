from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company, KBEntry, QueryLog


class TeamBoardAPITests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="clientco",
            password="securepass123",
            email="client@example.com",
        )
        self.client_user.company.company_name = "Client Co"
        self.client_user.company.save(update_fields=["company_name"])

        self.admin_user = User.objects.create_user(
            username="adminco",
            password="securepass123",
            email="admin@example.com",
        )
        self.admin_user.company.company_name = "Admin Co"
        self.admin_user.company.role = Company.Role.ADMIN
        self.admin_user.company.save(update_fields=["company_name", "role"])

        KBEntry.objects.bulk_create(
            [
                KBEntry(
                    question="What is select_related in Django ORM?",
                    answer="select_related performs a SQL join.",
                    category=KBEntry.Category.DATABASE,
                ),
                KBEntry(
                    question="When should I use Q objects?",
                    answer="Q objects are useful for OR conditions.",
                    category=KBEntry.Category.FRAMEWORK,
                ),
            ]
        )

    def authenticate(self, username, password):
        response = self.client.post(
            reverse("login"),
            {"username": username, "password": password},
            format="json",
        )
        return response.data["access"]

    def test_register_creates_company_and_returns_token(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "acmecorp",
                "password": "securepass123",
                "company_name": "Acme Corp",
                "email": "dev@acmecorp.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertTrue(Company.objects.filter(user__username="acmecorp").exists())

    def test_register_duplicate_username_returns_400(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "clientco",
                "password": "securepass123",
                "company_name": "Another Co",
                "email": "another@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_token_company_name_and_api_key(self):
        response = self.client.post(
            reverse("login"),
            {"username": "clientco", "password": "securepass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "Client Co")
        self.assertIn("api_key", response.data)
        self.assertIn("access", response.data)

    def test_login_invalid_credentials_returns_401(self):
        response = self.client.post(
            reverse("login"),
            {"username": "clientco", "password": "wrongpass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_query_requires_authentication(self):
        response = self.client.post(
            reverse("kb-query"),
            {"search": "select_related"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_query_blank_search_returns_400(self):
        token = self.authenticate("clientco", "securepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            reverse("kb-query"),
            {"search": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_returns_results_and_writes_log(self):
        token = self.authenticate("clientco", "securepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            reverse("kb-query"),
            {"search": "select_related"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(QueryLog.objects.count(), 1)
        self.assertEqual(QueryLog.objects.first().results_count, 1)

    def test_query_no_results_still_logs(self):
        token = self.authenticate("clientco", "securepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            reverse("kb-query"),
            {"search": "does-not-exist"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(QueryLog.objects.count(), 1)
        self.assertEqual(QueryLog.objects.first().results_count, 0)

    def test_usage_summary_forbidden_for_client(self):
        token = self.authenticate("clientco", "securepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("usage-summary"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usage_summary_returns_aggregates_for_admin(self):
        QueryLog.objects.create(
            company=self.client_user.company,
            search_term="select_related",
            results_count=1,
        )
        QueryLog.objects.create(
            company=self.admin_user.company,
            search_term="select_related",
            results_count=1,
        )
        QueryLog.objects.create(
            company=self.admin_user.company,
            search_term="jwt authentication",
            results_count=0,
        )

        token = self.authenticate("adminco", "securepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("usage-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_queries"], 3)
        self.assertEqual(response.data["active_companies"], 2)
        self.assertEqual(response.data["top_search_terms"][0]["search_term"], "select_related")
