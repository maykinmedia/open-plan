from opentelemetry import metrics

meter = metrics.get_meter("openplan.plannen")

contactmomenten_create_counter = meter.create_counter(
    "openplan.contactmoment.creates",
    description="Amount of contactmomenten created (via the API).",
    unit="1",
)
contactmomenten_update_counter = meter.create_counter(
    "openplan.contactmoment.updates",
    description="Amount of contactmomenten updated (via the API).",
    unit="1",
)
contactmomenten_delete_counter = meter.create_counter(
    "openplan.contactmoment.deletes",
    description="Amount of contactmomenten deleted (via the API).",
    unit="1",
)

doelen_create_counter = meter.create_counter(
    "openplan.doel.creates",
    description="Amount of doelen created (via the API).",
    unit="1",
)
doelen_update_counter = meter.create_counter(
    "openplan.doel.updates",
    description="Amount of doelen updated (via the API).",
    unit="1",
)
doelen_delete_counter = meter.create_counter(
    "openplan.doel.deletes",
    description="Amount of doelen deleted (via the API).",
    unit="1",
)

doelcategorieen_create_counter = meter.create_counter(
    "openplan.doelcategorie.creates",
    description="Amount of doelcategorieën created (via the API).",
    unit="1",
)
doelcategorieen_update_counter = meter.create_counter(
    "openplan.doelcategorie.updates",
    description="Amount of doelcategorieën updated (via the API).",
    unit="1",
)
doelcategorieen_delete_counter = meter.create_counter(
    "openplan.doelcategorie.deletes",
    description="Amount of doelcategorieën deleted (via the API).",
    unit="1",
)

doeltypen_create_counter = meter.create_counter(
    "openplan.doeltype.creates",
    description="Amount of doeltypen created (via the API).",
    unit="1",
)
doeltypen_update_counter = meter.create_counter(
    "openplan.doeltype.updates",
    description="Amount of doeltypen updated (via the API).",
    unit="1",
)
doeltypen_delete_counter = meter.create_counter(
    "openplan.doeltype.deletes",
    description="Amount of doeltypen deleted (via the API).",
    unit="1",
)

instrumenten_create_counter = meter.create_counter(
    "openplan.instrument.creates",
    description="Amount of instrumenten created (via the API).",
    unit="1",
)
instrumenten_update_counter = meter.create_counter(
    "openplan.instrument.updates",
    description="Amount of instrumenten updated (via the API).",
    unit="1",
)
instrumenten_delete_counter = meter.create_counter(
    "openplan.instrument.deletes",
    description="Amount of instrumenten deleted (via the API).",
    unit="1",
)

instrumenttypen_create_counter = meter.create_counter(
    "openplan.instrumenttype.creates",
    description="Amount of instrumenttypen created (via the API).",
    unit="1",
)
instrumenttypen_update_counter = meter.create_counter(
    "openplan.instrumenttype.updates",
    description="Amount of instrumenttypen updated (via the API).",
    unit="1",
)
instrumenttypen_delete_counter = meter.create_counter(
    "openplan.instrumenttype.deletes",
    description="Amount of instrumenttypen deleted (via the API).",
    unit="1",
)

subjecten_create_counter = meter.create_counter(
    "openplan.subject.creates",
    description="Amount of subjecten created (via the API).",
    unit="1",
)
subjecten_update_counter = meter.create_counter(
    "openplan.subject.updates",
    description="Amount of subjecten updated (via the API).",
    unit="1",
)
subjecten_delete_counter = meter.create_counter(
    "openplan.subject.deletes",
    description="Amount of subjecten deleted (via the API).",
    unit="1",
)

plannen_create_counter = meter.create_counter(
    "openplan.plan.creates",
    description="Amount of plannen created (via the API).",
    unit="1",
)
plannen_update_counter = meter.create_counter(
    "openplan.plan.updates",
    description="Amount of plannen updated (via the API).",
    unit="1",
)
plannen_delete_counter = meter.create_counter(
    "openplan.plan.deletes",
    description="Amount of plannen deleted (via the API).",
    unit="1",
)
