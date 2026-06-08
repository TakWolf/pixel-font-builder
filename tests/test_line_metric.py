from copy import copy, deepcopy

from pixel_font_builder import LineMetric


def test_line_metric_1():
    line_metric = LineMetric()
    assert line_metric.ascent == 0
    assert line_metric.descent == 0
    assert line_metric.line_height == 0
    assert line_metric.line_gap == 0


def test_line_metric_2():
    line_metric = LineMetric(
        ascent=8,
        descent=-2,
        line_gap=1,
    ) * 2
    assert line_metric.ascent == 16
    assert line_metric.descent == -4
    assert line_metric.line_height == 20
    assert line_metric.line_gap == 2


def test_copy():
    line_metric_1 = LineMetric(
        ascent=8,
        descent=-2,
        line_gap=1,
    )
    line_metric_2 = copy(line_metric_1)
    line_metric_3 = deepcopy(line_metric_1)

    assert line_metric_1 == line_metric_2
    assert line_metric_1 == line_metric_3
    assert line_metric_1 is not line_metric_2
    assert line_metric_1 is not line_metric_3


def test_eq():
    line_metric_1 = LineMetric(
        ascent=8,
        descent=-2,
        line_gap=1,
    )
    line_metric_2 = LineMetric(
        ascent=8,
        descent=-2,
        line_gap=1,
    )
    assert line_metric_1 == line_metric_2
