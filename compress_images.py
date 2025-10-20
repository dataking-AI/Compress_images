# -*- coding: utf-8 -*-
import os
import argparse
from io import BytesIO
from PIL import Image, ImageOps

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".webp")

def is_effectively_opaque(img: Image.Image) -> bool:
    """
    返回 True 表示：图像对外观来说是“完全不透明的”
    - 无 Alpha 通道：不透明
    - 有 Alpha 通道：仅当所有像素的 Alpha 都是 255 才算不透明
    - P 模式带 transparency：转成 RGBA 再检测
    """
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        lo, hi = alpha.getextrema()  # 极值范围
        return lo == 255 and hi == 255
    if img.mode == "P":
        if "transparency" in img.info:
            rgba = img.convert("RGBA")
            alpha = rgba.getchannel("A")
            lo, hi = alpha.getextrema()
            return lo == 255 and hi == 255
        return True  # P 且无 transparency，即无透明
    # 其他模式（RGB、L等）本身就不含透明
    return True


def has_alpha(img: Image.Image) -> bool:
    """判断图片是否带透明通道"""
    if img.mode in ("RGBA", "LA"):
        return True
    if img.mode == "P" and "transparency" in img.info:
        return True
    return False

def open_with_exif(path: str) -> Image.Image:
    """按 EXIF 方向打开"""
    img = Image.open(path)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    return img

def save_to_buffer(img: Image.Image, fmt: str, quality: int) -> bytes:
    """按指定格式和质量保存到内存并返回字节"""
    buf = BytesIO()
    params = {}
    if fmt == "JPEG":
        if img.mode != "RGB":
            img = img.convert("RGB")
        params.update(dict(quality=quality, optimize=True, progressive=True, subsampling=2))
    elif fmt == "WEBP":
        params.update(dict(quality=quality, method=6))
    elif fmt == "PNG":
        params.update(dict(optimize=True, compress_level=9))
    else:
        raise ValueError("Unsupported format in save_to_buffer")

    img.save(buf, format=fmt, **params)
    return buf.getvalue()

def binary_search_quality(img: Image.Image, fmt: str, target_kb: int, qmin=10, qmax=95):
    """二分法搜索合适的质量以接近目标大小"""
    best_bytes = None
    best_q = qmin
    lo, hi = qmin, qmax
    while lo <= hi:
        mid = (lo + hi) // 2
        data = save_to_buffer(img, fmt, mid)
        size_kb = len(data) / 1024.0
        if size_kb <= target_kb:
            best_bytes = data
            best_q = mid
            lo = mid + 1
        else:
            hi = mid - 1
    if best_bytes is None:
        data = save_to_buffer(img, fmt, max(hi, qmin))
        return data, max(hi, qmin)
    return best_bytes, best_q

def compress_image(input_path, output_dir, target_size_kb=500, max_resolution=None, keep_png=False):
    """压缩单张图片"""
    img = open_with_exif(input_path)

    # 可选调整分辨率
    if max_resolution:
        img.thumbnail(max_resolution, Image.Resampling.LANCZOS)

    ext = os.path.splitext(input_path)[1].lower()
    opaque = is_effectively_opaque(img)

    if keep_png and ext == ".png":
        fmt, out_ext = "PNG", ".png"
    else:
        if opaque:
            fmt, out_ext = "JPEG", ".jpg"   # 真正不透明：用 JPEG
        else:
            fmt, out_ext = "WEBP", ".webp"  # 存在透明像素：用 WebP（保透明）

    print("[detector] opaque={}, mode={}, keep_png={}".format(opaque, img.mode, keep_png))


    # 文件名加 "_compressed"
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, base_name + "_compressed" + out_ext)

    # 压缩保存
    if fmt in ("JPEG", "WEBP"):
        data, q = binary_search_quality(img, fmt, target_size_kb)
        with open(output_path, "wb") as f:
            f.write(data)
        size_kb = len(data) / 1024.0
        print("✅ {} -> {:.2f}KB (Q={}, fmt={})".format(base_name, size_kb, q, fmt))
    else:
        img.save(output_path, format="PNG", optimize=True, compress_level=9)
        size_kb = os.path.getsize(output_path) / 1024.0
        print("✅ {} -> {:.2f}KB (fmt=PNG, 无损)".format(base_name, size_kb))

def batch_compress(input_dir, output_dir, target_size_kb=500, max_resolution=None, keep_png=False):
    """批量压缩文件夹内的图片"""
    os.makedirs(output_dir, exist_ok=True)

    # 检查是否有可压缩图片
    images = [f for f in os.listdir(input_dir) if f.lower().endswith(SUPPORTED_EXTS)]
    if not images:
        print("⚠️ 目录 '{}' 下没有可压缩的图片文件。".format(input_dir))
        return

    for name in images:
        in_path = os.path.join(input_dir, name)
        try:
            compress_image(in_path, output_dir, target_size_kb, max_resolution, keep_png)
        except Exception as e:
            print("❌ {} 压缩失败: {}".format(name, e))

def main():
    parser = argparse.ArgumentParser(description="批量压缩图片到指定大小，可选调整分辨率。支持透明图与 PNG 保留。")
    parser.add_argument("--input", type=str, default="~/视频", help="输入文件夹路径（支持 ~）")
    parser.add_argument("--output", type=str, default="~/视频/compressed", help="输出文件夹路径（支持 ~）")
    parser.add_argument("--size", type=int, default=500, help="目标大小 (KB)")
    parser.add_argument("--width", type=int, help="目标宽度（可选）")
    parser.add_argument("--height", type=int, help="目标高度（可选）")
    parser.add_argument("--keep-png", action="store_true", help="PNG 图片保持 PNG 格式输出（无损优化）")

    args = parser.parse_args()

    # ✅ 自动展开 ~ 为绝对路径
    input_dir = os.path.expanduser(args.input)
    output_dir = os.path.expanduser(args.output)

    resolution = (args.width, args.height) if (args.width and args.height) else None

    batch_compress(input_dir, output_dir, args.size, resolution, args.keep_png)

if __name__ == "__main__":
    main()
