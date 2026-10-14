# ruff: noqa: F403,F405
import os

# Django-hijack (and Django-hijack-admin)
from django.urls import reverse_lazy

os.environ["_USE_STRUCTLOG"] = "True"

from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config
from vng_api_common.conf.api import BASE_REST_FRAMEWORK  # noqa: F401


#
# Core Django settings
#

#
# DATABASE and CACHING setup
#
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DB_NAME", default="openplan"),
        "USER": config("DB_USER", default="openplan"),
        "PASSWORD": config("DB_PASSWORD", default="openplan"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432", cast=lambda s: int(s) if s else ""),
    }
}

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
    help_text=("Namespace used in URNs schemas."),
)

PLANNEN_API_VERSION = "0.1.0"

API_VERSION = "0"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()

REST_FRAMEWORK["DEFAULT_VERSION"] = "0"
REST_FRAMEWORK["PAGE_SIZE"] = 100

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
) + ("openplan.utils.renderers.ProblemJSONRenderer",)

REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "openplan.utils.schema.AutoSchema"

REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = (
    "vng_api_common.pagination.DynamicPageSizePagination"
)
REST_FRAMEWORK["EXCEPTION_HANDLER"] = "vng_api_common.views.exception_handler"

SPECTACULAR_SETTINGS = {
    "CONTACT": {
        "url": "https://github.com/maykinmedia/open-plan",
        "name": "Maykin Media",
        "email": "support@maykinmedia.nl",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "LICENSE": {
        "name": "EUPL 1.2",
        "url": "https://opensource.org/licenses/EUPL-1.2",
    },
}

# LOGIN_URL = reverse_lazy("admin:login")


#
# SECURITY settings
#
CSRF_FAILURE_VIEW = "openplan.accounts.views.csrf_failure"

X_FRAME_OPTIONS = "DENY"


#
# Custom settings
#
PROJECT_NAME = "Open Plan"

# Displaying environment information
ENVIRONMENT_LABEL = config("ENVIRONMENT_LABEL", ENVIRONMENT)
ENVIRONMENT_BACKGROUND_COLOR = config("ENVIRONMENT_BACKGROUND_COLOR", "orange")
ENVIRONMENT_FOREGROUND_COLOR = config("ENVIRONMENT_FOREGROUND_COLOR", "black")
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
