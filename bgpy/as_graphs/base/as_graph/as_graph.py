from typing import Any, Callable, Optional

from frozendict import frozendict
from yamlable import yaml_info, YamlAble, yaml_info_decorate

from .base_as import AS

from bgpy.enums import ASGroups


# can't import into class due to mypy issue
# https://github.com/python/mypy/issues/7045
# Graph building functionality
from .graph_building_funcs import _gen_graph
from .graph_building_funcs import _add_relationships
from .graph_building_funcs import _make_relationships_tuples

# propagation rank building funcs
from .propagation_rank_funcs import _assign_propagation_ranks
from .propagation_rank_funcs import _assign_ranks_helper
from .propagation_rank_funcs import _get_propagation_ranks

# Customer cone funcs
from .customer_cone_funcs import _get_customer_cone_size
from .customer_cone_funcs import _get_cone_size_helper
from .customer_cone_funcs import _get_as_rank

import bgpy

from ..as_graph_info import ASGraphInfo


@yaml_info(yaml_tag="ASGraph")
class ASGraph(YamlAble):
    """BGP Topology"""

    # Graph building functionality
    _gen_graph = _gen_graph
    _add_relationships = _add_relationships
    _make_relationships_tuples = _make_relationships_tuples

    # propagation rank building funcs
    _assign_propagation_ranks = _assign_propagation_ranks
    _assign_ranks_helper = _assign_ranks_helper
    _get_propagation_ranks = _get_propagation_ranks

    # Customer cone funcs
    _get_customer_cone_size = _get_customer_cone_size
    _get_cone_size_helper = _get_cone_size_helper
    _get_as_rank = _get_as_rank

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # Fix this later once the system test framework is updated
        yaml_info_decorate(cls, yaml_tag=cls.__name__)

    def __init__(
        self,
        as_graph_info: "ASGraphInfo",
        BaseASCls: type[AS] = AS,
        BasePolicyCls: type[
            bgpy.simulation_engine.Policy
        ] = bgpy.simulation_engine.BGPSimplePolicy,
        customer_cones: bool = True,
        yaml_as_dict: Optional[frozendict[int, AS]] = None,
        yaml_ixp_asns: frozenset[int] = frozenset(),
        # Users can pass in any additional AS groups they want to keep track of
        additional_as_group_filters: frozendict[
            str, Callable[["ASGraph"], frozenset[AS]]
        ] = frozendict(),
    ):
        """Reads in relationship data from a TSV and generate graph"""

        if yaml_as_dict is not None:
            # We are coming from YAML, so init from YAML (for testing)
            self._set_yaml_attrs(yaml_as_dict, yaml_ixp_asns)
        else:
            # init as normal, through the as_graph_info
            self._set_non_yaml_attrs(
                as_graph_info, BaseASCls, BasePolicyCls, customer_cones
            )
        # Set the AS and ASN group groups
        self._set_as_groups(additional_as_group_filters)

    ##############
    # Init funcs #
    ##############

    def _set_yaml_attrs(
        self,
        yaml_as_dict: frozendict[int, AS],
        yaml_ixp_asns: frozenset[int],
    ) -> None:
        """Generates the AS Graph from YAML"""

        self.ixp_asns: frozenset[int] = yaml_ixp_asns
        self.as_dict: frozendict[int, AS] = yaml_as_dict
        # Convert ASNs to refs
        for as_obj in self.as_dict.values():
            as_obj.peers = tuple([self.as_dict[asn] for asn in as_obj.peers])
            as_obj.customers = tuple([self.as_dict[asn] for asn in as_obj.customers])
            as_obj.providers = tuple([self.as_dict[asn] for asn in as_obj.providers])

        # Used for iteration
        self.ases: tuple[AS, ...] = tuple(self.as_dict.values())
        self.propagation_ranks: tuple[
            tuple[AS, ...], ...
        ] = self._get_propagation_ranks()

    def _set_non_yaml_attrs(
        self,
        as_graph_info: ASGraphInfo,
        BaseASCls: type["AS"],
        BasePolicyCls: type["bgpy.simulation_engine.Policy"],
        customer_cones: bool,
    ) -> None:
        """Generates the AS graph normally (not from YAML)"""

        assert as_graph_info.ixp_asns is not None
        self.ixp_asns = as_graph_info.ixp_asns
        # Probably there is a better way to do this, but for now we
        # store this as a dict then later make frozendict, thus the type ignore
        self.as_dict = dict()  # type: ignore
        # Just adds all ASes to the dict, and adds ixp/input_clique info
        self._gen_graph(
            as_graph_info,
            BaseASCls,
            BasePolicyCls,
        )
        # Can't allow modification of the AS dict since other things like
        # as group filters will be broken then
        self.as_dict = frozendict(self.as_dict)
        # Adds references to all relationships
        self._add_relationships(as_graph_info)
        # Used for iteration
        self.ases: tuple[AS, ...] = tuple(self.as_dict.values())  # type: ignore
        # Remove duplicates from relationships and sort
        self._make_relationships_tuples()
        # Assign propagation rank to each AS
        self._assign_propagation_ranks()
        # Get the ranks for the graph
        self.propagation_ranks = self._get_propagation_ranks()
        # We don't run this every time since it has the runtime greater than the
        # entire graph generation
        if customer_cones:
            # Determine customer cones of all ases
            self._get_customer_cone_size()
            self._get_as_rank()

    def _set_as_groups(
        self,
        additional_as_group_filters: Optional[
            frozendict[str, Callable[["ASGraph"], frozenset[AS]]]
        ],
    ) -> None:
        """Sets the AS Groups"""

        as_group_filters: dict[str, Callable[["ASGraph"], frozenset[AS]]] = dict(
            self._default_as_group_filters
        )

        if additional_as_group_filters:
            as_group_filters.update(additional_as_group_filters)

        self.as_group_filters: frozendict[
            str, Callable[["ASGraph"], frozenset[AS]]
        ] = frozendict(as_group_filters)

        # Some helpful sets of ases for faster loops
        as_groups: dict[str, frozenset[AS]] = dict()
        asn_groups: dict[str, frozenset[int]] = dict()

        for as_group_key, filter_func in self.as_group_filters.items():
            as_groups[as_group_key] = filter_func(self)
            asn_groups[as_group_key] = frozenset(x.asn for x in filter_func(self))

        # Turn these into frozen dicts. They shouldn't be modified
        self.as_groups: frozendict[str, frozenset[AS]] = frozendict(as_groups)
        self.asn_groups: frozendict[str, frozenset[int]] = frozendict(asn_groups)

    @property
    def _default_as_group_filters(
        self,
    ) -> frozendict[str, Callable[["ASGraph"], frozenset[AS]]]:
        """Returns the default filter functions for AS groups"""

        def ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.ixp)

        def stub_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.stub and not x.ixp)

        def multihomed_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.multihomed and not x.ixp)

        def stubs_or_multihomed_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(
                x for x in as_graph if (x.stub or x.multihomed) and not x.ixp
            )

        def input_clique_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(x for x in as_graph if x.input_clique and not x.ixp)

        def etc_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(
                x
                for x in as_graph
                if not (x.stub or x.multihomed or x.input_clique or x.ixp)
            )

        def all_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
            return frozenset(list(as_graph))

        return frozendict(
            {
                ASGroups.IXPS.value: ixp_filter,
                ASGroups.STUBS.value: stub_no_ixp_filter,
                ASGroups.MULTIHOMED.value: multihomed_no_ixp_filter,
                ASGroups.STUBS_OR_MH.value: stubs_or_multihomed_no_ixp_filter,
                ASGroups.INPUT_CLIQUE.value: input_clique_no_ixp_filter,
                ASGroups.ETC.value: etc_no_ixp_filter,
                ASGroups.ALL_WOUT_IXPS.value: all_no_ixp_filter,
            }
        )

    ##############
    # Yaml funcs #
    ##############

    def __to_yaml_dict__(self) -> dict[str, Any]:  # type: ignore
        """Optional method called when yaml.dump is called"""

        return {
            "as_dict": {asn: as_obj for asn, as_obj in self.as_dict.items()},
            "ixp_asns": list(self.ixp_asns),
        }

    @classmethod
    def __from_yaml_dict__(cls, dct, yaml_tag) -> Any:
        """Optional method called when yaml.load is called"""

        return cls(
            ASGraphInfo(),
            yaml_as_dict=frozendict(dct["as_dict"]),
            yaml_ixp_asns=frozenset(dct["ixp_asns"]),
        )

    ##################
    # Iterator funcs #
    ##################

    # https://stackoverflow.com/a/7542261/8903959
    def __getitem__(self, index) -> AS:
        return self.ases[index]  # type: ignore

    def __len__(self) -> int:
        return len(self.as_dict)

    #def determine_announcement_aspa_validity(self, ann: Announcement) -> bool:

    #    k = 0
    #    l = 0
    #    passed_peak = False
    #    for i in range(len(ann.as_path) - 1, 1, -1):
    #        if self.ases[ann.as_path[i-1]] in self.ases[ann.as_path[i]].providers:

    #   self.ases
    #   pass
