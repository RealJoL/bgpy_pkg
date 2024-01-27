from frozendict import frozendict
from bgpy.enums import ASNs
from bgpy.tests.engine_tests.as_graph_infos import as_graph_info_000
from bgpy.tests.engine_tests.utils import EngineTestConfig

from bgpy.simulation_engine import BGPSimplePolicy, BGPSecSimplePolicy
from bgpy.simulation_framework import (
    ScenarioConfig,
    PrefixHijack,
    preprocess_anns_funcs,
)


desc = (
    "Origin spoofing prefix hijack with bgpsec simple\n"
    "BGPSec is security third, which doesn't amount to much\n"
    "AS 2 is saved, but as long as the chain is broken, AS 5"
    " is still hijacked"
)

ex_config_016 = EngineTestConfig(
    name="ex_016_origin_spoofing_hijack_bgpsec",
    desc=desc,
    scenario_config=ScenarioConfig(
        ScenarioCls=PrefixHijack,
        preprocess_anns_func=preprocess_anns_funcs.origin_spoofing_hijack,
        BasePolicyCls=BGPSecSimplePolicy,
        override_attacker_asns=frozenset({ASNs.ATTACKER.value}),
        override_victim_asns=frozenset({ASNs.VICTIM.value}),
        override_non_default_asn_cls_dict=frozendict(
            {
                ASNs.ATTACKER.value: BGPSimplePolicy,
            }
        ),
    ),
    as_graph_info=as_graph_info_000,
)