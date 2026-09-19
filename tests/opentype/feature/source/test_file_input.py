from copy import copy, deepcopy
from pathlib import Path

from pixel_font_builder.opentype import FeatureFileInput


def test_copy() -> None:
    feature_file_input_1 = FeatureFileInput(
        path=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_file_input_2 = copy(feature_file_input_1)
    feature_file_input_3 = deepcopy(feature_file_input_1)

    assert feature_file_input_1 == feature_file_input_2
    assert feature_file_input_1 == feature_file_input_3
    assert feature_file_input_1 is not feature_file_input_2
    assert feature_file_input_1 is not feature_file_input_3


def test_eq() -> None:
    feature_file_input_1 = FeatureFileInput(
        path=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_file_input_2 = FeatureFileInput(
        path=Path('test.fea'),
        include_dir=Path('fea'),
    )
    assert feature_file_input_1 == feature_file_input_2
