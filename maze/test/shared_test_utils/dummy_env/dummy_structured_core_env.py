"""Dummy structured (multi-agent, with two agents) core environment."""

from typing import Tuple, Dict, Any, Union, Optional

import gym
import numpy as np

from maze.core.annotations import override
from maze.core.env.core_env import CoreEnv
from maze.core.env.structured_env import StepKeyType
from maze.core.events.pubsub import Pubsub
from maze.test.shared_test_utils.dummy_env.reward.base import RewardAggregator, DummyEnvEvents


class DummyStructuredCoreEnvironment(CoreEnv):
    """Dummy structured (multi-agent, with two agents) core environment.

    :param observation_space: The observation space to sample observations from
    """

    def __init__(self, observation_space: gym.spaces.space.Space):
        super().__init__()

        self.pubsub = Pubsub(self.context.event_service)
        self.dummy_core_events = self.pubsub.create_event_topic(DummyEnvEvents)

        self.reward_aggregator = RewardAggregator()
        self.pubsub.register_subscriber(self.reward_aggregator)

        self.observation_space = observation_space

        self.current_agent = 0

    @override(CoreEnv)
    def step(self, maze_action: Dict) -> Tuple[Dict[str, np.ndarray], float, bool, Optional[Dict]]:
        """Switch agents, increment env step after the second agent"""
        if self.current_agent == 0:
            # No reward yet
            self.current_agent = 1
            return self.get_maze_state(), 0, False, {}
        else:
            # Calculate reward, increment env step
            self.current_agent = 0
            self.context.increment_env_step()
            return self.get_maze_state(), self.reward_aggregator.summarize_reward(), False, {}

    @override(CoreEnv)
    def get_maze_state(self) -> Dict[str, np.ndarray]:
        """Sample a random observation."""
        return self.observation_space.sample()

    @override(CoreEnv)
    def reset(self) -> Dict[str, np.ndarray]:
        """Reset current agent"""
        self.current_agent = 0
        return self.get_maze_state()

    @override(CoreEnv)
    def seed(self, seed: int) -> None:
        """No randomness in this env."""
        pass

    @override(CoreEnv)
    def get_serializable_components(self) -> Dict[str, Any]:
        """No components required/available"""
        return {}

    @override(CoreEnv)
    def get_renderer(self) -> None:
        """No renderer available"""
        return None

    @override(CoreEnv)
    def actor_id(self) -> Tuple[Union[str, int], int]:
        """Single-step, two-agent environment"""
        return 0, self.current_agent

    @property
    @override(CoreEnv)
    def agent_counts_dict(self) -> Dict[StepKeyType, int]:
        """Single-step, two-agent environment"""
        return {0: 2}

    @override(CoreEnv)
    def is_actor_done(self) -> bool:
        """Actors are never done"""
        return False

    @override(CoreEnv)
    def close(self) -> None:
        """Nothing to clean up"""
        pass
