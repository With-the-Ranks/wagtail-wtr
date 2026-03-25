from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    PageChooserBlock,
    StreamBlock,
    StructBlock,
    URLBlock,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

from .images import CustomImage


# ---------------------------------------------------------------------------
# Navigation link blocks (used by NavigationSettings and FooterSettings)
# ---------------------------------------------------------------------------


class InternalLinkBlock(StructBlock):
    """A navigation link to an internal Wagtail page."""

    text = CharBlock(label=_("link text"))
    page = PageChooserBlock(label=_("page"))

    class Meta:
        icon = "link"
        label = _("internal link")


class ExternalLinkBlock(StructBlock):
    """A navigation link to an external URL."""

    text = CharBlock(label=_("link text"))
    url = URLBlock(label=_("URL"))

    class Meta:
        icon = "link"
        label = _("external link")


class FooterColumnBlock(StructBlock):
    """A column of links in the footer."""

    heading = CharBlock(label=_("column heading"), required=False)
    links = StreamBlock(
        [
            ("internal", InternalLinkBlock()),
            ("external", ExternalLinkBlock()),
        ],
        label=_("links"),
    )

    class Meta:
        icon = "list-ul"
        label = _("footer column")


# Module-level so it can be reused in templates/filters if needed.
SOCIAL_PLATFORM_CHOICES = [
    ("facebook", "Facebook"),
    ("twitter", "Twitter / X"),
    ("instagram", "Instagram"),
    ("tiktok", "TikTok"),
    ("linkedin", "LinkedIn"),
    ("youtube", "YouTube"),
    ("threads", "Threads"),
    ("bluesky", "Bluesky"),
    ("mastodon", "Mastodon"),
]


class SocialLinkBlock(StructBlock):
    """
    A single social media link.

    Explicitly named StructBlock subclass (not anonymous) so Django's migration
    serialization can reference it by dotted path.
    """

    platform = ChoiceBlock(choices=SOCIAL_PLATFORM_CHOICES, label=_("platform"))
    url = URLBlock(label=_("URL"))

    class Meta:
        icon = "site"
        label = _("social link")


# ---------------------------------------------------------------------------
# Field validators
# ---------------------------------------------------------------------------


def validate_comma_separated_integers(value):
    """Validate that value is a comma-separated list of integers."""
    if value:
        try:
            [int(x.strip()) for x in value.split(",") if x.strip()]
        except ValueError:
            raise ValidationError(
                _("Enter a comma-separated list of integers, e.g. 10,25,50,100.")
            )


# ---------------------------------------------------------------------------
# Settings panels
# ---------------------------------------------------------------------------


@register_setting
class BrandingSEOSettings(BaseSiteSetting):
    """Settings > Branding & SEO — logo, favicon, default meta image, site description."""

    logo = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("logo"),
        help_text=_("Primary site logo. Displayed in the header."),
    )
    dark_logo = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("dark logo"),
        help_text=_("Logo variant for dark backgrounds."),
    )
    favicon = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("favicon"),
        help_text=_("Browser favicon (square image, 32×32 px or SVG)."),
    )
    default_meta_image = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("default meta image"),
        help_text=_(
            "Fallback OG / Twitter card image used when a page has no meta image set."
        ),
    )
    site_description = models.TextField(
        blank=True,
        verbose_name=_("site description"),
        help_text=_("Default meta description for the site."),
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel("logo"), FieldPanel("dark_logo"), FieldPanel("favicon")],
            heading=_("Logos"),
        ),
        MultiFieldPanel(
            [FieldPanel("default_meta_image"), FieldPanel("site_description")],
            heading=_("SEO defaults"),
        ),
    ]

    class Meta:
        verbose_name = _("Branding & SEO")


@register_setting
class NavigationSettings(BaseSiteSetting):
    """Settings > Navigation — primary nav links, CTA button."""

    primary_navigation = StreamField(
        [
            ("internal", InternalLinkBlock()),
            ("external", ExternalLinkBlock()),
        ],
        blank=True,
        verbose_name=_("primary navigation"),
        help_text=_("Links shown in the main navigation bar."),
        use_json_field=True,
    )
    cta_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("CTA button text"),
        help_text=_("Text for the header call-to-action button."),
    )
    cta_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("CTA page"),
        help_text=_(
            "Internal link for the CTA button. Set either this or CTA URL, not both."
        ),
    )
    cta_url = models.URLField(
        blank=True,
        verbose_name=_("CTA URL"),
        help_text=_(
            "External link for the CTA button. Set either this or CTA page, not both."
        ),
    )

    panels = [
        FieldPanel("primary_navigation"),
        MultiFieldPanel(
            [FieldPanel("cta_text"), FieldPanel("cta_page"), FieldPanel("cta_url")],
            heading=_("CTA button"),
        ),
    ]

    class Meta:
        verbose_name = _("Navigation")


@register_setting
class FooterSettings(BaseSiteSetting):
    """Settings > Footer — footer nav columns, copyright text."""

    footer_navigation = StreamField(
        [("column", FooterColumnBlock())],
        blank=True,
        verbose_name=_("footer navigation"),
        help_text=_(
            "Footer link columns. Each column has a heading and a list of links."
        ),
        use_json_field=True,
    )
    copyright_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("copyright text"),
        help_text=_(
            'Optional. Overrides the default "© {year} {site name}" copyright line.'
        ),
    )

    panels = [
        FieldPanel("footer_navigation"),
        FieldPanel("copyright_text"),
    ]

    class Meta:
        verbose_name = _("Footer")


@register_setting
class SocialSettings(BaseSiteSetting):
    """Settings > Social — social media links."""

    social_links = StreamField(
        [("link", SocialLinkBlock())],
        blank=True,
        verbose_name=_("social links"),
        use_json_field=True,
    )

    panels = [FieldPanel("social_links")]

    class Meta:
        verbose_name = _("Social")


DONATION_PLATFORM_CHOICES = [
    ("none", _("None")),
    ("actblue", "ActBlue"),
]

SIGNUP_PLATFORM_CHOICES = [
    ("wagtail_forms", _("Wagtail Forms (built-in)")),
    ("action_network", "Action Network"),
    ("none", _("None")),
]


@register_setting
class IntegrationSettings(BaseSiteSetting):
    """Settings > Integrations — donation and signup platform configuration."""

    donation_platform = models.CharField(
        max_length=50,
        choices=DONATION_PLATFORM_CHOICES,
        default="none",
        verbose_name=_("donation platform"),
    )
    donation_base_url = models.URLField(
        blank=True,
        verbose_name=_("donation base URL"),
        help_text=_(
            "e.g. https://secure.actblue.com/donate/mycampaign. "
            "Used by DonateBlock when no override URL is set."
        ),
    )
    donation_suggested_amounts = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("suggested donation amounts"),
        help_text=_(
            "Comma-separated integers, e.g. 10,25,50,100. "
            "Used by DonateBlock when no override amounts are set."
        ),
        validators=[validate_comma_separated_integers],
    )
    donation_default_recurring = models.BooleanField(
        default=False,
        verbose_name=_("default to recurring donation"),
    )
    signup_platform = models.CharField(
        max_length=50,
        choices=SIGNUP_PLATFORM_CHOICES,
        default="wagtail_forms",
        verbose_name=_("signup platform"),
    )
    action_network_api_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Action Network API key"),
        help_text=_(
            "Stored in the database. For production, prefer setting "
            "WTRX_ACTION_NETWORK_API_KEY as an environment variable and leaving this blank."
        ),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("donation_platform"),
                FieldPanel("donation_base_url"),
                FieldPanel("donation_suggested_amounts"),
                FieldPanel("donation_default_recurring"),
            ],
            heading=_("Donations"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("signup_platform"),
                FieldPanel("action_network_api_key"),
            ],
            heading=_("Signups"),
        ),
    ]

    def get_donation_platform(self):
        """
        Return the effective donation platform.
        Admin setting takes precedence; falls back to WTRX_DONATION_PLATFORM Django setting.
        """
        if self.donation_platform and self.donation_platform != "none":
            return self.donation_platform
        return getattr(settings, "WTRX_DONATION_PLATFORM", "none")

    def get_signup_platform(self):
        """
        Return the effective signup platform.
        Admin setting takes precedence; falls back to WTRX_SIGNUP_PLATFORM Django setting.
        """
        if self.signup_platform and self.signup_platform != "none":
            return self.signup_platform
        return getattr(settings, "WTRX_SIGNUP_PLATFORM", "wagtail_forms")

    def get_action_network_api_key(self):
        """
        Return the effective Action Network API key.

        Intentionally reversed precedence compared to get_donation_platform /
        get_signup_platform: the env/Django setting wins over the DB value here
        because API keys should not be stored in the database in production.
        Set WTRX_ACTION_NETWORK_API_KEY as an environment variable to override
        the DB-stored value.
        """
        env_key = getattr(settings, "WTRX_ACTION_NETWORK_API_KEY", "")
        return env_key or self.action_network_api_key

    class Meta:
        verbose_name = _("Integrations")
