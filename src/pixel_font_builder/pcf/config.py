
class Config:
    resolution_x: int
    resolution_y: int
    draw_right_to_left: bool
    ms_byte_first: bool
    ms_bit_first: bool
    glyph_pad: int
    scan_unit: int

    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            draw_right_to_left: bool = False,
            ms_byte_first: bool = True,
            ms_bit_first: bool = True,
            glyph_pad: int = 1,
            scan_unit: int = 1,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.draw_right_to_left = draw_right_to_left
        self.ms_byte_first = ms_byte_first
        self.ms_bit_first = ms_bit_first
        self.glyph_pad = glyph_pad
        self.scan_unit = scan_unit
