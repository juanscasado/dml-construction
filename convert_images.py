from pathlib import Path
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
import argparse

register_heif_opener()

SUPPORTED_FORMATS = {
    ".heic", ".heif", ".jpg", ".jpeg", ".png",
    ".bmp", ".tif", ".tiff", ".webp"
}

def convert_images(input_dir: Path, output_dir: Path, output_format: str, quality: int):
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    skipped = 0
    failed = 0

    for source in input_dir.rglob("*"):
        if not source.is_file() or source.suffix.lower() not in SUPPORTED_FORMATS:
            continue

        relative_path = source.relative_to(input_dir)
        destination = output_dir / relative_path
        destination = destination.with_suffix(f".{output_format}")
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image)

                if output_format == "png":
                    # PNG admite transparencia; convierte modos incompatibles.
                    if image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
                        image = image.convert("RGBA")
                    image.save(destination, format="PNG", optimize=True)
                else:
                    # WebP no necesita transparencia eliminada.
                    if image.mode not in ("RGB", "RGBA"):
                        image = image.convert("RGBA" if "A" in image.mode else "RGB")
                    image.save(
                        destination,
                        format="WEBP",
                        quality=quality,
                        method=6
                    )

            converted += 1
            print(f"[OK] {source} -> {destination}")

        except Exception as error:
            failed += 1
            print(f"[ERROR] {source}: {error}")

    print("\nResumen")
    print(f"Convertidas: {converted}")
    print(f"Errores:     {failed}")
    print(f"Omitidas:    {skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convierte imágenes a WebP o PNG."
    )
    parser.add_argument(
        "input",
        help="Carpeta que contiene las imágenes"
    )
    parser.add_argument(
        "--output",
        default="converted_images",
        help="Carpeta de salida (por defecto: converted_images)"
    )
    parser.add_argument(
        "--format",
        choices=("webp", "png"),
        default="webp",
        help="Formato de salida (por defecto: webp)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        choices=range(1, 101),
        metavar="1-100",
        help="Calidad WebP, de 1 a 100 (por defecto: 85)"
    )

    args = parser.parse_args()

    convert_images(
        Path(args.input),
        Path(args.output),
        args.format,
        args.quality
    )
