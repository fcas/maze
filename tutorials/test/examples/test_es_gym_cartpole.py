"""Contains unit tests for examples."""
from tutorials.examples.es_gym_cartpole import main


def test_es_gym_cartpole():
    """ unit tests """
    main(max_epochs=1)
