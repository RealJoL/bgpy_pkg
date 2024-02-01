from pathlib import Path

from bgpy.simulation_engine import ROVSimplePolicy
from bgpy.enums import SpecialPercentAdoptions
from bgpy.simulation_engine.policies.aspv import ASPVSimplePolicy, ASPVSimpleExpensive
from bgpy.simulation_framework import (
    Simulation,
    SubprefixHijack,
    ScenarioConfig,
)
from bgpy.simulation_framework.scenarios import PathHijack


def main():
    """Runs the defaults"""

    output_dir_parent = Path(__file__).parent.parent.parent
    output_dir = output_dir_parent / "ms-thesis-joel-braun/script/bgppy_data/"

    # Simulation for the paper
    sim = Simulation(
        percent_adoptions=(
            SpecialPercentAdoptions.ONLY_ONE,
            0.1,
            0.2,
            0.5,
            0.8,
            SpecialPercentAdoptions.ALL_BUT_ONE,
        ),
        scenario_configs=(
            ScenarioConfig(
                ScenarioCls=PathHijack, AdoptPolicyCls=ASPVSimplePolicy
            ),
        ),
        output_dir=output_dir,
        num_trials=5,
        parse_cpus=1,
    )
    sim.run()


if __name__ == "__main__":
    main()
