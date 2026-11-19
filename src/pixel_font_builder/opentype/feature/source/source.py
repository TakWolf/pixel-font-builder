from abc import abstractmethod
from collections.abc import Iterable
from copy import copy, deepcopy
from typing import Any, Protocol, Self, runtime_checkable

from pixel_font_builder.opentype.feature.source.input import FeatureInput


@runtime_checkable
class FeatureSource(Protocol):
    """An ordered source of FEA inputs parsed as one compilation unit.

    All inputs share one parser and therefore one symbol scope. Definitions such
    as glyph classes and lookups can be referenced by later inputs. Each input
    independently defines how its relative ``include()`` paths are resolved.
    """

    @abstractmethod
    def __copy__(self) -> Self:
        raise NotImplementedError()

    @abstractmethod
    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def create_inputs(self) -> Iterable[FeatureInput]:
        """Create ordered input descriptions for one compilation unit.

        Later inputs can reference definitions from earlier inputs because all
        returned inputs are parsed with one shared parser and symbol scope.
        """
        raise NotImplementedError()

    def copy(self) -> Self:
        return copy(self)

    def deepcopy(self) -> Self:
        return deepcopy(self)
