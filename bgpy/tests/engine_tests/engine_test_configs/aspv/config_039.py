from frozendict import frozendict

from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy
from bgpy.simulation_engine.policies.aspv import ASPVSimpleExpensive
from bgpy.simulation_framework.scenarios import PathHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix, PrefixHijack,
)

from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.as_graphs.base.links.customer_provider_link import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links.peer_link import PeerLink

as_graph_info_provider_attacker = ASGraphInfo(
    peer_links=frozenset([PeerLink(peer1_asn=2, peer2_asn=ASNs.ATTACKER.value),
                         # PeerLink(peer1_asn=1, peer2_asn=ASNs.ATTACKER.value),
                          PeerLink(peer1_asn=2, peer2_asn=1),
                          ]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=1, customer_asn=4),
            CPLink(provider_asn=ASNs.ATTACKER.value, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=7),
            CPLink(provider_asn=4, customer_asn=8),
            CPLink(provider_asn=2, customer_asn=4),
            CPLink(provider_asn=2, customer_asn=5),
            CPLink(provider_asn=5, customer_asn=ASNs.VICTIM.value),
        ]
    )
)
config_039 = EngineTestConfig(
    name="039",
    desc="Multi-provider ASPV-based scenario with attacker as provider",
    scenario_config=ScenarioConfig(
        ScenarioCls=PathHijack,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_provider_attacker,
)
