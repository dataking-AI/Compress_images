# 图片批量压缩工具

该脚本基于 **Python + Pillow** 实现，用于批量压缩指定文件夹下的图片到目标大小（单位：KB）。
脚本可自动判断图片透明性，智能选择输出格式（JPEG / WebP / PNG），并可选择是否保留 PNG 格式。
支持通过参数调整分辨率、目标体积、输入输出路径等。

---

## 功能特性

* 批量压缩图片（支持 JPG、JPEG、PNG、WebP）
* 自动判断是否包含真实透明像素

  * 有透明像素：输出 WebP
  * 无透明像素：输出 JPEG
* 支持 `--keep-png` 保留 PNG 格式（无损优化）
* 输出文件自动添加 `_compressed` 后缀
* 支持 `~` 符号路径展开（通用主目录路径）
* 自动检测输入文件夹是否包含图片
* 可选分辨率调整参数 `--width`、`--height`
* 二分法自动调整质量，逼近目标文件大小

---

## 环境依赖

需要 Python 3.6 及以上版本，并安装 Pillow：

```bash
pip install pillow
```

若系统未启用 WebP 支持，请先安装依赖：

```bash
sudo apt install libwebp-dev
pip install --upgrade pillow
```

---

## 目录结构

```
compress_images/
│
├── compress_images.py
└── README.md
```

---

## 使用方法

### 1. 压缩默认目录下的图片

```bash
python3 compress_images.py --size 500
```

将 `~/视频` 下的图片压缩至约 500KB，输出到 `~/视频/compressed`。

---

### 2. 指定输入与输出目录

```bash
python3 compress_images.py --input ~/图片 --output ~/图片/压缩后 --size 400
```

---

### 3. 限制输出分辨率

```bash
python3 compress_images.py --size 300 --width 1280 --height 720
```

---

### 4. 保留 PNG 格式输出（无损压缩）

```bash
python3 compress_images.py --size 500 --keep-png
```

---

## 参数说明

| 参数名          | 类型     | 默认值               | 说明                    |
| ------------ | ------ | ----------------- | --------------------- |
| `--input`    | `str`  | `~/视频`            | 输入图片文件夹路径（支持 `~`）     |
| `--output`   | `str`  | `~/视频/compressed` | 输出文件夹路径（支持 `~`）       |
| `--size`     | `int`  | `500`             | 目标文件大小（单位：KB）         |
| `--width`    | `int`  | *(可选)*            | 限制最大宽度                |
| `--height`   | `int`  | *(可选)*            | 限制最大高度                |
| `--keep-png` | `bool` | `False`           | PNG 图片保持 PNG 格式（无损优化） |

---

## 压缩逻辑说明

1. 读取图片并判断是否存在真实透明像素：

   * 若存在透明像素，则输出 WebP。
   * 若无透明像素，则输出 JPEG。
   * 若指定 `--keep-png`，则保持 PNG 格式。
2. 使用 Pillow 的 `thumbnail()` 函数调整分辨率（若指定宽高）。
3. 使用二分法自动调整质量（10–95），使文件尽量接近目标大小。
4. 输出文件名自动添加 `_compressed` 后缀。
5. 若输入目录中没有图片文件，则输出提示信息并退出。

---

## 输出示例

```
✅ photo_compressed.jpg -> 492.18KB (Q=87, fmt=JPEG)
✅ icon_compressed.webp -> 278.44KB (Q=95, fmt=WEBP)
✅ logo_compressed.png -> 742.31KB (fmt=PNG, 无损)
⚠️ 目录 '~/图片' 下没有可压缩的图片文件。
```

---

## 格式判断逻辑

| 图像特性            | 输出格式 |
| --------------- | ---- |
| 含透明像素           | WebP |
| 无透明像素（包括 PNG）   | JPEG |
| 启用 `--keep-png` | PNG  |

---

## 限制与说明

1. PNG 格式为无损压缩，无法严格控制目标大小，仅能略微减小体积。
2. WebP 压缩效率高，但在某些旧系统或软件中可能不兼容。
3. 目标大小表示“最大限制”，实际文件通常略小于设定值。
4. 输出文件若已存在，将被覆盖。
5. 脚本的最大 JPEG/WebP 质量为 95（高于此无明显画质提升）。

---

## 推荐使用策略

| 场景            | 推荐格式            | 原因         |
| ------------- | --------------- | ---------- |
| 摄影照片          | JPEG / WebP（有损） | 压缩率高，视觉损失小 |
| 图标、Logo、UI 素材 | PNG（无损）         | 保真度高       |
| 截图、文档图        | JPEG            | 体积小、清晰度足够  |
| 透明图像          | WebP            | 保留透明，体积更小  |
| 兼容性要求高        | JPEG / PNG      | 通用性好       |

---

## 示例命令汇总

```bash
# 压缩默认目录（~/视频）到 500KB
python3 compress_images.py --size 500

# 指定目录与分辨率
python3 compress_images.py --input ~/图片 --output ~/图片/压缩后 --size 300 --width 1280 --height 720

# 保持 PNG 格式输出
python3 compress_images.py --size 500 --keep-png
```

---

## 作者信息

**Zongzhuo**

图片批量压缩脚本

最后更新日期：2025-10-20

---

