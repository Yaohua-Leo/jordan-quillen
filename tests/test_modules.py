from jordan_qh.examples import square_zero_extension_shape
from jordan_qh.modules import SquareZeroExtensionSpec


def test_square_zero_extension_shape_records_dimensions() -> None:
    spec = square_zero_extension_shape(base_dimension=2, module_dimension=3)

    assert isinstance(spec, SquareZeroExtensionSpec)
    assert spec.total_dimension == 5
    assert spec.status == "not implemented"
