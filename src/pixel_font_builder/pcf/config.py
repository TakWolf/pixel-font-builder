from __future__ import annotations

from typing import Any

from pcffont import GlyphPad, ScanUnit


class Config:
    resolution_x: int
    resolution_y: int
    draw_right_to_left: bool
    ms_byte_first: bool
    ms_bit_first: bool
    glyph_pad: GlyphPad
    scan_unit: ScanUnit

    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            draw_right_to_left: bool = False,
            ms_byte_first: bool = True,
            ms_bit_first: bool = True,
            glyph_pad: GlyphPad = 1,
            scan_unit: ScanUnit = 1,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.draw_right_to_left = draw_right_to_left
        self.ms_byte_first = ms_byte_first
        self.ms_bit_first = ms_bit_first
        self.glyph_pad = glyph_pad
        self.scan_unit = scan_unit

    def __copy__(self) -> Config:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return self.deepcopy()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return (self.resolution_x == other.resolution_x and
                self.resolution_y == other.resolution_y and
                self.draw_right_to_left == other.draw_right_to_left and
                self.ms_byte_first == other.ms_byte_first and
                self.ms_bit_first == other.ms_bit_first and
                self.glyph_pad == other.glyph_pad and
                self.scan_unit == other.scan_unit)

    def copy(self) -> Config:
        return Config(
            self.resolution_x,
            self.resolution_y,
            self.draw_right_to_left,
            self.ms_byte_first,
            self.ms_bit_first,
            self.glyph_pad,
            self.scan_unit,
        )

    def deepcopy(self) -> Config:
        return self.copy()
