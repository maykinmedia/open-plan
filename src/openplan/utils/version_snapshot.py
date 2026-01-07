from openplan.plannen.api.serializers.doel import DoelSerializer
from openplan.plannen.api.serializers.plan import PlanSerializer


def build_snapshot(plan):
    return {
        "plan": PlanSerializer(plan).data,
        "doelen": DoelSerializer(plan.doelen.all(), many=True).data,
    }
