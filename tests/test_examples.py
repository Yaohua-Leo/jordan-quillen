from jordan_qh import __version__
from jordan_qh.examples import (
    one_dimensional_unital_algebra,
    zero_multiplication_algebra,
)


def test_package_version_exists() -> None:
    assert __version__ == "0.1.0"


def test_example_factories_have_expected_dimensions() -> None:
    assert zero_multiplication_algebra(4).dimension == 4
    assert one_dimensional_unital_algebra().dimension == 1
