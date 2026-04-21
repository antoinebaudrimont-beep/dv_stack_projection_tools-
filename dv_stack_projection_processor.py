import sys
from pathlib import Path

import numpy as np
import tifffile
from skimage.restoration import rolling_ball

try:
    from aicsimageio import AICSImage
except ImportError:
    AICSImage = None


def scale_to_8bit(stack, vmin, vmax):
    stack = np.asarray(stack, dtype=np.float32)
    if vmax <= vmin:
        raise ValueError(f"Invalid min/max: {vmin}, {vmax}")
    stack = np.clip(stack, vmin, vmax)
    stack = (stack - vmin) / (vmax - vmin)
    return (stack * 255).astype(np.uint8)


def subtract_background_stack(stack_8bit, radius=50):
    out = np.empty_like(stack_8bit)
    for z in range(stack_8bit.shape[0]):
        bg = rolling_ball(stack_8bit[z], radius=radius)
        sub = stack_8bit[z].astype(np.int16) - bg.astype(np.int16)
        out[z] = np.clip(sub, 0, 255).astype(np.uint8)
    return out


def max_project(stack):
    return np.max(stack, axis=0)


def split_and_project(stack, split_index_1based):
    """
    ImageJ-like logic:
      first projection:  start=1, stop=split_index
      second projection: start=split_index, stop=end

    So the split slice is included in both projections.
    """
    z = stack.shape[0]
    if not (1 <= split_index_1based <= z):
        raise ValueError(f"split_index {split_index_1based} out of bounds for Z={z}")

    i = split_index_1based - 1
    part1 = stack[: i + 1]
    part2 = stack[i:]
    return max_project(part1), max_project(part2)


def read_dv_file(path):
    if AICSImage is None:
        raise ImportError('aicsimageio is not installed. Run: pip install "aicsimageio[all]"')

    img = AICSImage(str(path))
    data = img.get_image_data("TCZYX")  # T, C, Z, Y, X

    if data.ndim != 5:
        raise ValueError(f"Unexpected data shape: {data.shape}")

    if data.shape[0] < 1:
        raise ValueError("No timepoint found")

    data = data[0]  # first timepoint -> C, Z, Y, X
    return data


def ask_int(prompt, default=None):
    while True:
        raw = input(f"{prompt}" + (f" [{default}]" if default is not None else "") + ": ").strip()
        if raw == "" and default is not None:
            return int(default)
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.")


def ask_yes_no(prompt, default=True):
    suffix = " [Y/n]: " if default else " [y/N]: "
    raw = input(prompt + suffix).strip().lower()
    if raw == "":
        return default
    return raw in {"y", "yes"}


def find_dv_files(folder):
    files = []
    for p in Path(folder).iterdir():
        if p.is_file() and p.name.lower().endswith("_d3d.dv"):
            files.append(p)
    return sorted(files)


def process_channel(stack, vmin, vmax, split_mode, offset, radius=50):
    stack_8 = scale_to_8bit(stack, vmin, vmax)
    stack_bg = subtract_background_stack(stack_8, radius=radius)

    if split_mode:
        z = stack_bg.shape[0]
        split_index = (z // 2) + offset
        split_index = max(1, min(split_index, z))
        proj1, proj2 = split_and_project(stack_bg, split_index)
        return {"top": proj1, "bottom": proj2, "split_index": split_index}
    else:
        return {"full": max_project(stack_bg)}


def process_file(path, requested_channels, settings, split_mode, output_dir):
    data = read_dv_file(path)  # C, Z, Y, X
    n_file_channels = data.shape[0]

    print(f"\nProcessing: {path.name}")
    print(f"Detected shape: {data.shape} (C,Z,Y,X)")

    if requested_channels > n_file_channels:
        raise ValueError(
            f"Requested {requested_channels} channel(s), but file has {n_file_channels}"
        )

    stem = path.name
    if stem.lower().endswith(".dv"):
        stem = stem[:-3]
    if stem.endswith("."):
        stem = stem[:-1]

    if requested_channels == 1:
        channel_stacks = [data[0]]
    else:
        channel_stacks = [data[i] for i in range(requested_channels)]

    for idx, stack in enumerate(channel_stacks, start=1):
        cfg = settings[idx - 1]
        print(
            f"  ch{idx}: Z={stack.shape[0]}, min={cfg['min']}, max={cfg['max']}, offset={cfg['offset']}"
        )

        result = process_channel(
            stack=stack,
            vmin=cfg["min"],
            vmax=cfg["max"],
            split_mode=split_mode,
            offset=cfg["offset"],
            radius=50,
        )

        if split_mode:
            out1 = output_dir / f"{stem}_ch{idx}_top.tif"
            out2 = output_dir / f"{stem}_ch{idx}_bottom.tif"
            tifffile.imwrite(out1, result["top"])
            tifffile.imwrite(out2, result["bottom"])
            print(f"    saved: {out1.name}")
            print(f"    saved: {out2.name}")
        else:
            out = output_dir / f"{stem}_ch{idx}.tif"
            tifffile.imwrite(out, result["full"])
            print(f"    saved: {out.name}")


def main():
    print("DV stack processor\n")

    folder = input("Folder containing *_D3D.dv files: ").strip()
    if not folder:
        print("No folder given.")
        sys.exit(1)

    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        print("Invalid folder.")
        sys.exit(1)

    files = find_dv_files(folder)
    if not files:
        print("No *_D3D.dv files found.")
        sys.exit(1)

    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  {f.name}")

    requested_channels = ask_int("How many channels should be processed", 1)
    split_mode = ask_yes_no("Split each channel into top/bottom half projections?", True)

    settings = []
    defaults = [
        {"min": 0, "max": 60000, "offset": 0},
        {"min": 0, "max": 130000, "offset": 1},
        {"min": 0, "max": 110000, "offset": 2},
        {"min": 0, "max": 170000, "offset": 3},
    ]

    for i in range(requested_channels):
        d = defaults[i] if i < len(defaults) else {"min": 0, "max": 60000, "offset": 0}
        print(f"\nChannel {i + 1}")
        vmin = ask_int("  min", d["min"])
        vmax = ask_int("  max", d["max"])
        offset = ask_int("  offset", d["offset"]) if split_mode else 0
        settings.append({"min": vmin, "max": vmax, "offset": offset})

    output_dir = folder / "processed_tiff"
    output_dir.mkdir(exist_ok=True)

    n_done = 0
    for f in files:
        try:
            process_file(f, requested_channels, settings, split_mode, output_dir)
            n_done += 1
        except Exception as e:
            print(f"\nERROR with {f.name}: {e}")

    print(f"\nDone. Processed {n_done}/{len(files)} file(s).")
    print(f"Output folder: {output_dir}")


if __name__ == "__main__":
    main()