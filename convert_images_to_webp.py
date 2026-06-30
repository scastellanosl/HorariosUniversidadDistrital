#!/usr/bin/env python3
"""
Convierte imágenes comunes a WebP y las coloca en la carpeta `img/`.

Uso:
    python convert_images_to_webp.py
    python convert_images_to_webp.py --delete-originals --quality 85

No borra los archivos originales a menos que se pase `--delete-originals`.
"""
import argparse
from pathlib import Path
from PIL import Image

SUPPORTED = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}


def convert_file(p: Path, out_dir: Path, quality: int = 85):
    try:
        img = Image.open(p)
        # Convert to RGB for formats that don't support alpha in WebP
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGBA', img.size, (255,255,255,0))
            background.paste(img, (0,0), img)
            img = background.convert('RGBA')
        else:
            img = img.convert('RGB')

        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (p.stem + '.webp')
        img.save(out_path, 'WEBP', quality=quality, method=6)
        print(f'Converted: {p} -> {out_path}')
        return out_path
    except Exception as e:
        print(f'Error converting {p}: {e}')
        return None


def main():
    parser = argparse.ArgumentParser(description='Convert images to WebP and move to img/ folder')
    parser.add_argument('--src', default='.', help='Carpeta raíz para buscar imágenes')
    parser.add_argument('--out', default='img', help='Carpeta destino (por defecto: img)')
    parser.add_argument('--quality', type=int, default=85, help='Calidad WebP (0-100)')
    parser.add_argument('--delete-originals', action='store_true', help='Eliminar originales tras conversión')
    args = parser.parse_args()

    root = Path(args.src)
    out_dir = Path(args.out)

    files = [p for p in root.rglob('*') if p.suffix.lower() in SUPPORTED]
    if not files:
        print('No se encontraron imágenes para convertir.')
        return

    converted = []
    for p in files:
        # skip files already inside out_dir with same stem and webp existing
        if out_dir in p.parents and p.suffix.lower() == '.webp':
            continue
        out = convert_file(p, out_dir, quality=args.quality)
        if out:
            converted.append((p, out))

    if args.delete_originals and converted:
        print('\nEliminando archivos originales...')
        for orig, out in converted:
            try:
                orig.unlink()
                print(f'Deleted {orig}')
            except Exception as e:
                print(f'No se pudo eliminar {orig}: {e}')

    print(f'Hecho. {len(converted)} archivos convertidos.')


if __name__ == '__main__':
    main()
