from copy import copy, deepcopy
from pathlib import Path

from pixel_font_builder.opentype import FeatureTextInput


def test_copy() -> None:
    feature_text_input_1 = FeatureTextInput(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_text_input_2 = copy(feature_text_input_1)
    feature_text_input_3 = deepcopy(feature_text_input_1)

    assert feature_text_input_1 == feature_text_input_2
    assert feature_text_input_1 == feature_text_input_3
    assert feature_text_input_1 is not feature_text_input_2
    assert feature_text_input_1 is not feature_text_input_3


def test_eq() -> None:
    feature_text_input_1 = FeatureTextInput(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_text_input_2 = FeatureTextInput(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    assert feature_text_input_1 == feature_text_input_2
