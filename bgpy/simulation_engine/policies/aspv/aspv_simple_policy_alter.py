import itertools

from bgpy.enums import Relationships
from bgpy.simulation_engine import Announcement
from bgpy.simulation_engine.policies.rov import ROVSimplePolicy
from bgpy.simulation_engine.policies.bgp import BGPSimplePolicy


class ASPVSimpleExpensive(ROVSimplePolicy):
    """A Policy that deploys ASPV as suggested in the internet draft"""

    name: str = "ASPVSimpleExpensive"

    # This implementation is closer to what was suggested in the IETF draft

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
                if not self.upstream_path_validity(as_path=ann.as_path):
                    return False
            case Relationships.PEERS:
                if not self.upstream_path_validity(as_path=ann.as_path):
                    return False
            case Relationships.PROVIDERS:
                if not self.downstream_path_validity(as_path=ann.as_path):
                    return False
            case _:
                raise NotImplementedError

        return super(ASPVSimpleExpensive, self)._valid_ann(  # type: ignore
            ann, *args, **kwargs
        )

    def upstream_path_validity(self, as_path: tuple[int]) -> bool:
        if len(as_path) == 1:
            return True

        as_obj_path = self.search_for_path(as_path)

        if len(as_obj_path) != len(as_path):
            # There actually exists not connection between ASes
            return False

        path_length = 2
        for as_i, as_j in itertools.pairwise(list(reversed(as_obj_path))[1:]):
            if not hop_validity(as_i, as_j):
                return False
            else:
                path_length += 1

        return True

    def downstream_path_validity(self, as_path: tuple[int]) -> bool:
        if len(as_path) <= 2:
            return True

        as_obj_path = self.search_for_path(as_path)

        if len(as_obj_path) != len(as_path):
            # Couldn't find all members of the path to verify validity
            # We can do this despite ROV/BGPPolicy ASes on the path because
            # they still possess relationships, despite not having ASPA attestation
            return False

        u_min = 0
        reversed_as_obj_path = list(reversed(as_obj_path))
        for u in range(1, len(as_obj_path)):
            as_i, as_j = reversed_as_obj_path[u - 1], reversed_as_obj_path[u]
            # This assumes that an ASes customers also see that AS as provider
            if hop_validity(as_j, as_i):
                u_min += 1
            else:
                break
            # TODO Verify

        if u_min == 0:
            u_min = len(as_obj_path)

        v_max = 0
        for v in range(0, len(as_obj_path) - 1):
            as_i, as_j = as_obj_path[v + 1], as_obj_path[v]
            if hop_validity(as_i, as_j):
                v_max += 1
            else:
                break

        if u_min <= v_max:
            return False

        # Now calculate up ramp
        k: int = 1
        for as_i, as_j in itertools.pairwise(list(reversed(as_obj_path))[2:]):
            if hop_validity(as_i, as_j):
                k += 1
            else:
                break

        # Now calculate down ramp
        l: int = 1
        for as_i, as_j in itertools.pairwise(as_obj_path[1:]):
            if hop_validity(as_i, as_j):
                l += 1
            else:
                break

        return l - k <= 1

    # Takes an AS from which to begin the search and returns the tuple representing the AS objects contained in the path
    def search_for_path(self, as_path: tuple[int]) -> tuple:

        as_obj_path = []
        cur_as_obj = self.as_

        for asn in as_path:
            # Get the AS corresponding to the ASN from the list of connected ASes
            in_customers = next((cur_as for cur_as in cur_as_obj.customers if cur_as.asn == asn), None)
            in_peers = next((cur_as for cur_as in cur_as_obj.peers if cur_as.asn == asn), None)
            in_providers = next((cur_as for cur_as in cur_as_obj.providers if cur_as.asn == asn), None)

            # Don't have any specific order in mind, maybe adjust later?
            if in_customers:
                as_obj_path.append(in_customers)
                cur_as_obj = in_customers
                continue
            if in_peers:
                as_obj_path.append(in_peers)
                cur_as_obj = in_peers
                continue
            if in_providers:
                as_obj_path.append(in_providers)
                cur_as_obj = in_providers
                continue
            return tuple(as_obj_path)
        return tuple(as_obj_path)


def get_as_from_customers(as_obj, asn: int):
    return next((cur_as for cur_as in as_obj.customers if cur_as.asn == asn), None)


def get_as_from_provider(as_obj, asn: int):
    return next((cur_as for cur_as in as_obj.providers if cur_as.asn == asn), None)


# Return true if the hop validity of AS(i) and AS(j) is provider
def hop_validity(as_i, as_j) -> bool:
    return as_j in as_i.providers
