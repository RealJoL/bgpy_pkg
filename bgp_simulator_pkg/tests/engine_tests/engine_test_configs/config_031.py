from ..graphs import Graph040
from ..utils import EngineTestConfig


from ....simulation_engine import BGPSimpleAS
from ....simulation_framework import ValidPrefix, ScenarioConfig


class Custom31ValidPrefix(ValidPrefix):
    """A valid prefix engine input"""

    __slots__ = ()

    def _get_announcements(self, *args, **kwargs):
        vic_ann = super()._get_announcements()[0]
        # Add 1 to the path so AS 1 rejects this
        vic_ann.as_path = (vic_ann.origin, 1, vic_ann.origin)
        return (vic_ann,)


config_031 = EngineTestConfig(
    name="031",
    desc="Test loop prevention mechanism",
    scenario_config=ScenarioConfig(
        ScenarioCls=Custom31ValidPrefix,
        override_victim_asns={4},
        BaseASCls=BGPSimpleAS
    ),
    graph=Graph040()
)
