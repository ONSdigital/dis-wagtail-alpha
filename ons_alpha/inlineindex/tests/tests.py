from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from wagtail.test.utils import WagtailTestUtils

import bs4

from ons_alpha.home.models import HomePage
from ons_alpha.inlineindex.tests.fixtures import (
    InlineIndexChildFactory,
    InlineIndexFactory,
)


class TestDisplayOfInlineIndexChildPages(TestCase, WagtailTestUtils):
    def setup_homepage(self):
        self.homepage = HomePage.objects.first()
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)

    def setup_inline_index(self, live):
        self.inline_index = InlineIndexFactory(
            parent=self.homepage, title="The Example Index", live=live
        )

    def setup_first_index_child(self, live):
        self.first_index_child = InlineIndexChildFactory(
            parent=self.inline_index, title="The First Child", live=live
        )

    def setup_second_index_child(self, live):
        self.second_index_child = InlineIndexChildFactory(
            parent=self.inline_index, title="The Second Child", live=live
        )

    def setUp(self):
        self.setup_homepage()

    def test_live_request_to_live_index_success(self):
        """
        Just a sanity check.
        """
        self.setup_inline_index(live=True)

        response = self.client.get(self.inline_index.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.inline_index.title)

    def test_live_request_to_draft_index_fails(self):
        """
        Just a sanity check.
        """
        self.setup_inline_index(live=False)

        response = self.client.get(self.inline_index.url)

        self.assertEqual(response.status_code, 404)

    def test_live_request_to_live_index_shows_live_child(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)

        response = self.client.get(self.inline_index.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_index_child.title, count=2)

    def test_live_request_to_live_index_not_shows_draft_child(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=False)

        response = self.client.get(self.inline_index.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.first_index_child.title)

    def test_draft_request_to_draft_index_success(self):
        self.setup_inline_index(live=False)
        self.login()

        response = self.client.get(
            reverse("wagtailadmin_pages:view_draft", args=(self.inline_index.id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.inline_index.title)

    def test_draft_request_to_draft_index_shows_draft_child(self):
        self.setup_inline_index(live=False)
        self.setup_first_index_child(live=False)
        self.login()

        response = self.client.get(
            reverse("wagtailadmin_pages:view_draft", args=(self.inline_index.id,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_index_child.title, count=2)

    def test_live_request_to_live_child_shows_live_next_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)
        self.second_index_child = InlineIndexChildFactory(
            parent=self.inline_index, title="The Second Child", live=True
        )

        response = self.client.get(self.first_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.second_index_child.title, count=2)

    def test_live_request_to_live_child_shows_live_prev_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)
        self.setup_second_index_child(live=True)

        response = self.client.get(self.second_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_index_child.title, count=2)

    def test_live_request_to_live_child_not_shows_draft_next_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)
        self.setup_second_index_child(live=False)

        response = self.client.get(self.first_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.second_index_child.title)

    def test_live_request_to_live_child_not_shows_draft_prev_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=False)
        self.setup_second_index_child(live=True)

        response = self.client.get(self.second_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.first_index_child.title)

    def test_draft_request_to_draft_child_shows_draft_next_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=False)
        self.setup_second_index_child(live=False)
        self.login()

        response = self.client.get(
            reverse("wagtailadmin_pages:view_draft", args=(self.first_index_child.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.second_index_child.title, count=2)

    def test_draft_request_to_draft_child_shows_draft_prev_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=False)
        self.setup_second_index_child(live=False)
        self.login()

        response = self.client.get(
            reverse("wagtailadmin_pages:view_draft", args=(self.second_index_child.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_index_child.title, count=2)

    def test_live_request_to_live_child_skips_draft_next_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)
        self.setup_second_index_child(live=False)
        third_index_child = InlineIndexChildFactory(
            parent=self.inline_index, title="The Third Child", live=True
        )

        response = self.client.get(self.first_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.second_index_child.title)
        self.assertContains(response, third_index_child.title, count=2)

    def test_live_request_to_live_child_skips_draft_prev_sibling(self):
        self.setup_inline_index(live=True)
        self.setup_first_index_child(live=True)
        self.setup_second_index_child(live=False)
        third_index_child = InlineIndexChildFactory(
            parent=self.inline_index, title="The Third Child", live=True
        )

        response = self.client.get(third_index_child.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.second_index_child.title)
        self.assertContains(response, self.first_index_child.title, count=2)


class TestInlineIndexTitles(TestCase):
    """
    Test how inline index title and subtitle are used when displaying the section.

    The title of the inline index page itself is the title to the whole section. It
    should not show up in the table of contents for the section. It should also not show
    up as the "previous" link that is displayed on the first child page. In either
    of those cases the inline index subtitle should be used.

    """

    @classmethod
    def setUpTestData(cls):
        cls.homepage = HomePage.objects.first()
        cls.inline_index = InlineIndexFactory(
            parent=cls.homepage,
            title="The inline index title",
            subtitle="The inline index subtitle",
        )
        cls.inline_child = InlineIndexChildFactory(
            parent=cls.inline_index, title="The inline child title"
        )

    def test_index_title(self):
        index_title = self.inline_index.index_title

        self.assertEqual(index_title, self.inline_index.title)

    def test_inline_index_page_content_title(self):
        index_title = self.inline_index.content_title

        self.assertEqual(index_title, self.inline_index.subtitle)

    def test_inline_child_page_index_title(self):
        """The index title should be the same on the child and the index."""

        self.assertEqual(self.inline_child.index_title, self.inline_index.index_title)

    def test_inline_child_page_content_title(self):
        child_content_title = self.inline_child.content_title

        self.assertEqual(child_content_title, self.inline_child.title)

    def test_inline_index_page_rendering(self):
        response = self.client.get(self.inline_index.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        # Page heading
        page_heading = soup.find("h1")
        self.assertEqual(page_heading.get_text(strip=True), self.inline_index.title)
        # Content heading
        content_heading = soup.find("h2", {"class": "heading"})
        self.assertEqual(
            content_heading.get_text(strip=True), self.inline_index.subtitle
        )

        # Table of contents
        table_of_contents = soup.find(class_="index-nav")
        self.assertIsNotNone(table_of_contents)

        first_toc_entry = table_of_contents.find(class_="index-nav__item")
        self.assertEqual(
            first_toc_entry.get_text(strip=True), self.inline_index.subtitle
        )

    def test_inline_child_page_rendering(self):
        response = self.client.get(self.inline_child.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        soup = bs4.BeautifulSoup(response.content, "html.parser")

        # Page heading
        page_heading = soup.find("h1")
        self.assertEqual(page_heading.get_text(strip=True), self.inline_index.title)
        # Content heading
        content_heading = soup.find("h2", {"class": "heading"})
        self.assertEqual(content_heading.get_text(strip=True), self.inline_child.title)

        # Table of contents
        table_of_contents = soup.find(class_="index-nav")
        self.assertIsNotNone(table_of_contents)
        first_toc_entry = table_of_contents.find(class_="index-nav__item")
        self.assertEqual(
            first_toc_entry.get_text(strip=True), self.inline_index.subtitle
        )

        # Previous page link
        prev_page_link = soup.find(class_="index-pagination__page-title")
        self.assertEqual(
            prev_page_link.get_text(strip=True), self.inline_index.subtitle
        )
