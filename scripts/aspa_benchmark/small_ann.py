from typing import Any, Optional

from bgpy.enums import Relationships


class SmallAnn:
    """Smaller BGP Announcement for speed"""

    __slots__ = ("prefix", "next_hop_asn", "as_path", "seed_asn", "recv_relationship")

    def __init__(
        self,
        *,
        prefix: str,
        next_hop_asn: int,
        as_path: tuple[int],
        seed_asn: Optional[int],
        recv_relationship: "Relationships",
        **kwargs
    ) -> None:
        self.prefix = prefix
        self.next_hop_asn = next_hop_asn
        self.as_path = as_path
        self.seed_asn = seed_asn
        self.recv_relationship = recv_relationship

    def copy(
        self, overwrite_default_kwargs: Optional[dict[Any, Any]] = None
    ) -> "SmallAnn":
        """Creates a new ann with proper sim attrs

        NOTE: This won't work with subclasses due to __slots__
        """

        # Replace seed asn and traceback end every time by default
        kwargs = {
            "prefix": self.prefix,
            "next_hop_asn": self.next_hop_asn,
            "as_path": self.as_path,
            "seed_asn": None,
            "recv_relationship": self.recv_relationship
        }

        if overwrite_default_kwargs:
            kwargs.update(overwrite_default_kwargs)

        return self.__class__(**kwargs)

    @property
    def origin(self) -> int:
        """Returns the origin of the announcement"""

        return self.as_path[-1]
