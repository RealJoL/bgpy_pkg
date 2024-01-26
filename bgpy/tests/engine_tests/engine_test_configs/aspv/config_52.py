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
    peer_links=frozenset(
        [PeerLink(peer1_asn=ASNs.VICTIM.value, peer2_asn=1)]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=4),
        ]
    ),
)

config_052 = EngineTestConfig(
    name="052",
    desc="ASPA-based test showing a complete valid route",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph,
)
