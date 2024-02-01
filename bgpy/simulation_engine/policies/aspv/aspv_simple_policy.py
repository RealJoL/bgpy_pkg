from copy import copy
from typing import Optional, Any

from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement
from bgpy.simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy

class ASPVSimplePolicy(ROVSimplePolicy):
    """A Policy that deploys ASPV"""

    name: str = "ASPVSimple"

    # My current idea is to, akin to how roa works in this framework, embed the aspv validity into the announcement
    # itself. This would mean that we'd have to ensure the simulated attacker does not touch the validity itself but
    # only tries to embed himself in the path.
    # TODO Document my idea more extensively

    def _valid_ann(self, ann: Announcement, *args, **kwargs) -> bool:
        """Returns announcement validity

        Returns false if invalid by ASPV, calls ROVSimplePolicy if path seems correct
        """

        if not ann.as_path:
            return False

        from_rel = args[0]

        # Ignoring AS_SET and prepend collapse for now
        # Should be added if your Policy includes these

        match from_rel:
            case Relationships.ORIGIN:
                # Verify that the path actually originates from origin AS
                if len(ann.as_path) != 1:
                    # Route supposedly announced by Origin, but path length > 2
                    return False

            case Relationships.CUSTOMERS:
                if len(ann.as_path) == 1:
                    # Path originating from customer (should be handled by origin anyway)
                    pass
                else:
                    # If our announcement traversed non ASPA speakers, we cannot validate our ASPA path
                    # TODO Maybe find a way to differentiate this into invalid and unknown?
                    if (ann.aspa_down_length == 0 and ann.aspa_up_length + 1 == len(ann.as_path)
                            and not ann.aspa_crossed_unattested):
                        # Route has only been propagated on a verified upstream so far -> Accept
                        pass
                    else:
                        return False
            case Relationships.PEERS:
                if len(ann.as_path) == 1:
                    # Path originating from peer (should be handled by origin anyway)
                    pass
                elif (ann.aspa_down_length == 0 and ann.aspa_up_length + 1 == len(ann.as_path)
                      and not ann.aspa_crossed_unattested):
                    pass
                    # Route has only been propagated on a verified upstream so far -> Accept
                else:
                    return False

            case Relationships.PROVIDERS:
                if len(ann.as_path) <= 2:
                    # Path received by the provider are accepted as legitimate as long as their
                    # length is max. 2.
                    pass
                elif (ann.aspa_up_length + ann.aspa_down_length + int(ann.aspa_crossed_unattested) + 1
                      < len(ann.as_path)):
                    return False
                else:
                    # If this is the first movement down on the AS_PATH but there were some up movements already,
                    # the path peak has been crossed
                    pass
            case _:
                raise NotImplementedError

        return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
            ann, *args, **kwargs
        )

    def _copy_and_process(
            self,
            ann: "Ann",
            recv_relationship: "Relationships",
            overwrite_default_kwargs: Optional[dict[Any, Any]] = None,
    ) -> "Ann":

        new_ann_aspa_up = ann.aspa_up_length
        new_ann_aspa_down = ann.aspa_down_length
        new_ann_aspa_peak = ann.aspa_crossed_unattested

        match recv_relationship:
            case Relationships.ORIGIN:
                # Adjust the path corresponding to the actual AS relationship
                # as we can't infer it from the recv_relationship
                # Modify the announcement accordingly
                from_as = ann.as_path[0]
                if from_as in [as_obj.asn for as_obj in self.as_.customers]:
                    new_ann_aspa_up = ann.aspa_up_length + 1
                elif from_as in [as_obj.asn for as_obj in self.as_.providers]:
                    new_ann_aspa_down = ann.aspa_down_length + 1
                elif from_as in [as_obj.asn for as_obj in self.as_.peers]:
                    new_ann_aspa_peak = True

            case Relationships.CUSTOMERS:
                new_ann_aspa_up = ann.aspa_up_length + 1
            case Relationships.PEERS:
                new_ann_aspa_peak = True
            case Relationships.PROVIDERS:
                new_ann_aspa_down = ann.aspa_down_length + 1
            case _:
                raise NotImplementedError

        if overwrite_default_kwargs:
            self.default_kwargs = overwrite_default_kwargs

        new_announcement = ann.copy(
            {
                "as_path": (self.as_.asn,) + ann.as_path,
                "recv_relationship": recv_relationship,
                "aspa_up_length": new_ann_aspa_up,
                "aspa_down_length": new_ann_aspa_down,
                "aspa_crossed_unattested": new_ann_aspa_peak,
            }
        )

        return new_announcement

    def receive_ann(self, ann: "Ann", accept_withdrawals: bool = False) -> None:
        super().receive_ann(copy(ann), accept_withdrawals)
