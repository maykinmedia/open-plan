from django.utils.translation import gettext_lazy as _

from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.evaluatietype import Evaluatietype
from openplan.utils.filters import UUIDFInFilter


class EvaluatietypeFilter(FilterSet):
    configuraties__uuids = UUIDFInFilter(
        field_name="configuraties__uuid",
        distinct=True,
        help_text=_("Lijst van configuratie uuids waarop kan worden gezocht."),
    )

    class Meta:
        model = Evaluatietype
        fields = {
            "configuraties__uuid": ["exact"],
            "naam": ["exact", "icontains"],
            "status": ["exact"],
            "omschrijving": ["icontains"],
        }
