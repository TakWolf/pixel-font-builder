
class MetaInfos:
    def __init__(
            self,
            version: str = None,
            family_name: str = None,
            description: str = None,
            manufacturer: str = None,
            foundry: str = None,
            designer: str = None,
            copyright_info: str = None,
            license_description: str = None,
            designer_url: str = None,
            license_url: str = None,
            vendor_url: str = None,
    ):
        self.version = version
        self.family_name = family_name
        self.description = description
        self.manufacturer = manufacturer
        self.foundry = foundry
        self.designer = designer
        self.copyright_info = copyright_info
        self.license_description = license_description
        self.designer_url = designer_url
        self.license_url = license_url
        self.vendor_url = vendor_url


class OpenTypeConfigs:
    def __init__(
            self,
            px_to_units: int = 100,
    ):
        self.px_to_units = px_to_units


class BdfConfigs:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
