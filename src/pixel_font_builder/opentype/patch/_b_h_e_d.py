from __future__ import annotations

from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d


class table__b_h_e_d(table__h_e_a_d):
    @staticmethod
    def replace(tb_old: table__h_e_a_d) -> table__b_h_e_d:
        tb_new = table__b_h_e_d()
        props = tb_old.__dict__.copy()
        props.pop('tableTag')
        tb_new.__dict__.update(props)
        return tb_new
