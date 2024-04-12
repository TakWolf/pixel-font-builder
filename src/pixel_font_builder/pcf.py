import logging

from pcffont import PcfFont

import pixel_font_builder

logger = logging.getLogger('pixel_font_builder.pcf')


class Config:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y


def create_font(context: 'pixel_font_builder.FontBuilder') -> PcfFont:

    # TODO

    return PcfFont()
