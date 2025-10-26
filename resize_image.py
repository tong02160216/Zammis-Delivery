from pathlib import Path
from datetime import datetime
from PIL import Image

# 要处理的原始图片路径
SRC = Path(r"F:\code\zammi\Zammis-Delivery\屏幕截图 2025-10-16 105916.png")


def backup_file(src: Path) -> Path:
    """创建备份文件，返回备份路径"""
    if not src.exists():
        raise FileNotFoundError(f"找不到文件: {src}")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    bak = src.with_name(src.stem + "_bak_" + ts + src.suffix)
    src.replace(bak)  # 移动原文件到备份名（原地替换）
    # 将备份文件复制回原名 so we still have original filename for output
    bak.copy = bak  # placeholder to keep reference
    return bak


def resize_image(src: Path, scale_divisor: int = 10) -> Path:
    """把 src 图片缩小为原来的 1/scale_divisor，输出为 *_small.ext，返回输出路径。"""
    if not src.exists():
        raise FileNotFoundError(f"找不到文件: {src}")

    im = Image.open(src)
    w, h = im.size
    new_w = max(1, w // scale_divisor)
    new_h = max(1, h // scale_divisor)
    im_small = im.resize((new_w, new_h), Image.LANCZOS)

    out_path = src.with_name(src.stem + "_small" + src.suffix)
    im_small.save(out_path)
    return out_path


def main():
    src = SRC
    if not src.exists():
        print(f"错误：找不到源文件 {src}")
        return

    # 不直接覆盖原文件：先创建一个时间戳备份，然后复制备份回原文件名以便后续生成 small 文件
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    bak = src.with_name(src.stem + "_bak_" + ts + src.suffix)
    src.rename(bak)  # 重命名为备份
    print(f"已创建备份: {bak}")

    # 将备份复制回原始文件名，以保留原始路径为操作输入
    # 使用 Pillow 打开备份并保存为原名
    im = Image.open(bak)
    im.save(src)

    out = resize_image(src, 10)
    print(f"已生成缩小图片: {out} （尺寸 {im.size} -> {(out)}）")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('发生错误:', e)
        raise
