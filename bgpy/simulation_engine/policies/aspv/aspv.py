from bgpy.simulation_engine import ROVSimplePolicy, BGPPolicy


class ASPVPolicy(ROVSimplePolicy, BGPPolicy):
    name: str = "ASPV"
