from frozendict import frozendict

from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_003
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix,
)

config_038 = EngineTestConfig(
    name="038",
    desc="Multi-provider ASPV-based scenario (Fig. 5 in ROV paper)",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ASPVSimplePolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_003,
)
