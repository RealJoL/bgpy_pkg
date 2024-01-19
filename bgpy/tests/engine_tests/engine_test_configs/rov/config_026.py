from frozendict import frozendict
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_019
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import ROVPolicy
from bgpy.enums import ASNs
from bgpy.simulation_framework import (
    ScenarioConfig,
    ValidPrefix,
)


config_026 = EngineTestConfig(
    name="026",
    desc="Test of tiebreak preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BasePolicyCls=ROVPolicy,
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(),
    ),
    as_graph_info=as_graph_info_019,
)