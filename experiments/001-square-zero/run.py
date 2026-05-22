"""Experiment 001 placeholder."""

from jordan_qh.examples import square_zero_extension_shape


def main() -> None:
    spec = square_zero_extension_shape(1, 1)
    print({"status": "not run yet", "total_dimension": spec.total_dimension})


if __name__ == "__main__":
    main()
