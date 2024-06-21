from django.test import Client, TestCase


class CSRFCustomViewTest(TestCase):
    def test_crsf_token_mismatch_displays_custom_page(self):
        client = Client(enforce_csrf_checks=True)
        client.cookies["csrftoken"] = "wrong"
        response = client.post("/admin/login/", {})

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "pages/errors/403.html")

    def test_crsf_token_mismatch_logs_an_error(self):
        client = Client(enforce_csrf_checks=True)
        client.cookies["csrftoken"] = "wrong"
        with self.assertLogs("django.security.csrf", level="ERROR") as logs_recorder:
            client.post("/admin/login/", {})
            self.assertIn("CSRF Failure: CSRF cookie", logs_recorder.output[0])
