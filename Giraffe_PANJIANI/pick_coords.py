#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式背景图关键位置坐标获取工具（像素风背景 GIF）

功能概述：
- 弹出指定的 GIF 背景图（像素风），支持用户通过鼠标点击图像上的关键点（如楼梯口、阿豆初始点），
    点击后终端实时输出对应的原始图像像素坐标（X, Y），并可将坐标保存到项目根目录下的 `picked_coords.json`（格式 {"1": [x,y], ...}）。

技术栈：Pillow + tkinter（Python 3.8+），无其他第三方依赖。兼容 Windows / macOS。

主要特性与要求实现：
- 只接受 GIF 格式（若输入非 GIF，会提示并退出）。
- 多帧 GIF 时读取第一帧进行定位，并在终端提示用户注意帧一致性。
- 若图片超出屏幕（按屏幕宽高的 `scale` 比例，默认 0.8），自动按等比例缩放显示，点击坐标会按缩放比例还原为原图坐标。
- 使用高质量重采样 `Image.Resampling.LANCZOS` 保持像素风画质。
- 点击后可通过弹窗输入楼层编号以保存该坐标，支持多次点击与保存。

使用方法示例：
        # 在脚本目录运行（若背景图与脚本同目录）
        python pick_coords.py background.gif

        # 或传入绝对路径（Windows）
        python pick_coords.py "C:\\Users\\you\\Desktop\\giraffe_house.gif"

输出示例：
- 启动时会先在终端输出：背景图原始分辨率：宽度XXX像素 × 高度YYY像素
- 然后输出：图像缩放比例：0.8（若需调整，可修改代码中 scale 变量）
- 每次点击后输出：点击位置坐标：X=xxx, Y=yyy，并提示是否保存为楼层坐标

注意事项：
- 若为多帧 GIF，脚本只读取第一帧用于定位，请确保各帧楼梯位置一致或先导出对应帧。
- 若 tkinter 在运行环境未安装或无法启动，程序会给出明确错误提示。
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import traceback
from PIL import Image, ImageTk
from tkinter import filedialog

# ---------------------- 可配置变量（请在此修改） ----------------------
# 背景图路径：支持绝对路径或相对路径（当脚本与背景图同目录时可直接填文件名）
# 默认背景图路径（可改为你的长颈鹿家 GIF 文件名或绝对路径）
BACKGROUND_PATH = "giraffe_house.gif"
# 当屏幕分辨率不足以完整显示原图时，窗口按屏幕的 scale 比例显示（默认 0.8 -> 80% 屏幕）
scale = 0.8
# 点击坐标保存文件（相对于脚本目录）
PICKED_COORDS_FILE = "picked_coords.json"
# 当屏幕分辨率不足以完整显示原图时，窗口按屏幕的 scale 比例显示（默认 0.8 -> 80% 屏幕）
scale = 0.8
# 点击坐标保存文件（相对于脚本目录）
PICKED_COORDS_FILE = "picked_coords.json"
# ---------------------------------------------------------------------


def print_and_flush(msg: str):
    # 同步输出到终端并写入本地日志文件，便于在 GUI/终端被捕获问题时排查
    try:
        print(msg)
        sys.stdout.flush()
    except Exception:
        pass
    try:
        with open("pick_coords.log", "a", encoding="utf-8") as lf:
            lf.write(msg.replace("\n", "") + "\n")
    except Exception:
        pass


def validate_and_open_image(path: str):
    """图像读取与校验模块
    - 检查文件存在性
    - 校验是否为 GIF 格式
    - 读取第一帧并返回 PIL.Image 对象，以及是否为多帧 GIF 的标识
    """
    if not os.path.isfile(path):
        print_and_flush("背景图路径错误，请检查文件位置")
        raise FileNotFoundError(f"File not found: {path}")

    try:
        img = Image.open(path)
    except Exception as e:
        print_and_flush("无法打开图片文件，请检查文件是否为有效图片")
        raise

    fmt = (img.format or "").upper()
    if fmt != "GIF":
        print_and_flush("请选择GIF格式的背景图")
        raise ValueError("Unsupported image format: " + fmt)

    is_animated = getattr(img, "is_animated", False) or getattr(img, "n_frames", 1) > 1
    if is_animated:
        print_and_flush("当前为多帧GIF，已读取第一帧用于坐标定位，请确保各帧楼梯位置一致")

    # 读取第一帧并转换为 RGBA
    try:
        img.seek(0)
    except Exception:
        pass
    frame = img.convert("RGBA")
    return frame, is_animated


def compute_display_image(img: Image.Image, screen_w: int, screen_h: int, config_scale: float):
    """窗口创建与图像缩放适配模块
    - 按 config_scale（如 0.8）作为屏幕占比阈值，若原图超过该阈值则缩放
    - 返回 (display_img, applied_ratio)，applied_ratio 为实际缩放比例（<=1.0）
    """
    img_w, img_h = img.width, img.height
    screen_max_w = int(screen_w * config_scale)
    screen_max_h = int(screen_h * config_scale)

    # 默认不缩放
    ratio = 1.0
    if img_w > screen_max_w or img_h > screen_max_h:
        ratio = min(screen_max_w / img_w, screen_max_h / img_h)

    # 使用高质量重采样以保持像素风格的清晰（Lanczos）
    try:
        resample = Image.Resampling.LANCZOS
    except Exception:
        # Pillow 旧版本回退
        try:
            resample = Image.LANCZOS
        except Exception:
            resample = Image.NEAREST

    if ratio < 1.0:
        new_w = max(1, int(img_w * ratio))
        new_h = max(1, int(img_h * ratio))
        display_img = img.resize((new_w, new_h), resample=resample)
    else:
        display_img = img.copy()

    return display_img, ratio


def launch_viewer(img: Image.Image, applied_ratio: float):
    """创建 tkinter 窗口并绑定点击事件
    点击后计算原图坐标并输出到终端
    """
    root = tk.Tk()
    root.title("背景图关键位置坐标获取")

    img_w, img_h = img.width, img.height
    canvas = tk.Canvas(root, width=img_w, height=img_h, highlightthickness=0)
    canvas.pack()

    # 转换为 PhotoImage 并显示
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

    def on_click(event):
        # event.x/event.y 是相对于画布（显示图像）的坐标
        disp_x, disp_y = event.x, event.y
        if disp_x < 0 or disp_y < 0 or disp_x >= img_w or disp_y >= img_h:
            # 点击在图像外部（不太可能，但做保护）
            return
        if applied_ratio <= 0:
            applied_ratio_local = 1.0
        else:
            applied_ratio_local = applied_ratio

            orig_x = int(disp_x / applied_ratio_local)
            orig_y = int(disp_y / applied_ratio_local)
            # 仅打印坐标，不自动保存到文件
            coord_text = f"点击位置坐标：X={orig_x}, Y={orig_y}"
            print_and_flush(coord_text)

            # 复制到剪贴板（便于粘贴到代码或其他地方）
            try:
                # root 是外层函数的 tkinter.Tk() 实例，可直接使用 clipboard
                clip_text = f"{orig_x},{orig_y}"
                root.clipboard_clear()
                root.clipboard_append(clip_text)
                # 确保剪贴板更新
                root.update()
                print_and_flush(f"已复制到剪贴板：{clip_text}")
            except Exception as e:
                print_and_flush(f"无法复制到剪贴板：{e}")

    # 鼠标移动时显示悬浮坐标提示（覆盖在图片上）
    def on_motion(event):
        disp_x, disp_y = event.x, event.y
        if disp_x < 0 or disp_y < 0 or disp_x >= img_w or disp_y >= img_h:
            # 超出图像范围则清除提示
            canvas.delete('tooltip')
            return

        # 计算原图坐标
        if applied_ratio <= 0:
            applied_ratio_local = 1.0
        else:
            applied_ratio_local = applied_ratio
        orig_x = int(disp_x / applied_ratio_local)
        orig_y = int(disp_y / applied_ratio_local)

        # 准备提示文本
        text = f"X={orig_x}, Y={orig_y}"
        padding = 4

        # 清除旧提示
        canvas.delete('tooltip')

        # 计算文本尺寸（使用 canvas 的测量能力）
        # 暂时创建文本以测宽度，然后用矩形背景
        temp = canvas.create_text(0, 0, text=text, anchor='nw', font=('Consolas', 12))
        bbox = canvas.bbox(temp)
        if bbox:
            tx0, ty0, tx1, ty1 = bbox
            text_w = tx1 - tx0
            text_h = ty1 - ty0
        else:
            text_w = len(text) * 7
            text_h = 16
        canvas.delete(temp)

        # 位置：优先显示在光标右下方，若超出边界则向左或向上调整
        box_x = disp_x + 12
        box_y = disp_y + 12
        if box_x + text_w + padding * 2 > img_w:
            box_x = disp_x - 12 - text_w - padding * 2
        if box_y + text_h + padding * 2 > img_h:
            box_y = disp_y - 12 - text_h - padding * 2

        # 绘制背景矩形和文本，统一使用 tag 'tooltip'
        rect = canvas.create_rectangle(box_x, box_y, box_x + text_w + padding * 2, box_y + text_h + padding * 2, fill='#ffffcc', outline='#000000', tags='tooltip')
        txt = canvas.create_text(box_x + padding, box_y + padding, text=text, anchor='nw', font=('Consolas', 12), tags='tooltip')

    def on_leave(event):
        canvas.delete('tooltip')

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Motion>", on_motion)
    canvas.bind("<Leave>", on_leave)

    # 当用户关闭窗口时退出程序
    def on_close():
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


def main():
    # 支持命令行传参覆盖顶部变量
    global BACKGROUND_PATH, scale
    if len(sys.argv) >= 2:
        BACKGROUND_PATH = sys.argv[1]

    # 如果指定路径不存在，尝试在当前目录自动查找 GIF 文件
    if not os.path.isfile(BACKGROUND_PATH):
        # 搜索工作目录下的 gif 文件
        cwd_gifs = [f for f in os.listdir('.') if f.lower().endswith('.gif')]
        if len(cwd_gifs) == 1:
            BACKGROUND_PATH = cwd_gifs[0]
            print_and_flush(f"未找到指定背景，已在当前目录自动选择 GIF：{BACKGROUND_PATH}")
        elif len(cwd_gifs) > 1:
            # 尝试优先匹配常见关键字（中文或英文）
            preferred = None
            for name in cwd_gifs:
                if "长颈鹿" in name or "giraffe" in name or "长" in name:
                    preferred = name
                    break
            if preferred:
                BACKGROUND_PATH = preferred
                print_and_flush(f"未找到指定背景，已在当前目录自动选择匹配 GIF：{BACKGROUND_PATH}")
            else:
                # 弹出文件选择对话让用户选择
                try:
                    root_fd = tk.Tk()
                    root_fd.withdraw()
                    chosen = filedialog.askopenfilename(title="请选择背景 GIF 文件", filetypes=[("GIF files", "*.gif" )], initialdir=os.getcwd())
                    root_fd.destroy()
                    if chosen:
                        BACKGROUND_PATH = chosen
                        print_and_flush(f"已选择背景：{BACKGROUND_PATH}")
                except Exception:
                    # 回退为控制台选择
                    print_and_flush("当前目录存在多个 GIF 文件，请在命令行中指定要打开的文件路径（或将目标 GIF 放在脚本目录并重试）。")
        else:
            # 没有找到任何 GIF，给出更详细的诊断提示并退出
            print_and_flush(f"背景图路径错误，请检查文件位置。当前工作目录：{os.getcwd()}，未找到 GIF 文件，或传入路径无效。")
            print_and_flush("你可以：\n  - 将 '长颈鹿家.gif' 放到此目录；\n  - 或在运行时传入绝对路径：python pick_coords.py \"F:\\\\...\\长颈鹿家.gif\"\n  - 或在运行后使用文件选择对话（如果出现）。")
            sys.exit(1)

    try:
        # 读取并校验图片
        frame, is_animated = validate_and_open_image(BACKGROUND_PATH)

        orig_w, orig_h = frame.width, frame.height
        print_and_flush(f"背景图原始分辨率：宽度{orig_w}像素 × 高度{orig_h}像素")
        
        # 固定目标尺寸为 1280×720
        target_w, target_h = 1280, 720
        print_and_flush(f"目标显示尺寸：{target_w}×{target_h}")
        
        # 缩放到目标尺寸
        try:
            resample = Image.Resampling.LANCZOS
        except Exception:
            try:
                resample = Image.LANCZOS
            except Exception:
                resample = Image.NEAREST
        
        display_img = frame.resize((target_w, target_h), resample=resample)
        # 计算缩放比例（用于将显示坐标转换为原图坐标）
        applied_ratio = target_w / orig_w
        print_and_flush(f"缩放比例：{applied_ratio:.4f} (原图{orig_w}×{orig_h} -> 显示{target_w}×{target_h})")

        # 启动带点击事件的窗口
        try:
            launch_viewer(display_img, applied_ratio)
        except Exception as e:
            print_and_flush(f"无法启动图形窗口，请检查 tkinter 环境：{e}")
            traceback.print_exc()
            sys.exit(1)

    except FileNotFoundError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)
    except Exception as e:
        print_and_flush(f"运行时发生未处理错误：{e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
