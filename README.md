# DV stack projection tools

Reusable ImageJ and Python tools for preprocessing multi-channel DV microscopy stacks and exporting 8-bit TIFF maximum-intensity projections.

This folder contains a Python script and the original ImageJ/Fiji macro workflow on which it was based. The tools are intended for routine microscopy preprocessing, especially for DeltaVision-style `.dv` image stacks containing multiple fluorescence channels.

## Files

```text
dv_stack_projection_processor.py
imagej_stack_projection_workflow.ijm
```

## Overview

The workflow converts multi-channel Z-stacks into processed TIFF projections.

For each selected channel, the scripts can:

1. Set display intensity limits.
2. Convert the image stack to 8-bit.
3. Apply rolling-ball background subtraction.
4. Generate maximum-intensity projections.
5. Optionally split the Z-stack into top and bottom projections.
6. Export the resulting images as TIFF files.

The Python version automates the workflow for multiple `.dv` files in a folder. In contrast to the ImageJ macro, the Python script automatically saves the processed projection images as TIFF files in the output folder.

## Python script

```text
dv_stack_projection_processor.py
```

This script processes all files ending with:

```text
_D3D.dv
```

in a selected folder.

It reads each DV file, extracts the requested number of channels, applies channel-specific intensity scaling, subtracts background using a rolling-ball algorithm, and exports maximum-intensity TIFF projections.

### Main features

- Batch processing of multiple `.dv` files.
- Support for one or more fluorescence channels.
- Channel-specific minimum and maximum intensity values.
- Rolling-ball background subtraction.
- Optional top/bottom Z-stack splitting.
- TIFF output saved automatically in a `processed_tiff/` folder.

### Output

The script creates an output folder:

```text
processed_tiff/
```

If top/bottom splitting is enabled, output files are named:

```text
sample_ch1_top.tif
sample_ch1_bottom.tif
sample_ch2_top.tif
sample_ch2_bottom.tif
```

If splitting is disabled, output files are named:

```text
sample_ch1.tif
sample_ch2.tif
```

## ImageJ/Fiji macro

```text
imagej_stack_projection_workflow.ijm
```

This macro represents the original manual ImageJ workflow.

Unlike the Python script, the ImageJ macro does not automatically save the projected images as TIFF files. After each projection is generated and displayed in a pop-up image window, the image should be copied to the clipboard and pasted manually into Photoshop for figure preparation or further handling.

The macro performs channel splitting, intensity scaling, 8-bit conversion, rolling-ball background subtraction, and maximum-intensity projection.

The macro includes two related workflows.

### Meiotic-region projection workflow

This part splits a multi-channel stack and generates top and bottom projections for each channel.

The Z-stack is divided approximately in half, with optional channel-specific offsets:

```text
channel 1: nSlices / 2
channel 2: nSlices / 2 + 1
channel 3: nSlices / 2 + 2
channel 4: nSlices / 2 + 3
```

This was used to generate separate projections from different regions of the same Z-stack.

### Diakinesis projection workflow

The macro also contains a simpler diakinesis workflow, where each channel is projected across the full Z-stack without top/bottom splitting.

## Requirements

### Python

The Python script requires:

```text
python
numpy
tifffile
scikit-image
aicsimageio
```

Install the required packages with:

```bash
pip install numpy tifffile scikit-image "aicsimageio[all]"
```

### ImageJ/Fiji

The ImageJ macro requires:

```text
Fiji or ImageJ
```

The macro uses standard ImageJ commands including:

```text
Stack Splitter
Subtract Background
Z Project
8-bit conversion
```

## How to run the Python script

Place the Python script anywhere on your computer.

Run:

```bash
python dv_stack_projection_processor.py
```

The script will ask for:

```text
Folder containing *_D3D.dv files
Number of channels to process
Whether to split the stack into top/bottom projections
Minimum and maximum intensity values for each channel
Z-split offset for each channel
```

Example:

```text
Folder containing *_D3D.dv files: /path/to/images
How many channels should be processed [1]: 4
Split each channel into top/bottom half projections? [Y/n]: Y
```

The processed TIFF files will be saved in:

```text
/path/to/images/processed_tiff/
```

## Default channel settings

The Python script currently uses these default values:

```text
Channel 1: min = 0, max = 60000,  offset = 0
Channel 2: min = 0, max = 130000, offset = 1
Channel 3: min = 0, max = 110000, offset = 2
Channel 4: min = 0, max = 170000, offset = 3
```

These values can be changed interactively when the script is run.

## Processing logic

The Python script reproduces the main logic of the ImageJ macro.

For each channel:

```text
raw stack
→ intensity scaling
→ 8-bit conversion
→ rolling-ball background subtraction
→ maximum-intensity projection
→ TIFF export
```

When top/bottom splitting is enabled, the split slice is included in both projections, matching the ImageJ-style logic:

```text
top projection:    slice 1 to split slice
bottom projection: split slice to final slice
```

## Notes

The Python script is designed as a general reusable preprocessing tool, not as a project-specific analysis script.

It is useful for routine conversion of DV microscopy stacks into TIFF projections before downstream analysis, figure preparation, or manual inspection.

The ImageJ macro is kept as a reference workflow and for cases where manual processing in Fiji is preferred.

## Limitations

- The Python script currently processes only the first timepoint of each DV file.
- Input files must end with `_D3D.dv`.
- The script assumes channel order is consistent across files.
- Intensity scaling values should be adjusted for each experiment.
- Rolling-ball background subtraction uses a fixed radius of 50 pixels.
