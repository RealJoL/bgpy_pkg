from bgpy.simulation_engine import BGPSimplePolicy, Announcement
from bgpy.enums import Relationships


class ASPVSimplePolicy(BGPSimplePolicy):
    """A Policy that deploys ASPV"""

    name: str = "ASPVSimple"

    # My current idea is to, akin to how roa works in this framework, embed the aspv validity into the announcement
    # itself. This would mean that we'd have to ensure the simulated attacker does not touch the validity itself but
    # only tries to embed himself in the path.

    def _valid_ann(self, ann: Announcement, *args, **kwargs) -> bool:
        """Returns announcement validity

        Returns false if invalid by ASPA,
        otherwise uses standard BGP (such as no loops, etc)
        to determine validity
        """

        if ann.as_path:
            return False

        # If our announcement traversed non ASPA speakers, we cannot validate our ASPA path
        # TODO Maybe find a way to differentiate this?
        if ann.aspa_up_length + ann.aspa_down_length + int(ann.aspa_peak_traversed) < len(ann.as_path):
            return False

        # If the AS_Path is one or two long it becomes valid
        if len(ann.as_path) <= 2:
            return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
                ann, *args, **kwargs
            )

        provider_set = self.as_.providers

        match ann.recv_relationship:
            case Relationships.PROVIDERS:
                pass # TODO Continue here
            case Relationships.PEERS:
                # Ignoring AS_SET and prepend collapse for now
                # Should be added if your Policy includes these

                if not ann.aspa_down_length == 0 and ann.aspa_up_length == len(ann.as_path) and not ann.aspa_peak_traversed:
                    ann.aspa_peak_traversed = True
                    # Route has only been propagated on a verified upstream so far -> Accept
                    return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
                        ann, *args, **kwargs
                    )
                else:
                    return False

            case Relationships.CUSTOMERS:
                # Ignoring AS_SET and prepend collapse for now
                # Should be added if your Policy includes these

                if not ann.aspa_down_length == 0 and ann.aspa_up_length == len(ann.as_path) and not ann.aspa_peak_traversed:
                    # Route has only been propagated on a verified upstream so far -> Accept
                    return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
                        ann, *args, **kwargs
                    )
                else:
                    return False
            case Relationships.ORIGIN:
                return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
                    ann, *args, **kwargs
                )
            case _:
                raise NotImplementedError

        # TODO This should probably call an ROA policy at some point as ASPA without ROA is kinda pointless.
        #  I am yet unsure if the framework supports this
        return super(ASPVSimplePolicy, self)._valid_ann(  # type: ignore
            ann, *args, **kwargs
        )
