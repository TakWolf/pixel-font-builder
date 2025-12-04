from pixel_font_builder.opentype import BoundingBox


def test_bounding_box_1():
    bounding_box = BoundingBox()
    assert bounding_box.x_min == 0
    assert bounding_box.y_min == 0
    assert bounding_box.x_max == 0
    assert bounding_box.y_max == 0


def test_bounding_box_2():
    bounding_box = BoundingBox(1, 2, 3, 4) * 10
    assert bounding_box.x_min == 10
    assert bounding_box.y_min == 20
    assert bounding_box.x_max == 30
    assert bounding_box.y_max == 40
