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
    peer_links=frozenset([
        PeerLink(1, 2),
    ]),
    customer_provider_links=frozenset(
        [
            CPLink(provider_asn=1, customer_asn=ASNs.VICTIM.value),
            CPLink(provider_asn=3, customer_asn=2),
        ]
    ),
)

config_046 = EngineTestConfig(
    name="046",
    desc="ASPA-based test of possible route leak scenario",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph,
)
