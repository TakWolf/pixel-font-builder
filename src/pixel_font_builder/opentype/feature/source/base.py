from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Protocol, runtime_checkable

from fontTools.feaLib import ast


@runtime_checkable
class FeatureSource(Protocol):
    """A complete FEA program source parsed as one compilation unit.

    Relative ``include()`` paths follow FontTools rules. They use one common
    root for the complete program and are not resolved relative to each
    including file. Concrete sources define how that root is selected.
    """

    def __copy__(self) -> FeatureSource:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FeatureSource:
        return self.deepcopy()

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def parse(self, glyph_names: Iterable[str]) -> ast.FeatureFile:
        raise NotImplementedError()

    @abstractmethod
    def copy(self) -> FeatureSource:
        raise NotImplementedError()

    @abstractmethod
    def deepcopy(self) -> FeatureSource:
        raise NotImplementedError()
