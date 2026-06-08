from copy import copy, deepcopy

from pixel_font_builder import FontBuilder, Glyph


def test_prepare_glyphs():
    builder = FontBuilder()
    builder.glyphs.extend([
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ])
    builder.character_mapping.update({
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    })
    builder.kerning_values.update({
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    })

    glyph_order, name_to_glyph = builder.prepare_glyphs()

    assert glyph_order == [
        '.notdef',
        'CAP_LETTER_A',
        'CAP_LETTER_B',
        'CAP_LETTER_C',
    ]
    assert builder.glyphs == [
        name_to_glyph['.notdef'],
        name_to_glyph['CAP_LETTER_A'],
        name_to_glyph['CAP_LETTER_B'],
        name_to_glyph['CAP_LETTER_C'],
    ]


def test_copy():
    builder_1 = FontBuilder()
    builder_1.glyphs.extend([
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ])
    builder_1.character_mapping.update({
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    })
    builder_1.kerning_values.update({
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    })
    builder_2 = copy(builder_1)

    assert builder_1 == builder_2
    assert builder_1 is not builder_2
    assert builder_1.font_metric is builder_2.font_metric
    assert builder_1.meta_info is builder_2.meta_info
    assert builder_1.glyphs is builder_2.glyphs
    assert builder_1.character_mapping is builder_2.character_mapping
    assert builder_1.kerning_values is builder_2.kerning_values
    assert builder_1.opentype_config is builder_2.opentype_config
    assert builder_1.bdf_config is builder_2.bdf_config
    assert builder_1.pcf_config is builder_2.pcf_config


def test_deepcopy():
    builder_1 = FontBuilder()
    builder_1.glyphs.extend([
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ])
    builder_1.character_mapping.update({
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    })
    builder_1.kerning_values.update({
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    })
    builder_2 = deepcopy(builder_1)

    assert builder_1 == builder_2
    assert builder_1 is not builder_2
    assert builder_1.font_metric is not builder_2.font_metric
    assert builder_1.meta_info is not builder_2.meta_info
    assert builder_1.glyphs is not builder_2.glyphs
    assert builder_1.character_mapping is not builder_2.character_mapping
    assert builder_1.kerning_values is not builder_2.kerning_values
    assert builder_1.opentype_config is not builder_2.opentype_config
    assert builder_1.bdf_config is not builder_2.bdf_config
    assert builder_1.pcf_config is not builder_2.pcf_config

    for glyph_1, glyph_2 in zip(builder_1.glyphs, builder_2.glyphs):
        assert glyph_1 is not glyph_2


def test_eq():
    builder_1 = FontBuilder()
    builder_1.glyphs.extend([
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ])
    builder_1.character_mapping.update({
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    })
    builder_1.kerning_values.update({
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    })

    builder_2 = FontBuilder()
    builder_2.glyphs.extend([
        Glyph(name='.notdef'),
        Glyph(name='CAP_LETTER_A'),
        Glyph(name='CAP_LETTER_B'),
        Glyph(name='CAP_LETTER_C'),
    ])
    builder_2.character_mapping.update({
        65: 'CAP_LETTER_A',
        66: 'CAP_LETTER_B',
        67: 'CAP_LETTER_C',
    })
    builder_2.kerning_values.update({
        ('CAP_LETTER_A', 'CAP_LETTER_B'): 1,
        ('CAP_LETTER_A', 'CAP_LETTER_C'): 2,
    })

    assert builder_1 == builder_2
