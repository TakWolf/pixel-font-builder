from enum import StrEnum, unique


@unique
class OutlineTableMode(StrEnum):
    # Generate standard outline data.
    # - TTF: write glyf/loca tables with full glyph outlines.
    # - OTF: write normal CFF table data.
    NORMAL = 'Normal'

    # Do not generate outline tables.
    OMIT = 'Omit'

    # Generate an outline table shell with zero-length table data.
    ZERO_LENGTH = 'Zero Length'

    # Generate outline tables for the full glyph order, but make glyph outlines empty.
    # Intended for fake scalable bitmap fonts where layout metrics still come from sfnt metrics tables.
    BLANK_GLYPHS = 'Blank Glyphs'


@unique
class BitmapTableMode(StrEnum):
    # Do not generate embedded bitmap tables.
    NONE = 'None'

    # Generate standard OpenType embedded bitmap tables.
    # Typically, EBDT + EBLC.
    STANDARD = 'Standard'

    # Generate Apple-style embedded bitmap tables.
    # Uses the same binary structure as EBDT/EBLC, but writes bdat/bloc tags instead.
    # Also generates a bhed table copied from head.
    APPLE = 'Apple'


@unique
class ColorTableFormat(StrEnum):
    # Generate color vector glyphs using COLR + CPAL.
    # Represents colored pixels as outline shapes with palette-based fills.
    COLR = 'COLR'

    # Generate color bitmap glyphs using CBDT + CBLC.
    # Embeds PNG glyph images at specific pixel sizes.
    CBDT = 'CBDT'

    # Generate color bitmap glyphs using Apple's sbix table.
    # Embeds PNG glyph images at specific pixel sizes.
    SBIX = 'SBIX'


@unique
class UserKerningMode(StrEnum):
    # Let any user kern feature or variation block take over all kerning.
    # Skip all generated kerning when such a block exists, even if it is empty
    # or limited to particular glyph pairs, scripts, languages, or conditions.
    # Generate kerning normally when no user kern block exists.
    TAKEOVER = 'Takeover'

    # Prepend generated kerning while preserving all user feature statements.
    # Rules are not deduplicated or merged by glyph pair. When both sets of rules
    # apply to the same pair, their positioning adjustments can accumulate.
    # Generated kerning uses DFLT/dflt; user script and language declarations
    # still determine where user rules apply.
    COEXIST = 'Coexist'


@unique
class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'
