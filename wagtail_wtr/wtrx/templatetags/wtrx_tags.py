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
