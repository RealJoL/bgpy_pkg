from copy import deepcopy

from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPAS
from ....simulation_framework import ValidPrefix, ScenarioConfig
from ....enums import Prefixes


class Custom34ValidPrefix(ValidPrefix):
    """Add a better announcement in round 2 to cause withdrawal"""

    __slots__ = ()

    def post_propagation_hook(self, engine=None, propagation_round=0, *args, **kwargs):
        if propagation_round == 1:  # second round
            ann = deepcopy(engine.as_dict[2]._local_rib.get_ann(Prefixes.PREFIX.value))
            # Add a new announcement at AS 3, which will be better than the one
            # from 2 and cause a withdrawn route by 1 to 4
            ann.seed_asn = 3
            ann.as_path = (3,)
            engine.as_dict[3]._local_rib.add_ann(ann)
            Custom34ValidPrefix.victim_asns = {2, 3}

        if propagation_round == 2:  # third round
            ann = deepcopy(engine.as_dict[3]._local_rib.get_ann(Prefixes.PREFIX.value))
            ann.withdraw = True
            # Remove the original announcement from 3
            # The one from 2 is now the next-best
            engine.as_dict[3]._local_rib.remove_ann(Prefixes.PREFIX.value)
            engine.as_dict[3]._ribs_out.remove_entry(1, Prefixes.PREFIX.value)
            engine.as_dict[3]._send_q.add_ann(1, ann)
            Custom34ValidPrefix.victim_asns = {2}


config_034 = EngineTestConfig(
    name="034",
    desc="Test withdrawal mechanism choosing next best announcement",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom34ValidPrefix,
        BaseASCls=BGPAS,
        override_victim_asns={2},
    ),
    graph=Graph040(),
    propagation_rounds=4
)
