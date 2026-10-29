from collections.abc import Iterable

from fontTools.feaLib import ast

from pixel_font_builder.opentype.config import KerningMode
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs
from pixel_font_builder.opentype.feature.source.source import FeatureSource


def _claims_feature(feature_ast: ast.FeatureFile, name: str) -> bool:
    return any(
        isinstance(statement, (ast.FeatureBlock, ast.VariationBlock)) and statement.name == name
        for statement in feature_ast.statements
    )


def _add_additive_kerning(feature_ast: ast.FeatureFile, generated: ast.FeatureBlock) -> None:
    # DFLT alone is not a fallback for individual features when a script has its own GPOS record.
    # Register the base kerning in the user kern scopes too.
    language_systems = set()
    insertion_index = 0
    for index, statement in enumerate(feature_ast.statements):
        if isinstance(statement, ast.LanguageSystemStatement):
            language_systems.add((statement.script, statement.language))
            insertion_index = index + 1

    language_systems = language_systems or {('DFLT', 'dflt')}
    scopes = language_systems | {('DFLT', 'dflt')}
    for statement in feature_ast.statements:
        if isinstance(statement, (ast.FeatureBlock, ast.VariationBlock)) and statement.name == 'kern':
            script = min(language_systems)[0]
            for child in statement.statements:
                if isinstance(child, ast.ScriptStatement):
                    script = child.script
                    scopes.add((script, 'dflt'))
                elif isinstance(child, ast.LanguageStatement):
                    scopes.add((script, child.language))

    generated_features = []
    for script, language in sorted(scopes):
        feature = ast.FeatureBlock('kern')
        feature.statements = [
            ast.ScriptStatement(script),
            ast.LanguageStatement(language, include_default=False),
            *generated.statements[2:],
        ]
        generated_features.append(feature)

    # Feature boundaries keep generated pairs separate from user pairs.
    # Put them before user lookups, but after language-system declarations.
    feature_ast.statements[insertion_index:insertion_index] = generated_features


def build_feature_ast(
        features: FeatureSource | None,
        glyph_names: Iterable[str],
        generated_kern_feature: ast.FeatureBlock | None = None,
        kerning_mode: KerningMode = KerningMode.USER_REPLACE,
) -> ast.FeatureFile:
    feature_ast = parse_feature_inputs(features.create_inputs(), glyph_names) if features is not None else ast.FeatureFile()
    if generated_kern_feature is not None:
        match kerning_mode:
            case KerningMode.USER_REPLACE:
                if not _claims_feature(feature_ast, 'kern'):
                    feature_ast.statements.append(generated_kern_feature)
            case KerningMode.ADDITIVE:
                _add_additive_kerning(feature_ast, generated_kern_feature)
            case _:
                raise ValueError(f'unsupported kerning mode: {kerning_mode!r}')
    return feature_ast
