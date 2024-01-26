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
        [PeerLink(peer1_asn=1, peer2_asn=4)]
    ),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=3, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=2, customer_asn=3),
            CPLink(provider_asn=1, customer_asn=2),
            CPLink(provider_asn=4, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=6),
            CPLink(provider_asn=6, customer_asn=7),
            CPLink(provider_asn=7, customer_asn=8),
        ]
    ),
)

config_049 = EngineTestConfig(
    name="049",
    desc="ASPA-based test showing a complete valid route",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph,
)
