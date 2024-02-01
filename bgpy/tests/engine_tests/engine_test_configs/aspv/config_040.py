from frozendict import frozendict

from bgpy.simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy
from bgpy.simulation_engine.policies.aspv import ASPVSimpleExpensive
from bgpy.simulation_framework.scenarios import PathHijack
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
)

from bgpy.as_graphs.base.as_graph_info import ASGraphInfo
from bgpy.as_graphs.base.links.customer_provider_link import CustomerProviderLink as CPLink
from bgpy.as_graphs.base.links.peer_link import PeerLink

as_graph_info_provider_attacker = ASGraphInfo(
    peer_links=frozenset([PeerLink(peer1_asn=4, peer2_asn=ASNs.ATTACKER.value),
]),
                        #  PeerLink(peer1_asn=4, peer2_asn=2)]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=4, customer_asn=2),
            CPLink(provider_asn=1, customer_asn=3),
            CPLink(provider_asn=3, customer_asn=2),
            CPLink(provider_asn=3, customer_asn=7)
        ]
    )
)
config_040 = EngineTestConfig(
    name="040",
    desc="ASPV-based scenario attacker as peer. This scenario demonstrates ASPVs effectiveness compared to ROV",
    scenario_config=ScenarioConfig(
        ScenarioCls=PathHijack,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_provider_attacker,
)

# This configuration will cause two other compromised ASes using a PathHijack attack under ROV
# Using ASPA, no AS is affected due to AS 666 not being inside the 777 provider set
