from copy import copy, deepcopy
from pathlib import Path

from pixel_font_builder.opentype import FeatureFile


def test_copy():
    feature_file_1 = FeatureFile(
        text='test',
        file_path=Path('test.fea'),
    )
    feature_file_2 = copy(feature_file_1)
    feature_file_3 = deepcopy(feature_file_1)

    assert feature_file_1 == feature_file_2
    assert feature_file_1 == feature_file_3
    assert feature_file_1 is not feature_file_2
    assert feature_file_1 is not feature_file_3


def test_eq():
    feature_file_1 = FeatureFile(
        text='test',
        file_path=Path('test.fea'),
    )
    feature_file_2 = FeatureFile(
        text='test',
        file_path=Path('test.fea'),
    )
    assert feature_file_1 == feature_file_2
