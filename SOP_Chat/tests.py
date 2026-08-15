from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from .models import Post





class PostTests(TestCase):
    @classmethod
    

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/upload/")
        self.assertEqual(response.status_code, 200)

    def test_upload_get(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upload/upload_form.html")
        #self.assertContains(response, "This is a test!")

    def test_upload_post(self):
        response= self.client.post(reverse("upload"))
        self.assertEqual(response.status_code, 200)


