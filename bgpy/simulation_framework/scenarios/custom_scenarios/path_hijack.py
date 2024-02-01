from bgpy.enums import Timestamps, Relationships, Prefixes
from bgpy.simulation_engine.announcement import Announcement
from bgpy.simulation_framework.scenarios.scenario import Scenario


class PathHijack(Scenario):
    def _get_announcements(self, *args, **kwargs) -> tuple[Announcement, ...]:

        # TODO Confirm correctness of implementation
        #  I assume appending the origin AS to the announced route would be ROV conformant
        #  I also employed subprefix hijack at the same time, I'll remove it later
        #  See here for route leak prevented by ASPA:
        #  https://www.manrs.org/2023/02/unpacking-the-first-route-leak-prevented-by-aspa/

        anns = list()
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(victim_asn,),
                    next_hop_asn=victim_asn,
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )

        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix="1.2.0.0/32",
                    as_path=(attacker_asn, victim_asn),
                    next_hop_asn=attacker_asn,
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.PROVIDERS,
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix="1.2.0.1/32",
                    as_path=(attacker_asn, victim_asn),
                    next_hop_asn=attacker_asn,
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn ,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.PEERS,
                )
            )
            anns.append(
                self.scenario_config.AnnCls(
                    prefix="1.2.0.2/32",
                    as_path=(attacker_asn, victim_asn),
                    next_hop_asn=attacker_asn,
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    roa_valid_length=True,
                    roa_origin=victim_asn,
                    recv_relationship=Relationships.CUSTOMERS,
                )
            )

        return tuple(anns)
