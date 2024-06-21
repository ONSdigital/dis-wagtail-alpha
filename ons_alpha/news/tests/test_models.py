from django.test import TestCase
from django.urls import reverse

from wagtail.test.utils import WagtailPageTestCase, WagtailTestUtils

import wagtail_factories

from ons_alpha.home.models import HomePage
from ons_alpha.news.factories import NewsIndexPageFactory, NewsPageFactory
from ons_alpha.news.models import NewsIndex, NewsPage


class NewsTests(WagtailPageTestCase):
    def test_factories(self):
        NewsPageFactory()
        NewsIndexPageFactory()

    def test_can_create_news_page_under_home_page(self):
        self.assertCanCreateAt(HomePage, NewsIndex)

    def test_can_create_news_page_under_news_index_page(self):
        self.assertCanCreateAt(NewsIndex, NewsPage)


class TestPreviewNewsPage(TestCase, WagtailTestUtils):
    """Regression test because some queries in .get_context() can break preview views

    This is because when previewing, Model Cluster's FakeQuerySets are used, and they
    don't implement the full API of Django's QuerySets.
    """

    def setUp(self):
        self.root_page = wagtail_factories.PageFactory(parent=None)
        self.news_index = NewsIndexPageFactory(parent=self.root_page)
        self.news_page = NewsPageFactory(parent=self.news_index)

        self.user = self.login()

        self.news_page_post_data = {
            "title": "Those that have just broken the flower vase",
            "slug": "those-that-have-just-broken-the-flower-vase",
            "introduction": "",
            "body-count": 1,
            "body-0-deleted": "",
            "body-0-order": 0,
            "body-0-type": "heading",
            "body-0-value": "Suckling pigs",
            "news_types-TOTAL_FORMS": 0,
            "news_types-INITIAL_FORMS": 0,
            "news_types-MIN_NUM_FORMS": 0,
            "news_types-MAX_NUM_FORMS": 0,
            "page_related_pages-TOTAL_FORMS": 0,
            "page_related_pages-INITIAL_FORMS": 0,
            "page_related_pages-MIN_NUM_FORMS": 0,
            "page_related_pages-MAX_NUM_FORMS": 0,
            "comments-TOTAL_FORMS": 0,
            "comments-INITIAL_FORMS": 0,
            "comments-MIN_NUM_FORMS": 0,
            "comments-MAX_NUM_FORMS": 1000,
        }
        self.news_index_post_data = {
            "title": "Innumerable ones",
            "slug": "innumerable-ones",
            "introduction": "",
            "comments-TOTAL_FORMS": 0,
            "comments-INITIAL_FORMS": 0,
            "comments-MIN_NUM_FORMS": 0,
            "comments-MAX_NUM_FORMS": 1000,
        }

    def test_preview_news_page_on_add(self):
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_add",
            args=("news", "newspage", self.news_index.id),
        )
        response = self.client.post(preview_url, self.news_page_post_data)

        # Check the JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"is_available": True, "is_valid": True}
        )

        # Check the user can refresh the preview
        preview_session_key = "wagtail-preview-news-newspage-{}".format(
            self.news_index.id
        )
        self.assertIn(preview_session_key, self.client.session)

        response = self.client.get(preview_url)

        # Check the HTML response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/news/news_page.html")
        self.assertContains(response, "Those that have just broken the flower vase")

    def test_preview_news_page_on_edit(self):
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_edit",
            args=(self.news_page.id,),
        )
        response = self.client.post(preview_url, self.news_page_post_data)

        # Check the JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"is_available": True, "is_valid": True}
        )

        # Check the user can refresh the preview
        preview_session_key = "wagtail-preview-{}".format(self.news_page.id)
        self.assertIn(preview_session_key, self.client.session)

        response = self.client.get(preview_url)

        # Check the HTML response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/news/news_page.html")
        self.assertContains(response, "Those that have just broken the flower vase")

    def test_preview_news_index_on_add(self):
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_add",
            args=("news", "newsindex", self.root_page.id),
        )
        response = self.client.post(preview_url, self.news_index_post_data)

        # Check the JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"is_available": True, "is_valid": True}
        )

        # Check the user can refresh the preview
        preview_session_key = "wagtail-preview-news-newsindex-{}".format(
            self.root_page.id
        )
        self.assertIn(preview_session_key, self.client.session)

        response = self.client.get(preview_url)

        # Check the HTML response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/news/news_index.html")
        self.assertContains(response, "Innumerable ones")

    def test_preview_news_index_on_edit(self):
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_edit",
            args=(self.news_index.id,),
        )
        response = self.client.post(preview_url, self.news_index_post_data)

        # Check the JSON response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"is_available": True, "is_valid": True}
        )

        # Check the user can refresh the preview
        preview_session_key = "wagtail-preview-{}".format(self.news_index.id)
        self.assertIn(preview_session_key, self.client.session)

        response = self.client.get(preview_url)

        # Check the HTML response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/news/news_index.html")
        self.assertContains(response, "Innumerable ones")
