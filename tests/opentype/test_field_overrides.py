from copy import copy, deepcopy

from pixel_font_builder.opentype import FieldOverrides


def test_copy() -> None:
    field_overrides_1 = FieldOverrides(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    field_overrides_2 = copy(field_overrides_1)
    field_overrides_3 = deepcopy(field_overrides_1)

    assert field_overrides_1 == field_overrides_2
    assert field_overrides_1 == field_overrides_3
    assert field_overrides_1 is not field_overrides_2
    assert field_overrides_1 is not field_overrides_3


def test_eq() -> None:
    field_overrides_1 = FieldOverrides(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    field_overrides_2 = FieldOverrides(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    assert field_overrides_1 == field_overrides_2
