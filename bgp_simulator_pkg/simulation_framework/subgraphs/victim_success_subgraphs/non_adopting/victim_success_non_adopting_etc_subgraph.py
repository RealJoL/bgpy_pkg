from ..victim_success_subgraph import VictimSuccessSubgraph
from .....enums import ASTypes
from .....enums import Outcomes


class VictimSuccessNonAdoptingEtcSubgraph(VictimSuccessSubgraph):
    """A graph for attacker success for etc ASes that don't adopt"""

    name: str = "victim_success_non_adopting_etc"

    def _get_subgraph_key(self, scenario, *args) -> str:  # type: ignore
        """Returns the key to be used in shared_data on the subgraph"""

        return self._get_as_type_pol_outcome_perc_k(
            ASTypes.ETC, scenario.BaseASCls, Outcomes.VICTIM_SUCCESS)

    @property
    def y_axis_label(self) -> str:
        """returns y axis label"""

        return Outcomes.VICTIM_SUCCESS.name