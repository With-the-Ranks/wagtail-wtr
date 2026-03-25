from django import template


register = template.Library()

# Wagtail site settings are available in all templates via the context processor
# registered in settings/base.py:
#   "wagtail.contrib.settings.context_processors.settings"
#
# Access in templates using the dot-notation path to the settings model:
#   settings.<app_label>.BrandingSEOSettings.site_description
#
# where <app_label> is the generated project's wtrx app label
# (e.g. myproject_wtrx for a project named myproject).
#
# Alternatively, use the Wagtail built-in tag for one-off access:
#   load wagtailsettings_tags
#   get_settings
#   settings.<app_label>.BrandingSEOSettings.site_description
#
# Add project-specific template tags below.


@register.simple_tag
def page_as_card(page):
    """
    Convert a Wagtail Page object into the card dict shape expected by
    components/card.html.

    card.html expects: heading, description, image, link_page, link_url.
    Wagtail Page objects have: title, search_description, and optionally
    hero_image (if the page uses HeroMixin).

    Usage in templates:
        {% load wtrx_tags %}
        {% page_as_card child as card %}
        {% include "components/card.html" %}
    """
    image = getattr(page, "hero_image", None)
    return {
        "heading": page.title,
        "description": page.search_description or "",
        "image": image,
        "link_page": page,
        "link_url": None,
    }
