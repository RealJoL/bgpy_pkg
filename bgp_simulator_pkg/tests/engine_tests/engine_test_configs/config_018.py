from ..graphs import Graph018
from ..utils import EngineTestConfig

from ....simulation_engine import ROVAS
from ....enums import ASNs
from ....simulation_framework import ScenarioConfig, ValidPrefix


config_018 = EngineTestConfig(
    name="018",
    desc="Test of path length preference",
    scenario_config=ScenarioConfig(
        ScenarioCls=ValidPrefix,
        BaseASCls=ROVAS,
        override_attacker_asns={ASNs.ATTACKER.value},
        override_victim_asns={ASNs.VICTIM.value},
    ),
    graph=Graph018(),
)
