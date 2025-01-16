from pixel_font_builder.meta import WeightName, MetaInfo


def create_name_strings(meta_info: MetaInfo) -> dict[str, str]:
    """
    https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
    copyright (nameID 0)
    familyName (nameID 1)
    styleName (nameID 2)
    uniqueFontIdentifier (nameID 3)
    fullName (nameID 4)
    version (nameID 5)
    psName (nameID 6)
    trademark (nameID 7)
    manufacturer (nameID 8)
    designer (nameID 9)
    description (nameID 10)
    vendorURL (nameID 11)
    designerURL (nameID 12)
    licenseDescription (nameID 13)
    licenseInfoURL (nameID 14)
    typographicFamily (nameID 16)
    typographicSubfamily (nameID 17)
    compatibleFullName (nameID 18)
    sampleText (nameID 19)
    postScriptCIDFindfontName (nameID 20)
    wwsFamilyName (nameID 21)
    wwsSubfamilyName (nameID 22)
    lightBackgroundPalette (nameID 23)
    darkBackgroundPalette (nameID 24)
    variationsPostScriptNamePrefix (nameID 25)
    """
    unique_name = meta_info.family_name.replace(' ', '-')
    style_name = meta_info.weight_name or WeightName.REGULAR
    name_strings = {
        'familyName': meta_info.family_name,
        'styleName': style_name,
        'uniqueFontIdentifier': f'{unique_name}-{style_name};{meta_info.version}',
        'fullName': f'{meta_info.family_name} {style_name}',
        'version': meta_info.version,
        'psName': f'{unique_name}-{style_name}',
    }
    if meta_info.copyright_info is not None:
        name_strings['copyright'] = meta_info.copyright_info
    if meta_info.manufacturer is not None:
        name_strings['manufacturer'] = meta_info.manufacturer
    if meta_info.designer is not None:
        name_strings['designer'] = meta_info.designer
    if meta_info.description is not None:
        name_strings['description'] = meta_info.description
    if meta_info.vendor_url is not None:
        name_strings['vendorURL'] = meta_info.vendor_url
    if meta_info.designer_url is not None:
        name_strings['designerURL'] = meta_info.designer_url
    if meta_info.license_info is not None:
        name_strings['licenseDescription'] = meta_info.license_info
    if meta_info.license_url is not None:
        name_strings['licenseInfoURL'] = meta_info.license_url
    if meta_info.sample_text is not None:
        name_strings['sampleText'] = meta_info.sample_text
    return name_strings
