from pixel_font_builder import LineMetric, FontMetric


def test_font_metric_1():
    font_metric = FontMetric(
        font_size=10,
        horizontal_layout=LineMetric(
            ascent=1,
            descent=-1,
            line_gap=2,
        ),
        vertical_layout=LineMetric(
            ascent=3,
            descent=-3,
            line_gap=4,
        ),
        x_height=5,
        cap_height=6,
        underline_position=7,
        underline_thickness=8,
        strikeout_position=9,
        strikeout_thickness=10,
    ) * 2
    assert font_metric.font_size == 20
    assert font_metric.horizontal_layout.ascent == 2
    assert font_metric.horizontal_layout.descent == -2
    assert font_metric.horizontal_layout.line_height == 4
    assert font_metric.horizontal_layout.line_gap == 4
    assert font_metric.vertical_layout.ascent == 6
    assert font_metric.vertical_layout.descent == -6
    assert font_metric.vertical_layout.line_height == 12
    assert font_metric.vertical_layout.line_gap == 8
    assert font_metric.x_height == 10
    assert font_metric.cap_height == 12
    assert font_metric.underline_position == 14
    assert font_metric.underline_thickness == 16
    assert font_metric.strikeout_position == 18
    assert font_metric.strikeout_thickness == 20


def test_font_metric_2():
    font_metric = FontMetric()
    assert font_metric.font_size == 0
    assert font_metric.horizontal_layout.ascent == 0
    assert font_metric.horizontal_layout.descent == 0
    assert font_metric.horizontal_layout.line_height == 0
    assert font_metric.horizontal_layout.line_gap == 0
    assert font_metric.vertical_layout.ascent == 0
    assert font_metric.vertical_layout.descent == 0
    assert font_metric.vertical_layout.line_height == 0
    assert font_metric.vertical_layout.line_gap == 0
    assert font_metric.x_height == 0
    assert font_metric.cap_height == 0
    assert font_metric.underline_position == 0
    assert font_metric.underline_thickness == 0
    assert font_metric.strikeout_position == 0
    assert font_metric.strikeout_thickness == 0
