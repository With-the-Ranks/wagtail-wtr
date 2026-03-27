"""
Tests for ContentPage and IndexPage models.

WagtailPageTests covers parent/subpage type constraints.
TestCase with RequestFactory covers get_context() behaviour.
"""

from django.test import RequestFactory, TestCase
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTests

from wagtail_wtr.home.models import HomePage
from wagtail_wtr.pages.models import ContentPage, IndexPage, ITEMS_PER_PAGE
from wagtail_wtr.forms.models import FormPage


# ---------------------------------------------------------------------------
# ContentPage
# ---------------------------------------------------------------------------


class TestContentPageParentSubpageTypes(WagtailPageTests):
    """ContentPage parent/subpage type constraints."""

    def test_can_create_under_home_page(self):
        self.assertCanCreateAt(HomePage, ContentPage)

    def test_can_create_under_content_page(self):
        self.assertCanCreateAt(ContentPage, ContentPage)

    def test_can_create_under_index_page(self):
        self.assertCanCreateAt(IndexPage, ContentPage)

    def test_can_not_create_under_root(self):
        self.assertCanNotCreateAt(Page, ContentPage)

    def test_allowed_subpage_types(self):
        self.assertAllowedSubpageTypes(ContentPage, [ContentPage, IndexPage, FormPage])


class TestContentPageGetContext(TestCase):
    """ContentPage.get_context() must populate the hero dict correctly."""

    @classmethod
    def setUpTestData(cls):
        root = Page.objects.filter(depth=1).first()
        cls.home = HomePage(title="Home", slug="home-cp")
        root.add_child(instance=cls.home)
        cls.page = ContentPage(
            title="About Us",
            slug="about",
            hero_headline="Our Story",
            hero_link_text="Contact",
            hero_link_url="https://example.com/contact",
        )
        cls.home.add_child(instance=cls.page)

    def _get_context(self, page):
        request = RequestFactory().get("/")
        return page.get_context(request)

    def test_hero_headline_uses_custom(self):
        ctx = self._get_context(self.page)
        self.assertEqual(ctx["hero"]["headline"], "Our Story")

    def test_hero_headline_falls_back_to_title(self):
        self.page.hero_headline = ""
        ctx = self._get_context(self.page)
        self.assertEqual(ctx["hero"]["headline"], "About Us")
        self.page.hero_headline = "Our Story"

    def test_copy_is_block_is_false(self):
        ctx = self._get_context(self.page)
        self.assertFalse(ctx["hero"]["copy_is_block"])

    def test_hero_video_defaults_none(self):
        ctx = self._get_context(self.page)
        self.assertIsNone(ctx["hero"]["video"])

    def test_hero_dict_keys(self):
        ctx = self._get_context(self.page)
        expected = {
            "headline",
            "copy",
            "copy_is_block",
            "image",
            "video",
            "link_text",
            "link_page",
            "link_url",
        }
        self.assertEqual(set(ctx["hero"].keys()), expected)


class TestContentPageMeta(TestCase):
    def test_verbose_name(self):
        self.assertEqual(ContentPage._meta.verbose_name, "content page")

    def test_verbose_name_plural(self):
        self.assertEqual(ContentPage._meta.verbose_name_plural, "content pages")


# ---------------------------------------------------------------------------
# IndexPage
# ---------------------------------------------------------------------------


class TestIndexPageParentSubpageTypes(WagtailPageTests):
    """IndexPage parent/subpage type constraints."""

    def test_can_create_under_home_page(self):
        self.assertCanCreateAt(HomePage, IndexPage)

    def test_can_create_under_content_page(self):
        self.assertCanCreateAt(ContentPage, IndexPage)

    def test_can_not_create_under_root(self):
        self.assertCanNotCreateAt(Page, IndexPage)

    def test_allowed_subpage_types(self):
        self.assertAllowedSubpageTypes(IndexPage, [ContentPage, IndexPage, FormPage])


class TestIndexPageGetContext(TestCase):
    """IndexPage.get_context() must populate hero + children + paginator."""

    @classmethod
    def setUpTestData(cls):
        root = Page.objects.filter(depth=1).first()
        cls.home = HomePage(title="Home", slug="home-ip")
        root.add_child(instance=cls.home)
        cls.index = IndexPage(title="Blog", slug="blog")
        cls.home.add_child(instance=cls.index)

        # Create 3 live child pages
        for i in range(3):
            child = ContentPage(title=f"Post {i + 1}", slug=f"post-{i + 1}")
            cls.index.add_child(instance=child)

    def _get_context(self, page, query_string=""):
        request = RequestFactory().get("/", query_string)
        return page.get_context(request)

    def test_hero_dict_present(self):
        ctx = self._get_context(self.index)
        self.assertIn("hero", ctx)

    def test_children_in_context(self):
        ctx = self._get_context(self.index)
        self.assertIn("children", ctx)

    def test_paginator_in_context(self):
        ctx = self._get_context(self.index)
        self.assertIn("paginator", ctx)

    def test_children_count_matches_live_children(self):
        ctx = self._get_context(self.index)
        # Page object from Paginator; len() counts items on the current page
        self.assertEqual(len(ctx["children"].object_list), 3)

    def test_invalid_page_number_returns_page_1(self):
        ctx = self._get_context(self.index, {"page": "abc"})
        self.assertEqual(ctx["children"].number, 1)

    def test_out_of_range_page_returns_last_page(self):
        ctx = self._get_context(self.index, {"page": "9999"})
        paginator = ctx["paginator"]
        self.assertEqual(ctx["children"].number, paginator.num_pages)

    def test_items_per_page_constant(self):
        self.assertEqual(ITEMS_PER_PAGE, 12)


class TestIndexPageMeta(TestCase):
    def test_verbose_name(self):
        self.assertEqual(IndexPage._meta.verbose_name, "index page")

    def test_verbose_name_plural(self):
        self.assertEqual(IndexPage._meta.verbose_name_plural, "index pages")
