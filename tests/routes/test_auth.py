import unittest
from app import app


class AuthRoutesTests(unittest.TestCase):
    # Unit tests for auth routes.

    def setUp(self):
        # Set up Flask test client.
        app.testing = True
        self.client = app.test_client()

    def test_login_get_renders_template(self):
        # GET auth/login should render login page if user not logged in.
        with self.client.session_transaction() as sess:
            sess.clear()

        response = self.client.get("auth/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign In", response.data)

    def test_login_get_redirect_if_logged_in(self):
        # GET auth/login should redirect if user already logged in.
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role_name"] = "admin"

        response = self.client.get("auth/login")
        self.assertEqual(response.status_code, 302)
