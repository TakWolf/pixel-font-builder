from datetime import datetime
from enum import StrEnum, unique
from typing import Any


@unique
class WeightName(StrEnum):
    THIN = 'Thin'                # 100
    EXTRA_LIGHT = 'Extra Light'  # 200
    LIGHT = 'Light'              # 300
    NORMAL = 'Normal'            # 400
    REGULAR = 'Regular'          # Same as 'Normal'
    MEDIUM = 'Medium'            # 500
    SEMI_BOLD = 'Semi Bold'      # 600
    BOLD = 'Bold'                # 700
    EXTRA_BOLD = 'Extra Bold'    # 800
    BLACK = 'Black'              # 900
    HEAVY = 'Heavy'              # Same as 'Black'


@unique
class SerifStyle(StrEnum):
    SERIF = 'Serif'
    SANS_SERIF = 'Sans Serif'


@unique
class SlantStyle(StrEnum):
    NORMAL = 'Normal'
    ITALIC = 'Italic'
    OBLIQUE = 'Oblique'
    REVERSE_ITALIC = 'Reverse Italic'
    REVERSE_OBLIQUE = 'Reverse Oblique'


@unique
class WidthStyle(StrEnum):
    MONOSPACED = 'Monospaced'
    DUOSPACED = 'Duospaced'
    CHARACTER_CELL = 'Character Cell'
    PROPORTIONAL = 'Proportional'


class MetaInfo:
    version: str
    created_time: datetime | None
    modified_time: datetime | None
    family_name: str | None
    weight_name: WeightName | None
    serif_style: SerifStyle | None
    slant_style: SlantStyle | None
    width_style: WidthStyle | None
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
            weight_name: WeightName | None = None,
            serif_style: SerifStyle | None = None,
            slant_style: SlantStyle | None = None,
            width_style: WidthStyle | None = None,
            manufacturer: str | None = None,
            designer: str | None = None,
            description: str | None = None,
            copyright_info: str | None = None,
            license_info: str | None = None,
            vendor_url: str | None = None,
            designer_url: str | None = None,
            license_url: str | None = None,
            sample_text: str | None = None,
    ):
        self.version = version
        self.created_time = created_time
        self.modified_time = modified_time
        self.family_name = family_name
        self.weight_name = weight_name
        self.serif_style = serif_style
        self.slant_style = slant_style
        self.width_style = width_style
        self.manufacturer = manufacturer
        self.designer = designer
        self.description = description
        self.copyright_info = copyright_info
        self.license_info = license_info
        self.vendor_url = vendor_url
        self.designer_url = designer_url
        self.license_url = license_url
        self.sample_text = sample_text

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MetaInfo):
            return NotImplemented
        return (self.version == other.version and
                self.created_time == other.created_time and
                self.modified_time == other.modified_time and
                self.family_name == other.family_name and
                self.weight_name == other.weight_name and
                self.serif_style == other.serif_style and
                self.slant_style == other.slant_style and
                self.width_style == other.width_style and
                self.manufacturer == other.manufacturer and
                self.designer == other.designer and
                self.description == other.description and
                self.copyright_info == other.copyright_info and
                self.license_info == other.license_info and
                self.vendor_url == other.vendor_url and
                self.designer_url == other.designer_url and
                self.license_url == other.license_url and
                self.sample_text == other.sample_text)
