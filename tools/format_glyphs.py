from png import PngImage, PngHeader, PngColorType, PngFilterType

from tools import GLYPHS_DIR


def main() -> None:
    for file_path in GLYPHS_DIR.glob('*.png'):
        if not file_path.is_file():
            continue

        if not file_path.name.endswith(('.mono.png', '.color.png')):
            continue

        image = PngImage.load(file_path)
        if image.header.color_type != PngColorType.TRUECOLOR_ALPHA or image.header.bit_depth != 8:
            image = image.to_rgba(bit_depth=8)

        if file_path.name.endswith('.mono.png'):
            rows = [
                [
                    sample
                    for x in range(0, len(row), 4)
                    for sample in ((0, 0, 0, 255) if row[x + 3] >= 128 else (0, 0, 0, 0))
                ]
                for row in image.bitmap
            ]
        else:
            rows = [
                [
                    sample
                    for x in range(0, len(row), 4)
                    for sample in ((row[x], row[x + 1], row[x + 2], row[x + 3]) if row[x + 3] > 0 else (0, 0, 0, 0))
                ]
                for row in image.bitmap
            ]

        image = PngImage(
            header=PngHeader(image.dimensions),
            bitmap=rows,
        )
        image.save(file_path, filter_type=PngFilterType.NONE)


if __name__ == '__main__':
    main()
