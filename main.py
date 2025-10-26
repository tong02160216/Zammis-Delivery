import pygame
import cv2
import sys
from pathlib import Path

# 前景与背景图片的绝对路径（请确保文件存在）
FOREGROUND_PATH = Path(r"F:\code\zammi\Zammis-Delivery\屏幕截图 2025-10-16 105916.png")
BACKGROUND_PATH = Path(r"F:\code\zammi\Zammis-Delivery\屏幕截图 2025-10-11 171938.png")
VIDEO_PATH = Path(r"F:\code\zammi\Zammis-Delivery\875b55be8f5a0e72b6e28c650a49a795.mp4")


def load_image(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到图片: {path}")
    # 使用 str(path) 以兼容 pygame
    return pygame.image.load(str(path))


def main():
    pygame.init()

    # 加载图片
    bg = load_image(BACKGROUND_PATH)
    fg = load_image(FOREGROUND_PATH)

    # 转换加速显示：根据 Surface 是否含有 alpha 选择 convert/convert_alpha
    try:
        # 如果图片含有 alpha 通道，使用 convert_alpha() 否则 convert()
        if getattr(bg, 'get_alpha', lambda: None)() is not None or bg.get_bitsize() == 32:
            bg = bg.convert_alpha()
        else:
            bg = bg.convert()
    except Exception:
        pass
    try:
        if getattr(fg, 'get_alpha', lambda: None)() is not None or fg.get_bitsize() == 32:
            fg = fg.convert_alpha()
        else:
            fg = fg.convert()
    except Exception:
        pass

    # 在背景图上绘制装饰（右上角白色圆）——创建背景副本以避免修改原始 Surface
    try:
        bg_decor = bg.copy()
    except Exception:
        # 某些 Surface 类型可能不支持 copy(); 回退为直接使用 bg
        bg_decor = bg

    # 圆的参数（可调整）
    circle_margin = 12
    circle_radius = 20
    # 计算圆心位置（右上角，留出 margin）
    try:
        cx = bg_decor.get_width() - circle_margin - circle_radius
        cy = circle_margin + circle_radius
        pygame.draw.circle(bg_decor, (255, 255, 255), (cx, cy), circle_radius)
    except Exception:
        # 如果绘制失败，忽略装饰
        pass

    # 窗口大小与背景一致（使用带装饰的背景）
    screen = pygame.display.set_mode(bg_decor.get_size())
    pygame.display.set_caption("WASD 控制 — Esc 退出")

    clock = pygame.time.Clock()

    # 初始位置居中
    x = (screen.get_width() - fg.get_width()) // 2
    y = (screen.get_height() - fg.get_height()) // 2

    # 运动参数（每帧即时响应的简单实现，参考示例）
    speed = 5  # 每帧移动像素（可调整，增大使移动更灵敏）

    # 简单文字提示
    font = pygame.font.SysFont(None, 20)

    # 使用整数位置以匹配每帧位移
    x = int(x)
    y = int(y)

    # 文字框状态与分页：show_box 在碰撞时为 True，box_page 控制显示哪一页文本
    show_box = False
    box_page = 0  # 0: first text, 1: second text
    box_rect = None

    def play_video(path: Path):
        """播放视频（阻塞），播放结束或窗口关闭后返回。"""
        if not path.exists():
            print(f"找不到视频文件: {path}")
            return
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            print(f"无法打开视频: {path}")
            return

        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        delay = int(1000 / fps)

        print(f"开始播放视频: {path}")
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit(0)

            ret, frame = cap.read()
            if not ret:
                break

            # BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转为 surface
            surf = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
            # 缩放到窗口大小
            surf = pygame.transform.smoothscale(surf, screen.get_size())
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(delay)

        cap.release()
        print(f"视频播放结束: {path}")
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标左键点击时，如果文字框可见并且点击在框内，则翻页或播放视频
                if event.button == 1 and show_box:
                    mx, my = event.pos
                    try:
                        # 重新计算文字框区域以确保判定与绘制一致
                        h = screen.get_height() // 3
                        bx = 0
                        by = screen.get_height() - h
                        bw = screen.get_width()
                        if bx <= mx <= bx + bw and by <= my <= by + h:
                            # 如果在第二页，点击则播放视频并在播放后隐藏文字框
                            if box_page == 1:
                                play_video(VIDEO_PATH)
                                show_box = False
                                box_page = 0
                            else:
                                box_page = 1
                    except Exception:
                        pass

        keys = pygame.key.get_pressed()
        # WASD 或 箭头 - 每帧固定位移
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y += speed

        # 边界限制：保证前景图不跑出窗口
        x = max(0, min(screen.get_width() - fg.get_width(), x))
        y = max(0, min(screen.get_height() - fg.get_height(), y))

        # 绘制背景（带装饰）。先填充一个中性色作为回退，防止意外的黑屏
        screen.fill((50, 50, 50))
        try:
            screen.blit(bg_decor, (0, 0))
        except Exception:
            # 如果 blit 失败，尝试 blit 原始 bg
            try:
                screen.blit(bg, (0, 0))
            except Exception:
                pass
        screen.blit(fg, (int(x), int(y)))

        # 碰撞检测：前景与右上白色圆
        try:
            # fg_rect 使用当前前景位置和尺寸
            fg_rect = pygame.Rect(int(x), int(y), fg.get_width(), fg.get_height())
            # 圆心和半径（在主循环外定义时已计算）
            # cx, cy, circle_radius
            closest_x = max(fg_rect.left, min(cx, fg_rect.right))
            closest_y = max(fg_rect.top, min(cy, fg_rect.bottom))
            dist_sq = (closest_x - cx) ** 2 + (closest_y - cy) ** 2
            collided = dist_sq <= (circle_radius ** 2)
        except Exception:
            collided = False

        # 根据碰撞设置文字框显示状态
        show_box = collided

        # 如果文字框可见，则绘制（支持分页）
        if show_box:
            # 白色框占满底部三分之一区域
            h = screen.get_height() // 3
            box_x = 0
            box_y = screen.get_height() - h
            box_w = screen.get_width()
            box_rect = pygame.Rect(box_x, box_y, box_w, h)
            # 绘制白色背景块
            pygame.draw.rect(screen, (255, 255, 255), box_rect)

            # 根据页码显示不同文本
            if box_page == 0:
                text = "1234567890"
            else:
                text = "123456789098764123456789098765432"

            # 大号字体，基于屏幕高度自适应
            large_font_size = max(24, screen.get_height() // 12)
            large_font = pygame.font.SysFont(None, large_font_size)
            txt_surf = large_font.render(text, True, (0, 0, 0))

            # 将文本居中显示在白色框内
            txt_x = box_x + (box_w - txt_surf.get_width()) // 2
            txt_y = box_y + (h - txt_surf.get_height()) // 2
            screen.blit(txt_surf, (txt_x, txt_y))

        info = font.render("WASD 或 箭头 移动 — Esc 退出", True, (255, 255, 255))
        # 在左上角绘制半透明底背景以确保可读性
        info_bg = pygame.Surface((info.get_width() + 8, info.get_height() + 6), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 120))
        screen.blit(info_bg, (8, 8))
        screen.blit(info, (12, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("程序发生错误:", e)
        raise
