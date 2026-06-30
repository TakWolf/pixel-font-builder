from copy import copy, deepcopy

from pixel_font_builder.bdf import Config


def test_copy():
    config_1 = Config(
        resolution_x=1,
        resolution_y=2,
        only_basic_plane=True,
    )
    config_2 = copy(config_1)
    config_3 = deepcopy(config_1)

    assert config_1 == config_2
    assert config_1 == config_3
    assert config_1 is not config_2
    assert config_1 is not config_3


def test_eq():
    config_1 = Config(
        resolution_x=1,
        resolution_y=2,
        only_basic_plane=True,
    )
    config_2 = Config(
        resolution_x=1,
        resolution_y=2,
        only_basic_plane=True,
    )
    assert config_1 == config_2
