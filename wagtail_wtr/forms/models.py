from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField

from wagtail_wtr.wtrx.models import BasePage


class FormField(AbstractFormField):
    """
    A single field in a FormPage's form builder.

    Uses ParentalKey so form fields are treated as child objects of FormPage
    and serialised correctly by Wagtail's modelcluster/page machinery.
    """

    page = ParentalKey(
        "FormPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class FormPage(BasePage, AbstractEmailForm):
    """
    A Wagtail form builder page.

    Editors define form fields via the inline panel. Submissions are stored
    in the Wagtail DB and optionally emailed. The form is rendered inline
    on any page that contains a SignupWagtailFormsBlock pointing to this page.

    MRO note: BasePage must come before AbstractEmailForm to keep Wagtail's
    page machinery (slug, tree, routing) in the correct resolution order.

    content_panels is explicitly defined starting from
    AbstractEmailForm.content_panels (== Page.content_panels) to avoid the
    MRO resolving to BasePage.content_panels and dropping email fields.

    Future: override process_form_submission() to forward submissions to
    Action Network when IntegrationSettings.signup_platform == "action_network".
    See PLAN.md FormPage notes for the full forwarding design.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        verbose_name=_("intro"),
        help_text=_("Optional introductory text displayed above the form."),
    )
    thank_you_text = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        verbose_name=_("thank you text"),
        help_text=_("Text displayed after a successful form submission."),
    )

    # Explicitly start from AbstractEmailForm.content_panels (== Page.content_panels).
    # Do NOT use BasePage.content_panels or MRO will drop the email notification fields.
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label=_("Form fields")),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading=_("Email notifications"),
        ),
    ]

    promote_panels = BasePage.promote_panels

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading=_("Content")),
        ObjectList(promote_panels, heading=_("Promote")),
    ])

    parent_page_types = [
        "wagtail_wtr_home.HomePage",
        "wagtail_wtr_pages.ContentPage",
        "wagtail_wtr_pages.IndexPage",
    ]
    subpage_types = []

    class Meta:
        verbose_name = _("form page")
        verbose_name_plural = _("form pages")

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        # FormPage has no HeroMixin, so there are no hero_* fields on the model.
        # We still build the hero dict so that components/hero.html can render a
        # consistent title-only heading bar without branching on page type.
        # All optional keys are None; headline is always the page title.
        ctx["hero"] = {
            "headline": self.title,
            "copy": None,
            "copy_is_block": False,
            "image": None,
            "link_text": None,
            "link_page": None,
            "link_url": None,
        }
        return ctx
