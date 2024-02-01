from dataclasses import dataclass, asdict, replace
from typing import Any, Optional, TYPE_CHECKING

from yamlable import YamlAble, yaml_info

if TYPE_CHECKING:
    from bgpy.enums import Relationships


@yaml_info(yaml_tag="Announcement")
@dataclass(slots=True, frozen=True)
class Announcement(YamlAble):
    """BGP Announcement"""

    prefix: str
    # Equivalent to the next hop in a normal BGP announcement
    next_hop_asn: int
    as_path: tuple[int]
    seed_asn: Optional[int]
    recv_relationship: "Relationships"

    #############################
    # Optional attributes below #
    #############################
    # If you aren't using the policies listed below,
    # You can create an announcement class without them
    # for a much faster runtime. Announcement copying is
    # the bottleneck for BGPy, smaller announcements copy
    # much faster across the AS topology

    # This currently is unused. Depending on some results from
    # our in-progress publications it may be used in the future
    # For now, we just set the timestamp of the victim to 0,
    # and timestamp of the attacker to 1
    timestamp: int = 0
    # Used for classes derived from BGPPolicy
    withdraw: bool = False
    # Deprecated attr. This existed before next_hop_asn
    # next_hop_asn should be set instead of this now
    # Currently functionality is unchanged but it just
    # shouldn't be used.
    traceback_end: bool = False
    # ROV, ROV++ optional attributes
    roa_valid_length: Optional[bool] = None
    roa_origin: Optional[int] = None
    # BGPsec optional attributes
    # BGPsec next ASN that should receive the control plane announcement
    # NOTE: this is the opposite direction of next_hop, for the data plane
    bgpsec_next_asn: Optional[int] = None
    bgpsec_as_path: tuple[int, ...] = ()
    # RFC 9234 OTC attribute (Used in OnlyToCustomers Policy)
    only_to_customers: Optional[bool] = None
    """Number of ASes implementing ASPA already traversed on the upstream ramp.
     Decribed as K in internet draft."""
    aspa_up_length: int = 0
    """ Number of ASes implementing ASPA already traversed on the downstream ramp.
     Not to be confused with the letter L in ASPA internet draft."""
    aspa_down_length: int = 0
    """ Boolean indicating if the peak of the ASPA path (traversing two equal rank/non-attested ASes)
    has already been passed. This replaces the K and L check on on path propagation from provider."""
    aspa_crossed_unattested: bool = False

    def prefix_path_attributes_eq(self, ann: Optional["Announcement"]) -> bool:

        """Checks prefix and as path equivalency"""

        if ann is None:
            return False
        elif isinstance(ann, Announcement):
            return (ann.prefix, ann.as_path) == (self.prefix, self.as_path)
        else:
            raise NotImplementedError

    def copy(
            self, overwrite_default_kwargs: Optional[dict[Any, Any]] = None
    ) -> "Announcement":

        """Creates a new ann with proper sim attrs"""

        # Replace seed asn and traceback end every time by default
        kwargs = {"seed_asn": None, "traceback_end": False}
        if overwrite_default_kwargs:
            kwargs.update(overwrite_default_kwargs)

        # Mypy says it gets this wrong
        # https://github.com/microsoft/pyright/issues/1047#issue-705124399
        return replace(self, **kwargs)  # type: ignore

    def bgpsec_valid(self, asn: int) -> bool:
        """Returns True if valid by BGPSec else False"""

        return self.bgpsec_next_asn == asn and self.bgpsec_as_path == self.as_path

    @property
    def invalid_by_roa(self) -> bool:
        """Returns True if Ann is invalid by ROA

        False means ann is either valid or unknown
        """
        # Not covered by ROA, unknown
        if self.roa_origin is None:
            return False
        else:
            return self.origin != self.roa_origin or not self.roa_valid_length

    @property
    def valid_by_roa(self) -> bool:
        """Returns True if Ann is valid by ROA

        False means ann is either invalid or unknown
        """

        # Need the bool here for mypy, ugh
        return bool(self.origin == self.roa_origin and self.roa_valid_length)

    @property
    def unknown_by_roa(self) -> bool:
        """Returns True if ann is not covered by roa"""

        return not self.invalid_by_roa and not self.valid_by_roa

    @property
    def covered_by_roa(self) -> bool:
        """Returns if an announcement has a roa"""

        return not self.unknown_by_roa

    @property
    def roa_routed(self) -> bool:
        """Returns bool for if announcement is routed according to ROA"""

        return self.roa_origin != 0

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]

    def __str__(self) -> str:
        return f"{self.prefix} {self.as_path} {self.recv_relationship}"

    def __hash__(self):
        """Hash func. Needed for ROV++"""
        return hash(str(self))

    ##############
    # Yaml funcs #
    ##############

    @classmethod
    def __from_yaml_dict__(
            cls: type["Announcement"], dct: dict[str, Any], yaml_tag: Any
    ) -> "Announcement":
        """This optional method is called when you call yaml.load()"""

        return cls(**dct)

    def __to_yaml_dict__(self) -> dict[str, Any]:
        """This optional method is called when you call yaml.dump()"""

        return asdict(self)
