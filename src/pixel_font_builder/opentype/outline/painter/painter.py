from abc import abstractmethod
from copy import copy, deepcopy
from typing import Any, Protocol, Self, runtime_checkable

from pixel_font_builder.glyph import MonoRaster
from pixel_font_builder.opentype.outline.pen.pen import OutlinePen


@runtime_checkable
class OutlinePainter(Protocol):
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
    def draw_outlines(self, raster: MonoRaster, pen: OutlinePen, px_to_units: int) -> None:
        raise NotImplementedError()

    def copy(self) -> Self:
        return copy(self)

    def deepcopy(self) -> Self:
        return deepcopy(self)
