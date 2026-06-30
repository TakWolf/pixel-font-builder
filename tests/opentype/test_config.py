from copy import copy, deepcopy
from pathlib import Path

from pixel_font_builder.opentype import FieldsOverride, FeatureFile, Config, SolidOutlinesPainter


def test_copy():
    config_1 = Config(
        px_to_units=1,
        outlines_painter=SolidOutlinesPainter(),
        has_vertical_metrics=False,
        is_monospaced=True,
        fields_override=FieldsOverride(
            head_x_min=1,
            head_y_min=2,
            head_x_max=3,
            head_y_max=4,
            os2_x_avg_char_width=5,
        ),
        feature_files=[
            FeatureFile(
                text='test',
                file_path=Path('test.fea'),
            ),
        ],
    )
    config_2 = copy(config_1)

    assert config_1 == config_2
    assert config_1 is not config_2
    assert config_1.outlines_painter is config_2.outlines_painter
    assert config_1.fields_override is config_2.fields_override
    assert config_1.feature_files is config_2.feature_files


def test_deepcopy():
    config_1 = Config(
        px_to_units=1,
        outlines_painter=SolidOutlinesPainter(),
        has_vertical_metrics=False,
        is_monospaced=True,
        fields_override=FieldsOverride(
            head_x_min=1,
            head_y_min=2,
            head_x_max=3,
            head_y_max=4,
            os2_x_avg_char_width=5,
        ),
        feature_files=[
            FeatureFile(
                text='test',
                file_path=Path('test.fea'),
            ),
        ],
    )
    config_2 = deepcopy(config_1)

    assert config_1 == config_2
    assert config_1 is not config_2
    assert config_1.fields_override is not config_2.fields_override
    assert config_1.feature_files is not config_2.feature_files

    for feature_file_1, feature_file_2 in zip(config_1.feature_files, config_2.feature_files):
        assert feature_file_1 is not feature_file_2


def test_eq():
    config_1 = Config(
        px_to_units=1,
        outlines_painter=SolidOutlinesPainter(),
        has_vertical_metrics=False,
        is_monospaced=True,
        fields_override=FieldsOverride(
            head_x_min=1,
            head_y_min=2,
            head_x_max=3,
            head_y_max=4,
            os2_x_avg_char_width=5,
        ),
        feature_files=[
            FeatureFile(
                text='test',
                file_path=Path('test.fea'),
            ),
        ],
    )
    config_2 = Config(
        px_to_units=1,
        outlines_painter=SolidOutlinesPainter(),
        has_vertical_metrics=False,
        is_monospaced=True,
        fields_override=FieldsOverride(
            head_x_min=1,
            head_y_min=2,
            head_x_max=3,
            head_y_max=4,
            os2_x_avg_char_width=5,
        ),
        feature_files=[
            FeatureFile(
                text='test',
                file_path=Path('test.fea'),
            ),
        ],
    )
    assert config_1 == config_2
