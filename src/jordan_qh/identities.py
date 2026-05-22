"""Identity checks for small Jordan algebra examples."""

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
Product = Callable[[T, T], T]


def jordan_identity_holds(elements: Iterable[T], product: Product[T]) -> bool:
    """Check `(x^2 y) x = x^2 (y x)` on a finite set of elements."""
    items = tuple(elements)
    for x in items:
        x_squared = product(x, x)
        for y in items:
            left = product(product(x_squared, y), x)
            right = product(x_squared, product(y, x))
            if left != right:
                return False
    return True


def is_commutative(elements: Iterable[T], product: Product[T]) -> bool:
    """Check commutativity on a finite set of elements."""
    items = tuple(elements)
    return all(product(x, y) == product(y, x) for x in items for y in items)
