from django.urls import include, path

from drf_spectacular.views import (
    SpectacularRedocView,
)
from vng_api_common import routers

from ...utils.views import SpectacularJSONAPIView, SpectacularYAMLAPIView
from .schema import custom_settings
from .viewsets.contactmoment import ContactmomentViewSet
from .viewsets.doel import DoelViewSet
from .viewsets.overkoepelendplan import OverkoepelendPlanViewSet
from .viewsets.persoon import PersoonViewSet
from .viewsets.plan import PlanViewSet
from .viewsets.plantype import PlanTypeViewSet
from .viewsets.relatie import RelatieViewSet
from .viewsets.relatietype import RelatieTypeViewSet

app_name = "plannen"

router = routers.DefaultRouter()

router.register("contactmoment", ContactmomentViewSet)
router.register("plan", PlanViewSet)
router.register("plantype", PlanTypeViewSet)
router.register("doel", DoelViewSet)
router.register("persoon", PersoonViewSet)
router.register("relatie", RelatieViewSet)
router.register("relatietype", RelatieTypeViewSet)

router.register("overkoepelendplan", OverkoepelendPlanViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", router.APIRootView.as_view(), name="root"),
    path(
        "openapi.json",
        SpectacularJSONAPIView.as_view(
            urlconf="openplan.plannen.api.urls",
            custom_settings=custom_settings,
        ),
        name="schema-json-plannen",
    ),
    path(
        "openapi.yaml",
        SpectacularYAMLAPIView.as_view(
            urlconf="openplan.plannen.api.urls",
            custom_settings=custom_settings,
        ),
        name="schema-yaml-plannen",
    ),
    path(
        "schema/",
        SpectacularRedocView.as_view(
            url_name="plannen:schema-yaml-plannen",
        ),
        name="schema-redoc-plannen",
    ),
]
