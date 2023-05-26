
class MetaInfos:
    def __init__(
            self,
            family_name: str,
            version: str,
            description: str = None,
            copyright_info: str = None,
            license_description: str = None,
            license_url: str = None,
            designer: str = None,
            designer_url: str = None,
            vendor_url: str = None,
    ):
        self.family_name = family_name
        self.version = version
        self.description = description
        self.copyright_info = copyright_info
        self.license_description = license_description
        self.license_url = license_url
        self.designer = designer
        self.designer_url = designer_url
        self.vendor_url = vendor_url
