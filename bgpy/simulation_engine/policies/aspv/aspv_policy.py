from .aspv_simple_policy import ASPVSimplePolicy
from bgpy.simulation_engine.policies.rov.rov_policy import ROVPolicy


class ASPVPolicy(ASPVSimplePolicy, ROVPolicy):
    name: str = "ASPV"
