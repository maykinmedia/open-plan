# ruff: noqa: F403,F405
import os

# Django-hijack (and Django-hijack-admin)
from django.urls import reverse_lazy

os.environ["_USE_STRUCTLOG"] = "True"

from open_api_framework.conf.base import *  # noqa
from maykin_common.config import config  # noqa
from maykin_common.config import DocumentationParams

from .api import *  # noqa

#
# APPLICATIONS enabled for this project
#
INSTALLED_APPS += [
    "rest_framework.authtoken",
    # External applications.
    "hijack",
    "hijack.contrib.admin",
    "maykin_common",
    "capture_tag",
    # Project applications.
    "openplan.accounts",
    "openplan.utils",
    "openplan.plannen",
]

MIDDLEWARE += [
    "hijack.middleware.HijackUserMiddleware",
]

# URN settings
URN_NAMESPACE = config(
    "URN_NAMESPACE",
    documentation=DocumentationParams(
        help_text=("Namespace used in URNs schemas."),
    ),
)

#
# SECURITY settings
#
CSRF_FAILURE_VIEW = "maykin_common.views.csrf_failure"

X_FRAME_OPTIONS = "DENY"


#
# Custom settings
#
PROJECT_NAME = "Open Plan"

# Displaying environment information
ENVIRONMENT_LABEL = config("ENVIRONMENT_LABEL", default=ENVIRONMENT)
ENVIRONMENT_BACKGROUND_COLOR = config("ENVIRONMENT_BACKGROUND_COLOR", default="orange")
ENVIRONMENT_FOREGROUND_COLOR = config("ENVIRONMENT_FOREGROUND_COLOR", default="black")
SHOW_ENVIRONMENT = config("SHOW_ENVIRONMENT", default=True)

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]


# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

#
# Django-Admin-Index
#
ADMIN_INDEX_SHOW_REMAINING_APPS = False
ADMIN_INDEX_AUTO_CREATE_APP_GROUP = False
ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS = True
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "maykin_common.django_two_factor_auth.should_display_dropdown_menu"
)


#
# DJANGO-HIJACK
#
HIJACK_PERMISSION_CHECK = "maykin_2fa.hijack.superusers_only_and_is_verified"
HIJACK_INSERT_BEFORE = (
    '<div class="content">'  # note that this only applies to the admin
)
