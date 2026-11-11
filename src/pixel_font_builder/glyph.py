from __future__ import annotations

from typing import Any, Generic, TypeVar, Self, cast

from pixel_font_builder.utils.color import ColorRgba

PixelT = TypeVar('PixelT', int, ColorRgba)


class Raster(Generic[PixelT]):
    """A mutable bitmap of typed pixels with horizontal and vertical placement.

    ``PixelT`` is either ``int`` or ``ColorRgba``. :class:`MonoRaster` and
    :class:`ColorRaster` fix the pixel type and define its interpretation.
    ``bitmap`` is a rectangular list of rows, ordered from top to bottom,
    with pixels ordered from left to right. Width is the first row's length,
    or zero for an empty bitmap; height is the number of rows. Offsets and
    bitmap dimensions are expressed in pixel-grid units.

    Both offsets default to ``(0, 0)``. Passing ``None`` for ``bitmap`` creates
    a new empty list with dimensions ``(0, 0)``. A supplied bitmap is retained
    by reference. Construction does not validate pixel values or row lengths.

    ``horizontal_offset`` positions the complete bitmap's bottom-left corner
    relative to the horizontal writing origin. Its x value is positive to the
    right, and its y value is positive upward from the baseline. The bitmap
    occupies ``[offset_x, offset_x + width]`` horizontally and
    ``[offset_y, offset_y + height]`` vertically in that coordinate system.

    ``vertical_offset`` positions the complete bitmap's top-left corner
    relative to the vertical writing origin, following the OpenType vertical
    bitmap-bearing convention. Its x value is positive to the right, and its
    y value is positive downward in the vertical writing direction.

    The vertical origin's y coordinate in the horizontal coordinate system
    can therefore be derived as
    ``height + horizontal_offset_y + vertical_offset_y``.
    This value describes the relationship between the two writing origins;
    it is not the bitmap's top edge or its vertical offset alone. Different
    bitmap dimensions and offsets can still produce the same origin y.

    In OpenType, this origin y is expressed in font design units. For CFF or
    CFF2 outlines, the optional VORG table records it directly. It can also
    be derived from the base glyph outline's yMax plus its top side bearing
    in vmtx; TrueType outlines use glyf and vmtx rather than VORG. The outline
    bounds used here need not equal the complete bitmap bounds, since the
    bitmap may include unfilled or transparent padding. A color presentation
    using the shared origin has its own top-edge distance, computed as the
    origin y minus the color graphic's top-edge y; the base outline's top
    side bearing must not be reused with the color graphic's bounds.

    Offsets do not crop transparent rows or columns. Padding remains part of
    the bitmap dimensions.
    """

    horizontal_offset_x: int
    horizontal_offset_y: int
    vertical_offset_x: int
    vertical_offset_y: int
    bitmap: list[list[PixelT]]

    def __init__(
            self,
            horizontal_offset: tuple[int, int] = (0, 0),
            vertical_offset: tuple[int, int] = (0, 0),
            bitmap: list[list[PixelT]] | None = None,
    ) -> None:
        self.horizontal_offset_x, self.horizontal_offset_y = horizontal_offset
        self.vertical_offset_x, self.vertical_offset_y = vertical_offset
        self.bitmap = bitmap if bitmap is not None else []

    def __copy__(self) -> Self:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Raster) or type(self) is not type(other):
            return NotImplemented
        return (self.horizontal_offset_x == other.horizontal_offset_x and
                self.horizontal_offset_y == other.horizontal_offset_y and
                self.vertical_offset_x == other.vertical_offset_x and
                self.vertical_offset_y == other.vertical_offset_y and
                self.bitmap == other.bitmap)

    @property
    def horizontal_offset(self) -> tuple[int, int]:
        return self.horizontal_offset_x, self.horizontal_offset_y

    @horizontal_offset.setter
    def horizontal_offset(self, value: tuple[int, int]) -> None:
        self.horizontal_offset_x, self.horizontal_offset_y = value

    @property
    def vertical_offset(self) -> tuple[int, int]:
        return self.vertical_offset_x, self.vertical_offset_y

    @vertical_offset.setter
    def vertical_offset(self, value: tuple[int, int]) -> None:
        self.vertical_offset_x, self.vertical_offset_y = value

    @property
    def width(self) -> int:
        if self.bitmap:
            return len(self.bitmap[0])
        else:
            return 0

    @property
    def height(self) -> int:
        return len(self.bitmap)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height

    def copy(self) -> Self:
        return cast(Self, type(self)(
            self.horizontal_offset,
            self.vertical_offset,
            self.bitmap,
        ))

    def deepcopy(self) -> Self:
        return cast(Self, type(self)(
            self.horizontal_offset,
            self.vertical_offset,
            [bitmap_row.copy() for bitmap_row in self.bitmap],
        ))


class MonoRaster(Raster[int]):
    """A monochrome bitmap and its horizontal and vertical placement.

    ``bitmap`` is a rectangular integer matrix: zero denotes an unfilled
    pixel, and any nonzero value denotes a filled pixel. Filled pixels do not
    specify a color. Placement follows the coordinate conventions of
    :class:`Raster`.

    An empty bitmap, ``[]``, has zero width and height. An empty MonoRaster
    provides a blank monochrome representation; ``Glyph.mono_raster=None``
    means that representation is absent.
    """
    pass


class ColorRaster(Raster[ColorRgba]):
    """An RGBA bitmap and its horizontal and vertical placement.

    ``bitmap`` is a rectangular matrix of ``(red, green, blue, alpha)`` tuples.
    Each channel is an integer from 0 to 255. RGB channels are not premultiplied
    by alpha; alpha 0 is fully transparent and alpha 255 is fully opaque.
    Placement follows the coordinate conventions of :class:`Raster`.

    An empty bitmap, ``[]``, has zero width and height. An empty or fully
    transparent ColorRaster provides an explicitly blank color representation;
    ``Glyph.color_raster=None`` means that representation is absent.
    """
    pass


class Glyph:
    """A named glyph with shared advances and optional raster representations.

    ``advance_width`` is the distance to the next horizontal writing origin,
    positive to the right. ``advance_height`` is the distance to the next
    vertical writing origin, positive downward. Both are expressed in the
    same pixel-grid units as the rasters and are shared by both representations.

    ``mono_raster`` and ``color_raster`` independently provide monochrome and
    RGBA representations of this glyph. ``None`` means that representation
    is absent. Either may be present without the other; the two sets of
    representations do not need identical glyph coverage.

    If both are absent, this is a valid blank glyph, retaining its name,
    character mappings, and advances. Its visible output is equivalent to
    an empty monochrome raster, as needed for a space, but no MonoRaster is
    implicitly created. If only the color raster is present, the glyph has
    a color representation and must not implicitly be treated as blank when
    exporting to a monochrome format; the exporter must handle the missing
    representation explicitly.

    Each raster owns its bitmap, dimensions, and horizontal and vertical
    offsets. The two representations may have different dimensions and
    offsets. See :class:`Raster` for the coordinate conventions.

    When both representations are used for the same COLR or sbix glyph with
    vertical layout, they must imply the same vertical origin y: the value
    ``height + horizontal_offset_y + vertical_offset_y`` must agree between
    them. Their bitmap bounds and individual offsets do not need to match.
    For example, a bitmap top at y=8 with vertical_offset_y=2 and another top
    at y=9 with vertical_offset_y=1 both imply an origin at y=10.

    These data classes allow independent placement and do not enforce
    target-format constraints. A COLR or sbix exporter must check this
    relationship when preserving both representations' vertical placement,
    and reject conflicting origins rather than silently override either offset.
    Calculating a shared origin alone cannot preserve incompatible horizontal
    and vertical placement requests. Other formats may have different
    placement constraints.
    """

    name: str
    advance_width: int
    advance_height: int
    mono_raster: MonoRaster | None
    color_raster: ColorRaster | None

    def __init__(
            self,
            name: str,
            advance_width: int = 0,
            advance_height: int = 0,
            mono_raster: MonoRaster | None = None,
            color_raster: ColorRaster | None = None,
    ) -> None:
        self.name = name
        self.advance_width = advance_width
        self.advance_height = advance_height
        self.mono_raster = mono_raster
        self.color_raster = color_raster

    def __copy__(self) -> Glyph:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Glyph:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Glyph):
            return NotImplemented
        return (self.name == other.name and
                self.advance_width == other.advance_width and
                self.advance_height == other.advance_height and
                self.mono_raster == other.mono_raster and
                self.color_raster == other.color_raster)

    @property
    def is_color_raster_only(self) -> bool:
        return self.mono_raster is None and self.color_raster is not None

    def copy(self) -> Glyph:
        return Glyph(
            self.name,
            self.advance_width,
            self.advance_height,
            self.mono_raster,
            self.color_raster,
        )

    def deepcopy(self) -> Glyph:
        return Glyph(
            self.name,
            self.advance_width,
            self.advance_height,
            self.mono_raster.deepcopy() if self.mono_raster is not None else None,
            self.color_raster.deepcopy() if self.color_raster is not None else None,
        )
