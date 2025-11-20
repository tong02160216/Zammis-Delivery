import pygame
import cv2
import sys
from pathlib import Path
import glob

# 前景与背景图片的绝对路径（请确保文件存在）
FOREGROUND_FRAMES_PATTERN = r"F:\code\zammi\Zammis-Delivery\zammi_*.png"
BACKGROUND_FRAMES_PATTERN = r"F:\code\zammi\Zammis-Delivery\邮局 - *.png"
VIDEO_PATH = Path(r"F:\code\zammi\Zammis-Delivery\875b55be8f5a0e72b6e28c650a49a795.mp4")


def load_image(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到图片: {path}")
    # 使用 str(path) 以兼容 pygame
    return pygame.image.load(str(path))


def load_png_frames(pattern: str):
    """加载PNG序列帧"""
    frame_files = sorted(glob.glob(pattern))
    if not frame_files:
        raise FileNotFoundError(f"找不到匹配的PNG文件: {pattern}")
    
    frames = []
    print(f"正在加载 {len(frame_files)} 个PNG帧...")
    
    for frame_file in frame_files:
        surface = pygame.image.load(frame_file).convert_alpha()
        frames.append(surface)
    
    # 所有帧使用相同的持续时间（100毫秒）
    durations = [100] * len(frames)
    
    return frames, durations


def main():
    pygame.init()

    # 先创建临时窗口以便加载PNG帧
    temp_screen = pygame.display.set_mode((100, 100))
    
    # 加载背景序列帧动画（邮局）
    bg_frames, bg_durations = load_png_frames(BACKGROUND_FRAMES_PATTERN)
    bg_current_frame = 0
    bg_frame_timer = 0
    print(f"✅ 成功加载 {len(bg_frames)} 帧背景动画")
    
    # 加载前景PNG序列帧动画（角色）
    fg_frames, fg_durations = load_png_frames(FOREGROUND_FRAMES_PATTERN)
    fg_current_frame = 0
    fg_frame_timer = 0
    print(f"✅ 成功加载 {len(fg_frames)} 帧角色动画")

    # 获取第一帧背景作为基础
    bg = bg_frames[0]
    
    # 转换背景加速显示
    bg_frames_converted = []
    for frame in bg_frames:
        try:
            if getattr(frame, 'get_alpha', lambda: None)() is not None or frame.get_bitsize() == 32:
                bg_frames_converted.append(frame.convert_alpha())
            else:
                bg_frames_converted.append(frame.convert())
        except Exception:
            bg_frames_converted.append(frame)
    bg_frames = bg_frames_converted
    bg = bg_frames[0]

    # 交互点参数（门口位置）
    circle_radius = 40  # 触发判定半径（检测用，较宽松）
    visual_radius = 10  # 白色圆点的视觉半径（较小）
    cx = 550  # X坐标在500-600之间
    cy = 600  # Y坐标限制为500-700范围内，默认放在600

    # 窗口大小与背景一致
    screen = pygame.display.set_mode(bg.get_size())
    pygame.display.set_caption("WASD 控制 — Esc 退出 | GIF 动画")

    clock = pygame.time.Clock()

    # 初始位置在画面最左边（使用第一帧获取尺寸）
    fg = fg_frames[fg_current_frame]
    x = 0  # 放置在最左边
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
    prev_collided = False
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

        # 更新背景动画帧
        bg_frame_timer += clock.get_time()
        if bg_frame_timer >= bg_durations[bg_current_frame]:
            bg_frame_timer = 0
            bg_current_frame = (bg_current_frame + 1) % len(bg_frames)
            bg = bg_frames[bg_current_frame]
        
        # 更新前景动画帧
        fg_frame_timer += clock.get_time()
        if fg_frame_timer >= fg_durations[fg_current_frame]:
            fg_frame_timer = 0
            fg_current_frame = (fg_current_frame + 1) % len(fg_frames)
            fg = fg_frames[fg_current_frame]
        
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

        # Y轴边界限制：始终生效，将角色中心 Y 限制在 500 到 700 之间
        # 计算角色中心点对应的左上角 y 可取范围
        half_height = fg.get_height() // 2
        min_y = 500 - half_height  # 中心点最小值对应的左上角Y坐标
        max_y = 700 - half_height  # 中心点最大值对应的左上角Y坐标
        y = max(min_y, min(max_y, y))
        # 同时确保交互点（蓝色圆圈）Y 坐标在 500-700 范围内
        cy = max(500, min(700, cy))

        # 绘制背景（循环播放的邮局序列帧）
        screen.fill((50, 50, 50))
        try:
            screen.blit(bg, (0, 0))
        except Exception as e:
            print(f"背景绘制错误: {e}")
            pass
        screen.blit(fg, (int(x), int(y)))

        # 碰撞检测:使用角色中心点作为检测点
        character_center_x = int(x) + fg.get_width() // 2
        character_center_y = int(y) + fg.get_height() // 2
        # 检测点偏移：向左40像素，向下100像素
        detect_x = character_center_x - 40
        detect_y = character_center_y + 100

        # 计算检测点与交互点的距离
        dist_x = detect_x - cx
        dist_y = detect_y - cy
        distance = (dist_x ** 2 + dist_y ** 2) ** 0.5

        # 实际触发仅在玩家检测点触碰白点时发生
        collided = distance <= circle_radius

        # 调试：在角色中心画小红点，显示距离与状态文本
        try:
            pygame.draw.circle(screen, (255, 0, 0), (detect_x, detect_y), 4)
        except Exception:
            pass

        dbg_text = font.render(f"dist={int(distance)} r={circle_radius} collided={collided}", True, (255, 255, 255))
        dbg_bg = pygame.Surface((dbg_text.get_width() + 8, dbg_text.get_height() + 6), pygame.SRCALPHA)
        dbg_bg.fill((0, 0, 0, 160))
        screen.blit(dbg_bg, (8, 40))
        screen.blit(dbg_text, (12, 42))

        # 在首次碰撞时在控制台打印一条记录，便于确认触发
        if collided and not prev_collided:
            print(f"触发：distance={distance:.1f}, circle_radius={circle_radius}, detect=({detect_x},{detect_y}), dot=({cx},{cy})")
        prev_collided = collided
        
        # 绘制交互点标记（白色实心圆，较小的视觉半径）
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), visual_radius)
        # 不再绘制白点周围的额外可视化圈（按要求）

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

            # 固定显示文字：玩家接触白色圆点时显示完成提示
            text = "取信完毕"

            # 大号字体，基于屏幕高度自适应
            large_font_size = max(24, screen.get_height() // 12)
            large_font = pygame.font.SysFont(None, large_font_size)
            txt_surf = large_font.render(text, True, (0, 0, 0))

            # 将文本居中显示在白色框内
            txt_x = box_x + (box_w - txt_surf.get_width()) // 2
            txt_y = box_y + (h - txt_surf.get_height()) // 2
            screen.blit(txt_surf, (txt_x, txt_y))

        # 绘制坐标标尺
        ruler_font = pygame.font.SysFont(None, 16)
        ruler_color = (255, 255, 0)  # 黄色
        
        # 左侧 Y 轴标尺（每50像素一个刻度）
        for y_pos in range(0, screen.get_height() + 1, 50):
            line_length = 15 if y_pos % 100 == 0 else 8
            pygame.draw.line(screen, ruler_color, (0, y_pos), (line_length, y_pos), 2)
            if y_pos % 100 == 0 or y_pos in [250, 279, 300, 319, 350]:  # 主要刻度和关键位置
                y_text = ruler_font.render(str(y_pos), True, ruler_color)
                screen.blit(y_text, (line_length + 2, y_pos - 8))
        
        # 顶部 X 轴标尺（每50像素一个刻度）
        for x_pos in range(0, screen.get_width() + 1, 50):
            line_length = 15 if x_pos % 100 == 0 else 8
            pygame.draw.line(screen, ruler_color, (x_pos, 0), (x_pos, line_length), 2)
            if x_pos % 100 == 0 or x_pos in [500, 550, 600]:  # 主要刻度和关键位置
                x_text = ruler_font.render(str(x_pos), True, ruler_color)
                screen.blit(x_text, (x_pos - 10, line_length + 2))
        
        # 绘制坐标轴线
        pygame.draw.line(screen, ruler_color, (0, 0), (0, screen.get_height()), 2)  # Y轴
        pygame.draw.line(screen, ruler_color, (0, 0), (screen.get_width(), 0), 2)  # X轴
        
        # 添加坐标轴说明
        axis_label_font = pygame.font.SysFont(None, 14)
        x_label = axis_label_font.render("X ->", True, ruler_color)
        y_label = axis_label_font.render("Y", True, ruler_color)
        y_label_down = axis_label_font.render("|", True, ruler_color)
        y_label_arrow = axis_label_font.render("v", True, ruler_color)
        screen.blit(x_label, (20, 2))
        screen.blit(y_label, (2, 20))
        screen.blit(y_label_down, (5, 30))
        screen.blit(y_label_arrow, (4, 38))
        
        # 显示当前角色中心位置以便与交互点比较
        pos_text = ruler_font.render(f"Center: ({character_center_x}, {character_center_y})", True, (255, 255, 0))
        pos_bg = pygame.Surface((pos_text.get_width() + 8, pos_text.get_height() + 4), pygame.SRCALPHA)
        pos_bg.fill((0, 0, 0, 150))
        screen.blit(pos_bg, (screen.get_width() - pos_text.get_width() - 12, screen.get_height() - 30))
        screen.blit(pos_text, (screen.get_width() - pos_text.get_width() - 8, screen.get_height() - 28))

        # 在右上角显示当前前景帧索引和是否启用 Y 轴限制，方便调试
        clamp_active = fg_current_frame < 8
        frame_status = f"Frame: {fg_current_frame}  Clamp: {'ON' if clamp_active else 'OFF'}"
        frame_text = font.render(frame_status, True, (255, 255, 255))
        frame_bg = pygame.Surface((frame_text.get_width() + 8, frame_text.get_height() + 6), pygame.SRCALPHA)
        frame_bg.fill((0, 0, 0, 140))
        fr_x = screen.get_width() - (frame_text.get_width() + 20)
        screen.blit(frame_bg, (fr_x, 8))
        screen.blit(frame_text, (fr_x + 4, 10))

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
