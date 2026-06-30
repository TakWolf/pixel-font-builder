from copy import copy, deepcopy

from pixel_font_builder.opentype import FieldsOverride


def test_copy():
    fields_override_1 = FieldsOverride(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    fields_override_2 = copy(fields_override_1)
    fields_override_3 = deepcopy(fields_override_1)

    assert fields_override_1 == fields_override_2
    assert fields_override_1 == fields_override_3
    assert fields_override_1 is not fields_override_2
    assert fields_override_1 is not fields_override_3


def test_eq():
    fields_override_1 = FieldsOverride(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    fields_override_2 = FieldsOverride(
        head_x_min=1,
        head_y_min=2,
        head_x_max=3,
        head_y_max=4,
        os2_x_avg_char_width=5,
    )
    assert fields_override_1 == fields_override_2
