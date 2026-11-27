from django.utils.translation import gettext_lazy as _

from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.subdoeltype import SubdoelType
from openplan.utils.filters import UUIDFInFilter


class SubdoeltypeFilter(FilterSet):
    configuraties__uuids = UUIDFInFilter(
        field_name="configuraties__uuid",
        distinct=True,
        help_text=_("Lijst van configuratie uuids waarop kan worden gezocht."),
    )

    class Meta:
        model = SubdoelType
        fields = {
            "configuraties__uuid": ["exact"],
            "naam": ["exact", "icontains"],
            "status": ["exact"],
            "omschrijving": ["icontains"],
        }
