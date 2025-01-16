from pixel_font_builder import FontLayoutHeader, FontMetric


def test_font_metric_1():
    font_metric = FontMetric(
        font_size=10,
        horizontal_layout=FontLayoutHeader(
            ascent=1,
            descent=-1,
            line_gap=2,
        ),
        vertical_layout=FontLayoutHeader(
            ascent=3,
            descent=-3,
            line_gap=4,
        ),
        x_height=5,
        cap_height=6,
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
