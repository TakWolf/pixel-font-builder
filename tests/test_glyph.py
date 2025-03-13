from pixel_font_builder import Glyph


def test_glyph_1():
    glyph = Glyph(
        name='test',
        horizontal_offset=(1, 2),
        advance_width=3,
        vertical_offset=(4, 5),
        advance_height=6,
        bitmap=[
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
    )
    assert glyph.name == 'test'
    assert glyph.horizontal_offset_x == 1
    assert glyph.horizontal_offset_y == 2
    assert glyph.horizontal_offset == (1, 2)
    assert glyph.advance_width == 3
    assert glyph.vertical_offset_x == 4
    assert glyph.vertical_offset_y == 5
    assert glyph.vertical_offset == (4, 5)
    assert glyph.advance_height == 6
    assert glyph.width == 7
    assert glyph.height == 9
    assert glyph.dimensions == (7, 9)
    assert glyph.calculate_bitmap_left_padding() == 1
    assert glyph.calculate_bitmap_right_padding() == 2
    assert glyph.calculate_bitmap_top_padding() == 3
    assert glyph.calculate_bitmap_bottom_padding() == 1

    glyph.horizontal_offset = (7, 8)
    assert glyph.horizontal_offset_x == 7
    assert glyph.horizontal_offset_y == 8

    glyph.vertical_offset = (9, 10)
    assert glyph.vertical_offset_x == 9
    assert glyph.vertical_offset_y == 10


def test_glyph_2():
    glyph = Glyph(name='test')
    assert glyph.horizontal_offset == (0, 0)
    assert glyph.advance_width == 0
    assert glyph.vertical_offset == (0, 0)
    assert glyph.advance_height == 0
    assert glyph.dimensions == (0, 0)
    assert glyph.calculate_bitmap_left_padding() == 0
    assert glyph.calculate_bitmap_right_padding() == 0
    assert glyph.calculate_bitmap_top_padding() == 0
    assert glyph.calculate_bitmap_bottom_padding() == 0


def test_glyph_3():
    glyph = Glyph(
        name='test',
        bitmap=[
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0],
        ],
    )
    assert glyph.calculate_bitmap_left_padding() == 2
    assert glyph.calculate_bitmap_right_padding() == 2
    assert glyph.calculate_bitmap_top_padding() == 4
    assert glyph.calculate_bitmap_bottom_padding() == 4
