from frozendict import frozendict

from bgpy.as_graphs import ASGraphInfo, PeerLink
from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy
from bgpy.tests.engine_tests.utils import EngineTestConfig
from bgpy.as_graphs.base.links.customer_provider_link import CustomerProviderLink as CPLink

from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix,
)

as_graph = ASGraphInfo(
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=ASNs.VICTIM.value, customer_asn=1),
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
        ]
    ),
)

config_051 = EngineTestConfig(
    name="051",
    desc="ASPA-based test showing a complete valid route",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph,
)
