from typing import TYPE_CHECKING

from bgpy.enums import Relationships
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

if TYPE_CHECKING:
    from bgpy.as_graphs import AS
    from bgpy.simulation_engine import Announcement as Ann


class OnlyToCustomersSimplePolicy(BGPSimplePolicy):
    """An Policy that deploys OnlyToCustomers"""

    name: str = "OnlyToCustomersSimple"

    def _valid_ann(self, ann: "Ann", from_rel: Relationships) -> bool:  # type: ignore
        """Returns False if from peer/customer when only_to_customers is set"""

        # If ann.only_to_customers is set, only accept from a provider
        if ann.only_to_customers and from_rel.value != Relationships.PROVIDERS.value:
            return False
        else:
            return super()._valid_ann(ann, from_rel)

    def _policy_propagate(  # type: ignore
        self,
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """If propagating to customers and only_to_customers isn't set, set it"""

        if (
            propagate_to.value == Relationships.CUSTOMERS.value
            and not ann.only_to_customers
        ):
            ann = ann.copy({"only_to_customers": True})
            self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
            return True
        else:
            return False
