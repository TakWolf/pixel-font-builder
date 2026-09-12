import pytest
from fontTools.feaLib import ast

from pixel_font_builder import FontBuilder, Glyph
from pixel_font_builder.opentype import OutlineTableMode
from pixel_font_builder.opentype.kerning import create_kern_feature


@pytest.fixture
def builder() -> FontBuilder:
    builder = FontBuilder()
    builder.meta_info.family_name = 'Test Font'

    builder.font_metric.font_size = 10
    builder.font_metric.horizontal_layout.ascent = 8
    builder.font_metric.horizontal_layout.descent = -2
    builder.font_metric.vertical_layout.ascent = 5
    builder.font_metric.vertical_layout.descent = -5

    builder.glyphs.extend([
        Glyph(name='.notdef', advance_width=5, advance_height=10),
        Glyph(name='a', advance_width=5, advance_height=10),
        Glyph(name='b', advance_width=5, advance_height=10),
    ])

    builder.character_mapping.update({
        0x61: 'a',
        0x62: 'b',
    })

    return builder


def test_create_kern_feature() -> None:
    feature = create_kern_feature({
        ('b', 'a'): -1,
        ('a', 'b'): -2,
    }, 100)

    assert feature.name == 'kern'
    assert isinstance(feature.statements[0], ast.ScriptStatement)
    assert feature.statements[0].script == 'DFLT'
    assert isinstance(feature.statements[1], ast.LanguageStatement)
    assert feature.statements[1].language == 'dflt'

    pair_positions = feature.statements[2:]
    assert [(statement.glyphs1.glyph, statement.glyphs2.glyph, statement.valuerecord1.xAdvance) for statement in pair_positions] == [
        ('b', 'a', -100),
        ('a', 'b', -200),
    ]


def test_kerning_uses_scaled_pair_positioning(builder: FontBuilder) -> None:
    builder.opentype_config.px_to_units = 100
    builder.kerning_values[('a', 'b')] = -2

    font = builder.to_ttf_builder().font
    tb_gpos = font['GPOS'].table
    pair_pos = tb_gpos.LookupList.Lookup[0].SubTable[0]

    assert [record.ScriptTag for record in tb_gpos.ScriptList.ScriptRecord] == ['DFLT']
    assert [record.FeatureTag for record in tb_gpos.FeatureList.FeatureRecord] == ['kern']
    assert pair_pos.PairSet[0].PairValueRecord[0].Value1.XAdvance == -200
    assert font['OS/2'].usMaxContext == 2


def test_kerning_pair_positioning_is_sorted_by_glyph_order(builder: FontBuilder) -> None:
    builder.kerning_values.update({
        ('b', 'a'): -1,
        ('a', 'b'): -2,
    })

    font = builder.to_ttf_builder().font
    tb_gpos = font['GPOS'].table
    pair_pos = tb_gpos.LookupList.Lookup[0].SubTable[0]

    assert pair_pos.Coverage.glyphs == ['a', 'b']
    assert pair_pos.PairSet[0].PairValueRecord[0].SecondGlyph == 'b'
    assert pair_pos.PairSet[1].PairValueRecord[0].SecondGlyph == 'a'


@pytest.mark.parametrize(
    'outline_table_mode',
    [
        OutlineTableMode.OMIT,
        OutlineTableMode.ZERO_LENGTH,
        OutlineTableMode.BLANK_GLYPHS,
    ],
)
def test_kerning_is_omitted_without_normal_outlines(builder: FontBuilder, outline_table_mode: OutlineTableMode) -> None:
    builder.kerning_values[('a', 'b')] = -1

    font = builder.to_ttf_builder(outline_table_mode=outline_table_mode).font

    assert 'GPOS' not in font
