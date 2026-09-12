from pathlib import Path

import pytest
from fontTools.feaLib import ast

from pixel_font_builder import FontBuilder, Glyph
from pixel_font_builder.opentype import OutlineTableMode, FeatureText, FeatureFile, FeatureIncludes
from pixel_font_builder.opentype.feature.common import build_feature_ast
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


def test_generated_kerning_is_added_without_user_kern() -> None:
    generated_kern_feature = create_kern_feature({
        ('a', 'b'): -1,
    }, 100)

    feature_ast = build_feature_ast(
        FeatureText('feature salt { sub a by b; } salt;'),
        ['a', 'b'],
        generated_kern_feature,
    )

    assert feature_ast.statements[-1] is generated_kern_feature


def test_non_kern_variation_block_does_not_claim_kerning() -> None:
    generated_kern_feature = create_kern_feature({
        ('a', 'b'): -1,
    }, 100)

    feature_ast = build_feature_ast(
        FeatureText(
            'conditionset Heavy { wght 700 900; } Heavy; variation dist Heavy { pos b a -300; } dist;'
        ),
        ['a', 'b'],
        generated_kern_feature,
    )

    assert feature_ast.statements[-1] is generated_kern_feature
    assert any(
        isinstance(statement, ast.VariationBlock) and statement.name == 'dist'
        for statement in feature_ast.statements
    )


def test_user_feature_block_claims_kerning() -> None:
    generated_kern_feature = create_kern_feature({
        ('a', 'b'): -1,
    }, 100)

    feature_ast = build_feature_ast(
        FeatureText('feature kern { pos b a -300; } kern;'),
        ['a', 'b'],
        generated_kern_feature,
    )

    assert generated_kern_feature not in feature_ast.statements
    assert [type(statement) for statement in feature_ast.statements] == [ast.FeatureBlock]


def test_user_variation_block_claims_kerning() -> None:
    generated_kern_feature = create_kern_feature({
        ('a', 'b'): -1,
    }, 100)

    feature_ast = build_feature_ast(
        FeatureText(
            'conditionset Heavy { wght 700 900; } Heavy; variation kern Heavy { pos b a -300; } kern;'
        ),
        ['a', 'b'],
        generated_kern_feature,
    )

    assert generated_kern_feature not in feature_ast.statements
    assert any(isinstance(statement, ast.VariationBlock) and statement.name == 'kern' for statement in feature_ast.statements)


def test_user_feature_and_variation_blocks_claim_kerning() -> None:
    generated_kern_feature = create_kern_feature({
        ('a', 'b'): -1,
    }, 100)

    feature_ast = build_feature_ast(
        FeatureText(
            'conditionset Heavy { wght 700 900; } Heavy; feature kern { pos a b -100; } kern; variation kern Heavy { pos b a -300; } kern;'
        ),
        ['a', 'b'],
        generated_kern_feature,
    )

    assert generated_kern_feature not in feature_ast.statements
    assert any(isinstance(statement, ast.FeatureBlock) and statement.name == 'kern' for statement in feature_ast.statements)
    assert any(isinstance(statement, ast.VariationBlock) and statement.name == 'kern' for statement in feature_ast.statements)


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


def test_generated_kerning_coexists_with_user_features(builder: FontBuilder) -> None:
    builder.kerning_values[('a', 'b')] = -1
    builder.opentype_config.features = FeatureText(
        'feature salt { sub a by b; } salt; feature kern { pos b a -300; } kern;'
    )

    font = builder.to_ttf_builder().font
    tb_gpos = font['GPOS'].table
    pair_pos = tb_gpos.LookupList.Lookup[0].SubTable[0]

    assert 'GSUB' in font
    assert [record.FeatureTag for record in font['GSUB'].table.FeatureList.FeatureRecord] == ['salt']
    assert [record.FeatureTag for record in tb_gpos.FeatureList.FeatureRecord] == ['kern']
    assert pair_pos.Coverage.glyphs == ['b']
    assert pair_pos.PairSet[0].PairValueRecord[0].Value1.XAdvance == -300


def test_generated_kerning_coexists_with_feature_file(builder: FontBuilder, tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('dist.fea')
    feature_path.write_text('feature dist { pos b a -300; } dist;', 'utf-8')

    builder.kerning_values[('a', 'b')] = -1
    builder.opentype_config.features = FeatureFile(feature_path)

    font = builder.to_ttf_builder().font
    tb_gpos = font['GPOS'].table
    feature_tags = [record.FeatureTag for record in tb_gpos.FeatureList.FeatureRecord]

    assert feature_tags == ['dist', 'kern']


def test_multiple_user_feature_files_are_combined(builder: FontBuilder, tmp_path: Path) -> None:
    salt_path = tmp_path.joinpath('salt.fea')
    salt_path.write_text('feature salt { sub a by b; } salt;', 'utf-8')
    ss01_path = tmp_path.joinpath('ss01.fea')
    ss01_path.write_text('feature ss01 { sub b by a; } ss01;', 'utf-8')

    builder.opentype_config.features = FeatureIncludes([salt_path, ss01_path])

    font = builder.to_ttf_builder().font
    tb_gsub = font['GSUB'].table
    feature_tags = [record.FeatureTag for record in tb_gsub.FeatureList.FeatureRecord]

    assert feature_tags == ['salt', 'ss01']
    assert font.getBestCmap() == {0x0061: 'a', 0x0062: 'b'}


def test_included_user_kerning_replaces_generated_kerning(builder: FontBuilder, tmp_path: Path) -> None:
    tmp_path.joinpath('kern.fea').write_text('feature kern { pos b a -300; } kern;', 'utf-8')

    builder.kerning_values[('a', 'b')] = -1
    builder.opentype_config.features = FeatureText(
        text='include(kern.fea);',
        filename=tmp_path.joinpath('main.fea'),
    )

    font = builder.to_ttf_builder().font
    tb_gpos = font['GPOS'].table
    pair_pos = tb_gpos.LookupList.Lookup[0].SubTable[0]

    assert pair_pos.Coverage.glyphs == ['b']
    assert pair_pos.PairSet[0].PairValueRecord[0].Value1.XAdvance == -300


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
