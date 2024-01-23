from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement
from bgpy.simulation_engine.policies.rov import ROVSimplePolicy


class ASPVSimplePolicy(ROVSimplePolicy):
    """A Policy that deploys ASPV"""

    name: str = "ASPVSimple"

    # My current idea is to, akin to how roa works in this framework, embed the aspv validity into the announcement
    # itself. This would mean that we'd have to ensure the simulated attacker does not touch the validity itself but
    # only tries to embed himself in the path.
    # TODO Document my idea more extensively

    def _valid_ann(self, ann: Announcement, *args, **kwargs) -> bool:
        """Returns announcement validity

        Returns false if invalid by ASPA,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        if ann.as_path:
            return False

        # If the AS_Path is one or two long it becomes valid
        # Ignoring AS_SET and prepend collapse for now
        # Should be added if your Policy includes these
        if len(ann.as_path) <= 2:
            match ann.recv_relationship:
                # Even though the path is valid, we still need to modify our announcement
                # fields to not cause problems in propagation to further ASes
                case Relationships.PROVIDERS:
                    ann.aspa_down_length += 1
                case Relationships.CUSTOMERS:
                    ann.aspa_up_length += 1
                case Relationships.PEERS:
                    ann.aspa_crossed_unattested_or_peak = True
                case Relationships.ORIGIN:
                    pass
        else:
            match ann.recv_relationship:
                case Relationships.PROVIDERS:
                    # If our announcement traversed non ASPA speakers, we cannot validate our ASPA path
                    # TODO Maybe find a way to differentiate this?
                    if (ann.aspa_up_length + ann.aspa_down_length + int(ann.aspa_crossed_unattested_or_peak)
                            < len(ann.as_path)):
                        return False
                    else:
                        # If this is the first movement down on the AS_PATH but there were some up movements already,
                        # the path peak has been crossed
                        if ann.aspa_down_length == 0 and ann.aspa_up_length != 0:
                            ann.aspa_crossed_unattested_or_peak = True
                        ann.aspa_down_length += 1
                case Relationships.PEERS:
                    if (ann.aspa_down_length != 0 and ann.aspa_up_length == len(ann.as_path)
                            and not ann.aspa_crossed_unattested_or_peak):
                        ann.aspa_crossed_unattested_or_peak = True
                        # Route has only been propagated on a verified upstream so far -> Accept
                    else:
                        return False

                case Relationships.CUSTOMERS:
                    if (ann.aspa_down_length != 0 and ann.aspa_up_length == len(ann.as_path)
                            and not ann.aspa_crossed_unattested_or_peak):
                        # Route has only been propagated on a verified upstream so far ->
                        ann.aspa_up_length += 1
                    else:
                        return False
                case Relationships.ORIGIN:
                    # Route announced by ourselves, will accept to not cause loop
                    pass
                case _:
                    raise NotImplementedError

        # TODO This should probably call an ROA policy at some point as ASPA without ROA is kinda pointless.
        #  I am yet unsure if the framework supports this
        return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
            ann, *args, **kwargs
        )
