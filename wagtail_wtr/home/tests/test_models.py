"""
Tests for the HomePage model.

Uses WagtailPageTests for page-tree / subpage assertion helpers, and
Django's TestCase with a request factory for get_context() tests.
"""

from django.test import RequestFactory, TestCase
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTests

from wagtail_wtr.home.models import HomePage
from wagtail_wtr.pages.models import ContentPage, IndexPage
from wagtail_wtr.forms.models import FormPage


class TestHomePageParentSubpageTypes(WagtailPageTests):
    """HomePage can only be created under the Wagtail root page."""

    def test_can_create_under_root(self):
        self.assertCanCreateAt(Page, HomePage)

    def test_can_not_create_under_home_page(self):
        self.assertCanNotCreateAt(HomePage, HomePage)

    def test_can_not_create_under_content_page(self):
        self.assertCanNotCreateAt(ContentPage, HomePage)

    def test_allowed_subpage_types(self):
        self.assertAllowedSubpageTypes(HomePage, [ContentPage, IndexPage, FormPage])


class TestHomePageGetContext(TestCase):
    """HomePage.get_context() must populate the hero dict correctly."""

    @classmethod
    def setUpTestData(cls):
        root = Page.objects.filter(depth=1).first()
        cls.home = HomePage(
            title="Home",
            slug="home-test-hpgc",
            hero_headline="Welcome",
            hero_copy="<p>Subtext</p>",
            hero_link_text="Learn more",
            hero_link_url="https://example.com",
        )
        root.add_child(instance=cls.home)

    def _get_context(self, page):
        request = RequestFactory().get("/")
        return page.get_context(request)

    def test_hero_headline_uses_custom_headline(self):
        ctx = self._get_context(self.home)
        self.assertEqual(ctx["hero"]["headline"], "Welcome")

    def test_hero_headline_falls_back_to_title(self):
        """When hero_headline is blank, headline falls back to page title."""
        self.home.hero_headline = ""
        ctx = self._get_context(self.home)
        self.assertEqual(ctx["hero"]["headline"], self.home.title)
        # restore
        self.home.hero_headline = "Welcome"

    def test_hero_copy_is_passed(self):
        ctx = self._get_context(self.home)
        self.assertEqual(ctx["hero"]["copy"], "<p>Subtext</p>")

    def test_hero_copy_is_block_is_false(self):
        ctx = self._get_context(self.home)
        self.assertFalse(ctx["hero"]["copy_is_block"])

    def test_hero_link_url_is_passed(self):
        ctx = self._get_context(self.home)
        self.assertEqual(ctx["hero"]["link_url"], "https://example.com")

    def test_hero_image_defaults_none(self):
        ctx = self._get_context(self.home)
        self.assertIsNone(ctx["hero"]["image"])

    def test_hero_video_defaults_none(self):
        ctx = self._get_context(self.home)
        self.assertIsNone(ctx["hero"]["video"])

    def test_hero_link_page_defaults_none(self):
        ctx = self._get_context(self.home)
        self.assertIsNone(ctx["hero"]["link_page"])

    def test_hero_dict_has_all_required_keys(self):
        ctx = self._get_context(self.home)
        required_keys = {
            "headline",
            "copy",
            "copy_is_block",
            "image",
            "video",
            "link_text",
            "link_page",
            "link_url",
        }
        self.assertEqual(set(ctx["hero"].keys()), required_keys)


class TestHomePageMeta(TestCase):
    """HomePage model Meta attributes."""

    def test_verbose_name(self):
        self.assertEqual(HomePage._meta.verbose_name, "home page")

    def test_verbose_name_plural(self):
        self.assertEqual(HomePage._meta.verbose_name_plural, "home pages")
