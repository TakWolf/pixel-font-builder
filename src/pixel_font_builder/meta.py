from __future__ import annotations

from copy import copy, deepcopy
from datetime import datetime
from enum import IntEnum, StrEnum, unique
from typing import Any


@unique
class Weight(IntEnum):
    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    HEAVY = 900

    @property
    def display_name(self) -> str:
        return self.name.replace('_', '').title()


@unique
class SerifStyle(StrEnum):
    # Letterforms with decorative strokes at the ends of main strokes
    SERIF = 'Serif'

    # Letterforms without decorative strokes at the ends of main strokes
    SANS_SERIF = 'Sans Serif'


@unique
class Spacing(StrEnum):
    # Glyphs share the same advance width
    MONOSPACED = 'Monospaced'

    # Glyphs use two advance widths, with the wider twice the narrower
    DUOSPACED = 'Duospaced'

    # Glyphs share the same advance width and fit within a common fixed cell
    CHARACTER_CELL = 'Character Cell'

    # Glyph advance widths vary according to their design
    PROPORTIONAL = 'Proportional'


@unique
class Slant(StrEnum):
    # Upright design
    UPRIGHT = 'Upright'

    # Italic design, slanted clockwise from the vertical
    ITALIC = 'Italic'

    # Obliqued upright design, slanted clockwise from the vertical
    OBLIQUE = 'Oblique'

    # Italic design, slanted counterclockwise from the vertical
    REVERSE_ITALIC = 'Reverse Italic'

    # Obliqued upright design, slanted counterclockwise from the vertical
    REVERSE_OBLIQUE = 'Reverse Oblique'

    # Other
    OTHER = 'Other'


class MetaInfo:
    version: str
    created_time: datetime | None
    modified_time: datetime | None
    family_name: str | None
    weight: Weight
    serif_style: SerifStyle | None
    spacing: Spacing | None
    slant: Slant | None
    manufacturer: str | None
    designer: str | None
    description: str | None
    copyright_info: str | None
    license_info: str | None
    vendor_url: str | None
    designer_url: str | None
    license_url: str | None
    sample_text: str | None

    def __init__(
            self,
            version: str = '0.0.0',
            created_time: datetime | None = None,
            modified_time: datetime | None = None,
            family_name: str | None = None,
            weight: Weight = Weight.REGULAR,
            serif_style: SerifStyle | None = None,
            spacing: Spacing | None = None,
            slant: Slant | None = None,
            manufacturer: str | None = None,
            designer: str | None = None,
            description: str | None = None,
            copyright_info: str | None = None,
            license_info: str | None = None,
            vendor_url: str | None = None,
            designer_url: str | None = None,
            license_url: str | None = None,
            sample_text: str | None = None,
    ) -> None:
        self.version = version
        self.created_time = created_time
        self.modified_time = modified_time
        self.family_name = family_name
        self.weight = weight
        self.serif_style = serif_style
        self.spacing = spacing
        self.slant = slant
        self.manufacturer = manufacturer
        self.designer = designer
        self.description = description
        self.copyright_info = copyright_info
        self.license_info = license_info
        self.vendor_url = vendor_url
        self.designer_url = designer_url
        self.license_url = license_url
        self.sample_text = sample_text

    def __copy__(self) -> MetaInfo:
        return MetaInfo(
            self.version,
            self.created_time,
            self.modified_time,
            self.family_name,
            self.weight,
            self.serif_style,
            self.spacing,
            self.slant,
            self.manufacturer,
            self.designer,
            self.description,
            self.copyright_info,
            self.license_info,
            self.vendor_url,
            self.designer_url,
            self.license_url,
            self.sample_text,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> MetaInfo:
        return copy(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetaInfo):
            return NotImplemented
        return (self.version == other.version and
                self.created_time == other.created_time and
                self.modified_time == other.modified_time and
                self.family_name == other.family_name and
                self.weight == other.weight and
                self.serif_style == other.serif_style and
                self.spacing == other.spacing and
                self.slant == other.slant and
                self.manufacturer == other.manufacturer and
                self.designer == other.designer and
                self.description == other.description and
                self.copyright_info == other.copyright_info and
                self.license_info == other.license_info and
                self.vendor_url == other.vendor_url and
                self.designer_url == other.designer_url and
                self.license_url == other.license_url and
                self.sample_text == other.sample_text)

    def validate(self) -> None:
        if self.family_name is None:
            raise RuntimeError('family_name must not be None')

    def copy(self) -> MetaInfo:
        return copy(self)

    def deepcopy(self) -> MetaInfo:
        return deepcopy(self)
