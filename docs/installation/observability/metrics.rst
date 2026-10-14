.. _installation_observability_metrics:

=======
Metrics
=======

Open Plan produces application metrics (using Open Telemetry).

.. note:: The exact metric names that show up may be transformed, e.g. Prometheus replaces
   periods with underscores, and processing pipelines may add prefixes or suffixes.

.. important:: Some metrics are defined as "global scope".

   These metrics are typically derived from application state introspection, e.g. by
   performing database (read) queries to aggregate some information. Usually those
   correspond to an `Asynchronous Gauge <https://opentelemetry.io/docs/specs/otel/metrics/api/#asynchronous-gauge>`_.

   Multiple replicas and/or instances of the same service will produce the same values
   of the metrics. You need to apply some kind of aggregation to de-duplicate these
   values. The attribute ``scope="global"``  acts as a marker for these type of metrics.

   With PromQL for example, you can use ``avg`` on the assumption that all values will
   be equal, so the average will also be identical:

   .. code-block:: promql

       avg by (type) (otel_openplan_auth_user_count{scope="global"})

Generic
=======

``http.server.duration``
    Captures how long each HTTP request took, in ms. The metric produces histogram data.

``http.server.request.duration`` (not active)
    The future replacement of ``http.server.duration``, in seconds. Currently not
    enabled, but the code is in the Open Telemetry SDK instrumentation already and could
    possibly be opted-in to.

Application specific
====================

Accounts
--------

``openplan.auth.user_count``
    Reports the number of users in the database. This is a global metric, you must take
    care in de-duplicating results. Additional attributes are:

    - ``scope`` - fixed, set to ``global`` to enable de-duplication.
    - ``type`` - the user type. ``all``, ``staff`` or ``superuser``.

    Sample PromQL query:

    .. code-block:: promql

        max by (type) (last_over_time(
          otel_openplan_auth_user_count{scope="global"}
          [1m]
        ))

``openplan.auth.login_failures``
    A counter incremented every time a user login fails (typically because of invalid
    credentials). Does not include the second factor, if enabled. Additional attributes:

    - ``http_target`` - the request path where the login failure occurred, if this
      happened in a request context.

``openplan.auth.user_lockouts``
    A counter incremented every time a user is locked out because they reached the
    maximum number of failed attempts. Additional attributes:

    - ``http_target`` - the request path where the login failure occurred, if this
      happened in a request context.
    - ``username`` - username of the user trying to log in.

``openplan.auth.logins``
    Counter incrementing on every successful login by a user. Additional attributes:

    - ``http_target`` - the request path where the login failure occurred, if this
      happened in a request context.
    - ``username`` - username of the user trying to log in.

``openplan.auth.logouts``
    Counter incrementing every time a user logs out. Additional attributes:

    - ``username`` - username of the user who logged out.



Contactmomenten
---------------

``openplan.contactmoment.creates``
    Reports the number of contactmomenten created via the API.

``openplan.contactmoment.updates``
    Reports the number of contactmomenten updated via the API.

``openplan.contactmoment.deletes``
    Reports the number of contactmomenten deleted via the API.


Subjecten
---------

``openplan.subject.creates``
    Reports the number of subjecten created via the API.

``openplan.subject.updates``
    Reports the number of subjecten updated via the API.

``openplan.subject.deletes``
    Reports the number of subjecten deleted via the API.


Doelen
------

``openplan.doel.creates``
    Reports the number of doelen created via the API.

``openplan.doel.updates``
    Reports the number of doelen updated via the API.

``openplan.doel.deletes``
    Reports the number of doelen deleted via the API.


Doeltypes
---------

``openplan.doeltype.creates``
    Reports the number of doeltypes created via the API.

``openplan.doeltype.updates``
    Reports the number of doeltypes updated via the API.

``openplan.doeltype.deletes``
    Reports the number of doeltypes deleted via the API.


Doelcategorieën
---------------

``openplan.doelcategorie.creates``
    Reports the number of doelcategorieën created via the API.

``openplan.doelcategorie.updates``
    Reports the number of doelcategorieën updated via the API.

``openplan.doelcategorie.deletes``
    Reports the number of doelcategorieën deleted via the API.


Plannen
-------

``openplan.plan.creates``
    Reports the number of plannen created via the API.

``openplan.plan.updates``
    Reports the number of plannen updated via the API.

``openplan.plan.deletes``
    Reports the number of plannen deleted via the API.


Instrumenten
------------

``openplan.instrument.creates``
    Reports the number of instrumenten created via the API.

``openplan.instrument.updates``
    Reports the number of instrumenten updated via the API.

``openplan.instrument.deletes``
    Reports the number of instrumenten deleted via the API.


Instrumenttypes
---------------

``openplan.instrumenttype.creates``
    Reports the number of instrumenttypes created via the API.

``openplan.instrumenttype.updates``
    Reports the number of instrumenttypes updated via the API.

``openplan.instrumenttype.deletes``
    Reports the number of instrumenttypes deleted via the API.

Query
-----

Sample PromQL query:

.. code-block:: promql

    sum by (otel_scope_name) (otel_openplan_plan_updates_total)
