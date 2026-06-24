from __future__ import annotations

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2


class table_O_S_2f_2_apple(table_O_S_2f_2):
    @staticmethod
    def replace(tb_old: table_O_S_2f_2) -> table_O_S_2f_2_apple:
        tb_new = table_O_S_2f_2_apple()
        props = tb_old.__dict__.copy()
        props.pop('tableTag')
        tb_new.__dict__.update(props)
        return tb_new

    dependencies = ['bhed']

    def __init__(self):
        super().__init__('OS/2')

    def compile(self, ttFont: TTFont) -> bytes:
        hacked = False
        if 'head' not in ttFont:
            hacked = True
            ttFont['head'] = ttFont['bhed']
        try:
            return super().compile(ttFont)
        finally:
            if hacked:
                del ttFont['head']
