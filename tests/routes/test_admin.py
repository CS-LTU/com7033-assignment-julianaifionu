import unittest
from unittest.mock import patch
from app import app


class FlaskTemplateRoutesTests(unittest.TestCase):
    # Tests for admin routes that render templates.
    def setUp(self):
        # Set up Flask test client.
        app.testing = True
        self.client = app.test_client()

    def test_dashboard_route(self):
        # Test GET /admin/dashboard renders the dashboard template.
        with patch(
            "models.patients.mongo_models.get_patient_admin_stats"
        ) as mock_patient_stats, patch(
            "models.admin.admin_models.get_user_admin_stats"
        ) as mock_user_stats, patch(
            "models.admin.admin_models.get_all_users"
        ) as mock_get_users:

            with self.client.session_transaction() as sess:
                sess["user_id"] = 1
                sess["role_name"] = "admin"

            mock_patient_stats.return_value = {"total": 5}
            mock_user_stats.return_value = {"total_users": 3}
            mock_get_users.return_value = [{"id": 1, "username": "admin"}]

            response = self.client.get("/admin/dashboard")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"dashboard", response.data)

    def test_create_user_get_route(self):
        # Test GET /admin/users/create renders the create user template.
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role_name"] = "admin"

        response = self.client.get("/admin/users/create")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"create", response.data)
