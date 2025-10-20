# Image Batch Compression Tool

This Python script compresses all images in a specified folder to a target file size (in KB).
It automatically detects real transparency and selects the most suitable output format (JPEG, WebP, or PNG).
It also supports optional resolution adjustment, PNG preservation, and user-friendly paths with `~`.

---

## Features

* Batch compress images (`.jpg`, `.jpeg`, `.png`, `.webp`)
* Automatically detect **real transparency**

  * Transparent images → WebP (keeps alpha channel)
  * Non-transparent images → JPEG
* Optionally keep PNG format with `--keep-png` (lossless)
* Automatically append `_compressed` to output filenames
* Supports `~` in paths (user home directory)
* Checks if input folder contains any valid images before processing
* Optional width and height constraints
* Uses binary search to adjust quality to meet target size

---

## Requirements

Install Python 3.6 or later and the Pillow library:

```bash
pip install pillow
```

If Pillow does not support WebP on your system:

```bash
sudo apt install libwebp-dev
pip install --upgrade pillow
```

---

## Directory Structure

```
compress_images/
│
├── compress_images.py
└── README.md
```

---

## Usage

### 1. Compress default directory

```bash
python3 compress_images.py --size 500
```

Compresses images in `~/Videos` and outputs to `~/Videos/compressed`.

---

### 2. Specify input and output folders

```bash
python3 compress_images.py --input ~/Pictures --output ~/Pictures/compressed --size 400
```

---

### 3. Limit resolution

```bash
python3 compress_images.py --size 300 --width 1280 --height 720
```

---

### 4. Keep PNG format (lossless)

```bash
python3 compress_images.py --size 500 --keep-png
```

---

## Arguments

| Argument     | Type   | Default               | Description                             |
| ------------ | ------ | --------------------- | --------------------------------------- |
| `--input`    | `str`  | `~/Videos`            | Input directory path (supports `~`)     |
| `--output`   | `str`  | `~/Videos/compressed` | Output directory path (supports `~`)    |
| `--size`     | `int`  | `500`                 | Target file size in KB                  |
| `--width`    | `int`  | *(optional)*          | Target maximum width                    |
| `--height`   | `int`  | *(optional)*          | Target maximum height                   |
| `--keep-png` | `bool` | `False`               | Keep PNG format (lossless optimization) |

---

## Compression Logic

1. Scan the input folder for valid image files.
2. If no images are found, the program prints:

   ```
   No compressible images found in '~/Pictures'.
   ```
3. For each image:

   * Detect whether it contains **any truly transparent pixels**.
   * Format selection:

     * Transparent → WebP
     * Non-transparent → JPEG
     * With `--keep-png` → PNG
4. Adjust resolution using `thumbnail()` if width/height are set.
5. Dynamically adjust quality (range 10–95) using binary search to reach the target size.
6. Output filenames will automatically append `_compressed`.

---

## Example Output

```
✅ photo_compressed.jpg -> 492.18KB (Q=87, fmt=JPEG)
✅ icon_compressed.webp -> 278.44KB (Q=95, fmt=WEBP)
✅ logo_compressed.png -> 742.31KB (fmt=PNG, lossless)
⚠️ No compressible images found in '~/Pictures'.
```

---

## Format Selection Rules

| Image Type                      | Output Format |
| ------------------------------- | ------------- |
| Contains transparent pixels     | WebP          |
| No transparency (including PNG) | JPEG          |
| `--keep-png` specified          | PNG           |

---

## Notes and Limitations

1. PNG compression is lossless and cannot strictly match the target size.
2. WebP compression offers excellent efficiency but may not be supported by older software.
3. The target size is an upper limit; actual files are usually smaller.
4. Existing files in the output folder will be overwritten.
5. The maximum quality is 95; higher values have negligible visual improvement.

---

## Recommended Use Cases

| Scenario                       | Recommended Format  | Reason                               |
| ------------------------------ | ------------------- | ------------------------------------ |
| Photographs                    | JPEG / WebP (lossy) | High compression, minor quality loss |
| Logos, Icons, UI Assets        | PNG (lossless)      | Perfect color accuracy               |
| Screenshots, Documents         | JPEG                | Compact and clear                    |
| Transparent images             | WebP                | Keeps transparency, smaller size     |
| High compatibility requirement | JPEG / PNG          | Universally supported                |

---

## Command Examples

```bash
# Compress ~/Videos images to ~500KB
python3 compress_images.py --size 500

# Compress images with resolution limit
python3 compress_images.py --input ~/Pictures --output ~/Pictures/compressed --size 300 --width 1280 --height 720

# Keep PNG format for all PNG files
python3 compress_images.py --size 500 --keep-png
```

---

## Author

**Zongzhuo**
Image Batch Compression Script
Last Updated: 2025-10-20
