from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.outline.pen.pen import OutlinePen


@runtime_checkable
class OutlinePainter(Protocol):
    def __copy__(self) -> OutlinePainter:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> OutlinePainter:
        return self.deepcopy()

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def draw_outlines(self, glyph: Glyph, pen: OutlinePen, px_to_units: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def copy(self) -> OutlinePainter:
        raise NotImplementedError()

    @abstractmethod
    def deepcopy(self) -> OutlinePainter:
        raise NotImplementedError()
