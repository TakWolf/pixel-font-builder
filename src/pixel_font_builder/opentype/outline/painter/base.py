from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.pen.base import OutlinesPen


@runtime_checkable
class OutlinesPainter(Protocol):
    def __copy__(self) -> OutlinesPainter:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> OutlinesPainter:
        return self.deepcopy()

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def draw_outlines(self, glyph: Glyph, pen: OutlinesPen, px_to_units: int):
        raise NotImplementedError()

    @abstractmethod
    def copy(self) -> OutlinesPainter:
        raise NotImplementedError()

    @abstractmethod
    def deepcopy(self) -> OutlinesPainter:
        raise NotImplementedError()
