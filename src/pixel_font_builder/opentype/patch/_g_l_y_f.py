from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import DefaultTable


class table__g_l_y_f_zero_length(DefaultTable.DefaultTable):
    def __init__(self):
        super().__init__('glyf')

    def compile(self, ttFont: TTFont) -> bytes:
        if 'loca' in ttFont:
            ttFont['loca'].set([0])
        return b''
