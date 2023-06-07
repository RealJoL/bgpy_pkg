# This should be made compatible with mypy, but I have no time

from pathlib import Path
from typing import Dict, Any

from .diagram import Diagram
from .engine_test_config import EngineTestConfig
from .simulator_codec import SimulatorCodec
from ....simulation_engine import SimulationEngine


class EngineTester:
    """Tests an engine run"""

    def __init__(
        self,
        base_dir: Path,
        conf: EngineTestConfig,
        overwrite: bool = False,
        codec: SimulatorCodec = SimulatorCodec(),
    ):
        self.conf = conf
        self.overwrite = overwrite
        self.codec = codec
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Creates directory for this specific test
        self.test_dir: Path = self.base_dir / self.conf.name  # type: ignore
        self.test_dir.mkdir(exist_ok=True)

    def test_engine(self):
        """Tests an engine run

        Takes in a scenario (initialized with adopt ASN, atk and vic ASN,
        and a graph
        The scenario + graph are used to build and seed the engine
        After the engine is seeded, the engine is run
        Data is collected from the engine
        The engine and traceback are output to YAML
        We then compare the current run's traceback and engine
            to the ground truth
        """

        # Get a fresh copy of the scenario
        scenario = self.conf.scenario_config.ScenarioCls(
            scenario_config=self.conf.scenario_config
        )
        # Get's an engine that has been set up
        engine = self._get_engine(scenario)
        # Run engine
        for propagation_round in range(self.conf.propagation_rounds):  # type: ignore
            engine.run(propagation_round=propagation_round, scenario=scenario)
            kwargs = {
                "engine": engine,
                "scenario": scenario,
                "propagation_round": propagation_round,
            }
            # By default, this is a no op
            scenario.post_propagation_hook(**kwargs)

        # Get traceback results {AS: Outcome}
        outcomes = self.conf.SubgraphCls()._get_engine_outcomes(engine, scenario)
        # Convert this to just be {ASN: Outcome} (Not the AS object)
        outcomes_yaml = {as_obj.asn: result for as_obj, result in outcomes.items()}
        # Get shared_data
        shared_data: Dict[Any, Any] = dict()
        self.conf.SubgraphCls()._add_traceback_to_shared_data(
            shared_data, engine, scenario, outcomes
        )
        # Store engine and traceback YAML
        self._store_yaml(engine, outcomes_yaml, shared_data)
        # Create diagrams before the test can fail
        self._generate_diagrams(scenario, shared_data)
        # Compare the YAML's together
        self._compare_yaml()

    def _get_engine(self, scenario):
        """Creates and engine and sets it up for runs"""

        engine = SimulationEngine(
            BaseASCls=self.conf.scenario_config.BaseASCls,
            peer_links=self.conf.graph.peer_links,  # type: ignore
            cp_links=self.conf.graph.customer_provider_links,  # type: ignore
        )  # type: ignore

        scenario.setup_engine(engine, 0, scenario)
        return engine

    def _store_yaml(self, engine, outcomes, shared_data):
        """Stores YAML for the engine, outcomes, and shared_data.

        If ground truth doesn't exist, create it
        """

        # Save engine
        self.codec.dump(engine, path=self.engine_guess_path)
        # Save engine as ground truth if ground truth doesn't exist
        if not self.engine_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(engine, path=self.engine_ground_truth_path)
        # Save outcomes
        self.codec.dump(outcomes, path=self.outcomes_guess_path)
        # Save outcomes as ground truth if ground truth doesn't exist
        if not self.outcomes_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(outcomes, path=self.outcomes_ground_truth_path)
        self.codec.dump(shared_data, path=self.shared_data_guess_path)
        # Save shared_data as ground truth if ground truth doesn't exist
        if not self.shared_data_ground_truth_path.exists() or self.overwrite:
            self.codec.dump(shared_data, path=self.shared_data_ground_truth_path)

    def _generate_diagrams(self, scenario, shared_data):
        """Generates diagrams"""

        # Load engines
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        # Load outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)

        # Write guess graph
        Diagram().generate_as_graph(
            engine_guess,
            scenario,  # type: ignore
            outcomes_guess,
            f"({self.conf.name} Guess)\n{self.conf.desc}",  # type: ignore
            shared_data,
            path=self.test_dir / "guess.gv",
            view=False,
        )
        # Write ground truth graph
        Diagram().generate_as_graph(
            engine_gt,
            scenario,  # type: ignore
            outcomes_gt,
            f"({self.conf.name} Ground Truth)\n"  # type: ignore
            f"{self.conf.desc}",  # type: ignore
            shared_data,
            path=self.test_dir / "ground_truth.gv",
            view=False,
        )

    def _compare_yaml(self):
        """Compares YAML for ground truth vs guess for engine and outcomes"""

        # Compare Engine
        engine_guess = self.codec.load(self.engine_guess_path)
        engine_gt = self.codec.load(self.engine_ground_truth_path)
        assert engine_guess == engine_gt
        # Compare outcomes
        outcomes_guess = self.codec.load(self.outcomes_guess_path)
        outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)
        assert outcomes_guess == outcomes_gt
        # Compare shared_data
        shared_data_guess = self.codec.load(self.shared_data_guess_path)
        shared_data_gt = self.codec.load(self.shared_data_ground_truth_path)
        assert shared_data_guess == shared_data_gt

    #########
    # Paths #
    #########

    @property
    def engine_ground_truth_path(self) -> Path:
        """Returns the path to the engine's ground truth YAML"""

        return self.test_dir / "engine_gt.yaml"

    @property
    def engine_guess_path(self) -> Path:
        """Returns the path to the engine's guess YAML"""

        return self.test_dir / "engine_guess.yaml"

    @property
    def outcomes_ground_truth_path(self) -> Path:
        """Returns the path to the outcomes ground truth YAML"""

        return self.test_dir / "outcomes_gt.yaml"

    @property
    def outcomes_guess_path(self) -> Path:
        """Returns the path to the outcomes guess YAML"""

        return self.test_dir / "outcomes_guess.yaml"

    @property
    def shared_data_ground_truth_path(self) -> Path:
        """Returns the path to the shared_data ground truth YAML"""

        return self.test_dir / "shared_data_gt.yaml"

    @property
    def shared_data_guess_path(self) -> Path:
        """Returns the path to the shared_data guess YAML"""

        return self.test_dir / "shared_data_guess.yaml"
