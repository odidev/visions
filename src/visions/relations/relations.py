from typing import Any, Optional

import attr
from multimethod import multimethod


def func_repr(func):
    return func.__name__ if hasattr(func, "__name__") else str("lambda")


def identity_transform(series: Any, state: dict) -> Any:
    return series


def default_relation(series: Any, state: dict) -> bool:
    return False


@attr.s(frozen=True)
class TypeRelation:
    """Relationship encoder between implementations of :class:`visions.types.type.VisionsBaseType`

    Defines a one to one relationship between two :class:`visions.types.type.VisionsBaseType` implementations,
    A and B, with respect to an underlying data series. In order to define a relationship we need
    two methods:

        - **is_relationship**, determines whether a series of type B can be alternatively represented as type A.
        - **transform**, provides a mechanism to convert the series from B -> A.

    For example, the series `pd.Series([1.0, 2.0, 3.0])` is encoded as a sequence of
    floats but in reality they are all integers.

    Examples:
        >>> from visions.types import Integer, Float
        >>> x = pd.Series([1.0, 2.0, 3.0])
        >>> state = dict()
        >>> relation = TypeRelation(Integer, Float)
        >>> relation.is_relation(x, state)
        True

        >>> relation.transform(x, state)
        pd.Series([1, 2, 3])
    """

    type = attr.ib()
    related_type = attr.ib()
    inferential = attr.ib()
    transformer = attr.ib(converter=multimethod, repr=func_repr)
    relationship = attr.ib(
        default=default_relation, converter=multimethod, repr=func_repr
    )

    def is_relation(self, series: Any, state: Optional[dict] = None) -> bool:
        if state is None:
            state = {}
        return self.relationship(series, state)

    def transform(self, series: Any, state: Optional[dict] = None) -> Any:
        if state is None:
            state = {}
        return self.transformer(series, state)

    def __str__(self):
        return f"{self.related_type}->{self.type}"


@attr.s(frozen=True)
class IdentityRelation(TypeRelation):
    relationship = attr.ib(repr=func_repr)  # converter=multimethod
    transformer = attr.ib(default=identity_transform, repr=func_repr)
    inferential = attr.ib(default=False)

    @relationship.default
    def make_relationship(self):
        return self.type.contains_op


@attr.s(frozen=True)
class InferenceRelation(TypeRelation):
    relationship = attr.ib(
        converter=multimethod, repr=func_repr, default=default_relation
    )
    transformer = attr.ib(
        converter=multimethod, default=identity_transform, repr=func_repr
    )
    inferential = attr.ib(default=True)
