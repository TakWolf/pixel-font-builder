from copy import copy, deepcopy

from pixel_font_builder import FontBuilder, Glyph, ColorRaster


def test_prepare_glyphs_1() -> None:
    builder = FontBuilder()
    builder.glyphs = [
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ]
    builder.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }

    glyph_order, name_to_glyph = builder.prepare_glyphs()

    assert glyph_order == [
        '.notdef',
        'CAP_LETTER_A',
        'CAP_LETTER_B',
        'CAP_LETTER_C',
    ]
    assert set(glyph_order) == set(name_to_glyph.keys())


def test_prepare_glyphs_2() -> None:
    builder = FontBuilder()
    builder.glyphs = [
        Glyph(name='.notdef', color_raster=ColorRaster()),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C', color_raster=ColorRaster()),
    ]
    builder.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }

    glyph_order, name_to_glyph = builder.prepare_glyphs(no_color_mode=True)
    character_mapping = builder.prepare_character_mapping(name_to_glyph)
    kerning_values = builder.prepare_kerning_values(name_to_glyph)

    assert glyph_order == [
        '.notdef',
        'CAP_LETTER_A',
        'CAP_LETTER_B',
    ]
    assert set(glyph_order) == set(name_to_glyph.keys())
    assert character_mapping == {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
    }
    assert kerning_values == {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
    }


def test_copy() -> None:
    builder_1 = FontBuilder()
    builder_1.glyphs = [
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ]
    builder_1.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder_1.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }
    builder_2 = copy(builder_1)

    assert builder_1 == builder_2
    assert builder_1 is not builder_2
    assert builder_1.font_metric is builder_2.font_metric
    assert builder_1.meta_info is builder_2.meta_info
    assert builder_1.glyphs is builder_2.glyphs
    assert builder_1.character_mapping is builder_2.character_mapping
    assert builder_1.kerning_values is builder_2.kerning_values
    assert builder_1.opentype_config is builder_2.opentype_config
    assert builder_1.dfont_config is builder_2.dfont_config
    assert builder_1.bdf_config is builder_2.bdf_config
    assert builder_1.pcf_config is builder_2.pcf_config


def test_deepcopy() -> None:
    builder_1 = FontBuilder()
    builder_1.glyphs = [
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ]
    builder_1.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder_1.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }
    builder_2 = deepcopy(builder_1)

    assert builder_1 == builder_2
    assert builder_1 is not builder_2
    assert builder_1.font_metric is not builder_2.font_metric
    assert builder_1.meta_info is not builder_2.meta_info
    assert builder_1.glyphs is not builder_2.glyphs
    assert builder_1.character_mapping is not builder_2.character_mapping
    assert builder_1.kerning_values is not builder_2.kerning_values
    assert builder_1.opentype_config is not builder_2.opentype_config
    assert builder_1.dfont_config is not builder_2.dfont_config
    assert builder_1.bdf_config is not builder_2.bdf_config
    assert builder_1.pcf_config is not builder_2.pcf_config

    for glyph_1, glyph_2 in zip(builder_1.glyphs, builder_2.glyphs):
        assert glyph_1 is not glyph_2


def test_eq() -> None:
    builder_1 = FontBuilder()
    builder_1.glyphs = [
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ]
    builder_1.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder_1.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }

    builder_2 = FontBuilder()
    builder_2.glyphs = [
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ]
    builder_2.character_mapping = {
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    }
    builder_2.kerning_values = {
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    }

    assert builder_1 == builder_2
