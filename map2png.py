import sys
import os
import gzip
import json
from pathlib import Path

import nbtlib
from PIL import Image

color_json = """
[
    { "id":"0",  "color_name":0, "colors":[0,0,0,1] },
    { "id":"1",  "color_name":1, "colors":[127,178,56,1] },
    { "id":"2",  "color_name":1, "colors":[247,233,163,1] },
    { "id":"3",  "color_name":1, "colors":[199,199,199,1] },
    { "id":"4",  "color_name":1, "colors":[255,0,0,1] },
    { "id":"5",  "color_name":1, "colors":[160,160,255,1] },
    { "id":"6",  "color_name":1, "colors":[167,167,167,1] },
    { "id":"7",  "color_name":1, "colors":[0,124,0,1] },
    { "id":"8",  "color_name":1, "colors":[255,255,255,1] },
    { "id":"9",  "color_name":1, "colors":[164,168,184,1] },
    { "id":"10", "color_name":1, "colors":[151,109,77,1] },
    { "id":"11", "color_name":1, "colors":[112,112,112,1] },
    { "id":"12", "color_name":1, "colors":[64,64,255,1] },
    { "id":"13", "color_name":1, "colors":[143,119,72,1] },
    { "id":"14", "color_name":1, "colors":[255,252,245,1] },
    { "id":"15", "color_name":1, "colors":[216,127,51,1] },
    { "id":"16", "color_name":1, "colors":[178,76,216,1] },
    { "id":"17", "color_name":1, "colors":[102,153,216,1] },
    { "id":"18", "color_name":1, "colors":[229,229,51,1] },
    { "id":"19", "color_name":1, "colors":[127,204,25,1] },
    { "id":"20", "color_name":1, "colors":[242,127,165,1] },
    { "id":"21", "color_name":1, "colors":[76,76,76,1] },
    { "id":"22", "color_name":1, "colors":[153,153,153,1] },
    { "id":"23", "color_name":1, "colors":[76,127,153,1] },
    { "id":"24", "color_name":1, "colors":[127,63,178,1] },
    { "id":"25", "color_name":1, "colors":[51,76,178,1] },
    { "id":"26", "color_name":1, "colors":[102,76,51,1] },
    { "id":"27", "color_name":1, "colors":[102,127,51,1] },
    { "id":"28", "color_name":1, "colors":[153,51,51,1] },
    { "id":"29", "color_name":1, "colors":[25,25,25,1] },
    { "id":"30", "color_name":1, "colors":[250,238,77,1] },
    { "id":"31", "color_name":1, "colors":[92,219,213,1] },
    { "id":"32", "color_name":1, "colors":[74,128,255,1] },
    { "id":"33", "color_name":1, "colors":[0,217,58,1] },
    { "id":"34", "color_name":1, "colors":[129,86,49,1] },
    { "id":"35", "color_name":1, "colors":[112,2,0,1] },
    { "id":"36", "color_name":1, "colors":[209,177,161,1] },
    { "id":"37", "color_name":1, "colors":[159,82,36,1] },
    { "id":"38", "color_name":1, "colors":[149,87,108,1] },
    { "id":"39", "color_name":1, "colors":[112,108,138,1] },
    { "id":"40", "color_name":1, "colors":[186,133,36,1] },
    { "id":"41", "color_name":1, "colors":[103,117,53,1] },
    { "id":"42", "color_name":1, "colors":[160,77,78,1] },
    { "id":"43", "color_name":1, "colors":[57,41,35,1] },
    { "id":"44", "color_name":1, "colors":[135,107,98,1] },
    { "id":"45", "color_name":1, "colors":[87,92,92,1] },
    { "id":"46", "color_name":1, "colors":[122,73,88,1] },
    { "id":"47", "color_name":1, "colors":[76,62,92,1] },
    { "id":"48", "color_name":1, "colors":[76,50,35,1] },
    { "id":"49", "color_name":1, "colors":[76,82,42,1] },
    { "id":"50", "color_name":1, "colors":[142,60,46,1] },
    { "id":"51", "color_name":1, "colors":[37,22,16,1] },
    { "id":"52", "color_name":1, "colors":[189,48,49,255] },
    { "id":"53", "color_name":1, "colors":[148,63,97,255] },
    { "id":"54", "color_name":1, "colors":[92,25,29,255] },
    { "id":"55", "color_name":1, "colors":[22,126,134,255] },
    { "id":"56", "color_name":1, "colors":[58,142,140,255] },
    { "id":"57", "color_name":1, "colors":[86,44,62,255] },
    { "id":"58", "color_name":1, "colors":[20,180,133,255] },
    { "id":"59", "color_name":1, "colors":[100,100,100,255] },
    { "id":"60", "color_name":1, "colors":[216,175,147,255] },
    { "id":"61", "color_name":1, "colors":[127,167,150,255] }
]
"""

def get_color_data():
    return json.loads(color_json)

def get_expanded_color(base_color, shade_index):
    multipliers = [180, 220, 255, 135]
    r0, g0, b0 = base_color['colors'][:3]
    m = multipliers[shade_index]
    return (
        (r0 * m) // 255,
        (g0 * m) // 255,
        (b0 * m) // 255,
    )

def get_all_colors(color_data):
    palette = []
    for base in color_data:
        for shade in range(4):
            palette.append(get_expanded_color(base, shade))
    return palette

def load_map_dat(path):
    """
    Load a gzipped NBT map_*.dat, returning the raw color byte array
    and the width/height (always 128×128 in Java Edition).
    """
    try:
        nbtfile = nbtlib.load(path, gzipped=True)
        root = nbtfile
    except TypeError:
        with gzip.open(path, 'rb') as f:
            root = nbtlib.File.parse(f)
    data = root['data']
    colors = list(data['colors'])
    return colors, 128, 128

def colors_to_image(colors, w, h, palette):
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            idx = colors[y * w + x] & 0xFF
            px[x, y] = palette[idx]
    return img
    
def build_palette():
    return get_all_colors(get_color_data())

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_dir> <output_dir>")
        sys.exit(1)

    in_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    if not in_dir.is_dir():
        print(f"Error: input_dir {in_dir!r} is not a folder")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    palette = build_palette()

    for dat_path in in_dir.glob("*.dat"):
        try:
            colors, w, h = load_map_dat(dat_path)

            # skip completely blank/black maps
            if all(c == 0 for c in colors):
                print(f"Skipping {dat_path.name}: blank/black map")
                continue

            img = colors_to_image(colors, w, h, palette)
            png_path = out_dir / (dat_path.stem + ".png")
            img.save(png_path)
            print(f"Converted {dat_path.name} → {png_path.name}")
        except Exception as e:
            print(f"Failed to convert {dat_path.name}: {e}")


if __name__ == '__main__':
    main()
