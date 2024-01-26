from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo
from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy
from bgpy.tests.engine_tests.utils import EngineTestConfig
from bgpy.as_graphs.base.links.customer_provider_link import CustomerProviderLink as CPLink

from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix,
)

as_graph_valley = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=2),
        ]
    ),
)

config_042 = EngineTestConfig(
    name="042",
    desc="ASPA-based test valid valley scenario showing the limitations of ASPV",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_valley,
)
