from __future__ import annotations

from datetime import datetime
from enum import StrEnum, unique
from typing import Any


@unique
class WeightName(StrEnum):
    THIN = 'Thin'                # 100
    EXTRA_LIGHT = 'Extra Light'  # 200
    LIGHT = 'Light'              # 300
    REGULAR = 'Regular'          # 400
    NORMAL = 'Normal'            # Same as 'Regular'
    MEDIUM = 'Medium'            # 500
    SEMI_BOLD = 'Semi Bold'      # 600
    BOLD = 'Bold'                # 700
    EXTRA_BOLD = 'Extra Bold'    # 800
    BLACK = 'Black'              # 900
    HEAVY = 'Heavy'              # Same as 'Black'

    @staticmethod
    def from_number(number: int) -> WeightName:
        match number:
            case 100:
                return WeightName.THIN
            case 200:
                return WeightName.EXTRA_LIGHT
            case 300:
                return WeightName.LIGHT
            case 400:
                return WeightName.REGULAR
            case 500:
                return WeightName.MEDIUM
            case 600:
                return WeightName.SEMI_BOLD
            case 700:
                return WeightName.BOLD
            case 800:
                return WeightName.EXTRA_BOLD
            case 900:
                return WeightName.BLACK
            case _:
                raise ValueError(f'unsupported weight number: {number}')

    @property
    def number(self) -> int:
        match self:
            case WeightName.THIN:
                return 100
            case WeightName.EXTRA_LIGHT:
                return 200
            case WeightName.LIGHT:
                return 300
            case WeightName.REGULAR | WeightName.NORMAL:
                return 400
            case WeightName.MEDIUM:
                return 500
            case WeightName.SEMI_BOLD:
                return 600
            case WeightName.BOLD:
                return 700
            case WeightName.EXTRA_BOLD:
                return 800
            case WeightName.BLACK | WeightName.HEAVY:
                return 900
            case _:
                raise AssertionError()


@unique
class SerifStyle(StrEnum):
    SERIF = 'Serif'
    SANS_SERIF = 'Sans Serif'


@unique
class SlantStyle(StrEnum):
    NORMAL = 'Normal'                    # Upright design
    ROMAN = 'Roman'                      # Same as 'NORMAL'
    ITALIC = 'Italic'                    # Italic design, slanted clockwise from the vertical
    OBLIQUE = 'Oblique'                  # Obliqued upright design, slanted clockwise from the vertical
    REVERSE_ITALIC = 'Reverse Italic'    # Italic design, slanted counterclockwise from the vertical
    REVERSE_OBLIQUE = 'Reverse Oblique'  # Obliqued upright design, slanted counterclockwise from the vertical
    OTHER = 'Other'                      # Other


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

    def __copy__(self) -> MetaInfo:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> MetaInfo:
        return self.deepcopy()

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

    def copy(self) -> MetaInfo:
        return MetaInfo(
            self.version,
            self.created_time,
            self.modified_time,
            self.family_name,
            self.weight_name,
            self.serif_style,
            self.slant_style,
            self.width_style,
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

    def deepcopy(self) -> MetaInfo:
        return self.copy()
