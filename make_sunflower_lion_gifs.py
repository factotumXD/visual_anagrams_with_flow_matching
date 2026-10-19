#!/usr/bin/env python3
"""Combine the nine 0048 Rotate180View images into one GIF, ordered v=2..10.

Run: python make_sunflower_lion_gifs.py
Requires Pillow. Preserves the source orientation and resolution by default.
"""

import argparse
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, default=ROOT / 'results')
    parser.add_argument('--output', type=Path, default=None,
                        help='Default: RESULTS_DIR/sunflower_to_lion_face.gif')
    parser.add_argument('--versions', type=int, nargs='+', default=list(range(2, 11)))
    parser.add_argument('--frame-ms', type=int, default=700,
                        help='Time per image in milliseconds (default: 700)')
    parser.add_argument('--size', type=int, default=None,
                        help='Optional maximum image side; defaults to original resolution')
    args = parser.parse_args()
    if args.frame_ms < 10 or (args.size is not None and args.size < 1):
        parser.error('frame-ms must be >= 10 and size must be positive')
    sources = [args.results_dir / f'rotate_180.sunflower.lionFace.woodcut.{v}'
               / '0048' / 'sample_1024.Rotate180View.png' for v in args.versions]
    missing = [str(source) for source in sources if not source.is_file()]
    if missing:
        parser.error('Missing input images:\n' + '\n'.join(missing))

    frames = []
    for source in sources:
        with Image.open(source) as image:
            frame = image.convert('RGB')
        if args.size is not None:
            frame.thumbnail((args.size, args.size), Image.Resampling.LANCZOS)
        frames.append(frame)
    if len({frame.size for frame in frames}) != 1:
        parser.error('All input images must have the same dimensions')

    # Sample every frame to build one palette for consistent colors.
    swatches = Image.new('RGB', (128 * len(frames), 128))
    for index, frame in enumerate(frames):
        swatches.paste(frame.resize((128, 128)), (128 * index, 0))
    palette = swatches.quantize(colors=256)
    frames = [frame.quantize(palette=palette) for frame in frames]
    destination = args.output or args.results_dir / 'sunflower_to_lion_face.gif'
    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=args.frame_ms, loop=0, optimize=False, disposal=2)
    print(destination)


if __name__ == '__main__':
    main()
