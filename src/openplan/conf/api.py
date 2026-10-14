from vng_api_common.conf.api import BASE_REST_FRAMEWORK  # noqa: F401

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
REST_FRAMEWORK["EXCEPTION_HANDLER"] = (
    "vng_api_common.exception_handling.exception_handler"
)
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework.authentication.TokenAuthentication",
)

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
