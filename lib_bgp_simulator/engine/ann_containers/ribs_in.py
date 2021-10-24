from collections import defaultdict, namedtuple
import dataclasses

from yamlable import YamlAble, yaml_info

from .ann_container import AnnContainer

from ...announcements import Announcement
from ...enums import Relationships



@yaml_info(yaml_tag="AnnInfo")
@dataclasses.dataclass
class AnnInfo(YamlAble):
    unprocessed_ann: Announcement
    recv_relationship: Relationships


class RIBsIn(AnnContainer):
    """Incomming announcements for a BGP AS

    neighbor: {prefix: (announcement, relationship)}
    """

    __slots__ = tuple()

    def __init__(self, _info=None):
        self._info = _info if _info is not None else defaultdict(dict)

    def get_unprocessed_ann_recv_rel(self, neighbor_asn: int, prefix: str):
        return self._info[neighbor_asn].get(prefix)

    def add_unprocessed_ann(self,
                            unprocessed_ann: Announcement,
                            recv_relationship: Relationships):
        ann = unprocessed_ann
        self._info[ann.as_path[0]][ann.prefix] = AnnInfo(
            unprocessed_ann=unprocessed_ann,
            recv_relationship=recv_relationship)

    def get_ann_infos(self, prefix: str):
        for prefix_ann_info in self._info.values():
            yield prefix_ann_info.get(prefix, (None, None))

    def remove_entry(self, neighbor_asn: int, prefix: int):
        del self._info[neighbor_asn][prefix]
