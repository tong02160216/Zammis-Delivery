import pygame
import cv2
import sys
from PIL import Image
from pathlib import Path
import glob

# 前景与背景图片的相对路径（请确保文件存在）
FOREGROUND_FRAMES_PATTERN = "Zammis-Delivery/zammi_*.png"
BACKGROUND_FRAMES_PATTERN = (
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0001.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0002.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0003.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0004.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0005.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0006.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0007.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0008.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0009.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0010.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0011.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0012.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0013.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0014.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0015.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0016.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0017.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0018.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0019.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0020.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0021.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0022.png," 
    "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0023.png"
)
VIDEO_PATH = Path("875b55be8f5a0e72b6e28c650a49a795.mp4")


def load_image(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到图片: {path}")
    # 使用 str(path) 以兼容 pygame
    return pygame.image.load(str(path))


def load_png_frames(pattern: str):
    """加载PNG序列帧"""
    # 支持逗号分隔的多个文件名
    if ',' in pattern:
        frame_files = [f.strip() for f in pattern.split(',') if f.strip()]
    else:
        frame_files = sorted(glob.glob(pattern))
    if not frame_files:
        raise FileNotFoundError(f"找不到匹配的PNG文件: {pattern}")
    frames = []
    print(f"正在加载 {len(frame_files)} 个PNG帧...")
    for frame_file in frame_files:
        surface = pygame.image.load(frame_file).convert_alpha()
        frames.append(surface)
    durations = [100] * len(frames)
    return frames, durations


def main():
    pygame.init()

    # 先创建临时窗口以便加载PNG帧
    temp_screen = pygame.display.set_mode((100, 100))
    
    # 加载背景序列帧动画（邮局）
    # 使用相对路径加载背景帧
    bg_frames, bg_durations = load_png_frames(
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0001.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0002.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0003.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0004.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0005.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0006.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0007.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0008.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0009.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0010.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0011.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0012.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0013.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0014.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0015.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0016.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0017.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0018.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0019.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0020.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0021.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0022.png," 
        "Zammis-Delivery/assets/Fruit stand scene_pig/Fruit_pig_0023.png"
    )
    bg_current_frame = 0
    bg_frame_timer = 0
    print(f"✅ 成功加载 {len(bg_frames)} 帧背景动画")
    
    # 加载前景PNG序列帧动画（角色）
    # 使用相对路径加载前景帧
    fg_frames, fg_durations = load_png_frames("Zammis-Delivery/zammi_*.png")
    fg_current_frame = 0
    fg_frame_timer = 0
    print(f"✅ 成功加载 {len(fg_frames)} 帧角色动画")

    # 获取第一帧背景作为基础
    bg = bg_frames[0]
    
    # 转换并缩小背景加速显示（缩放为原来的三分之二）
    bg_frames_converted = []
    for frame in bg_frames:
        try:
            w, h = frame.get_width(), frame.get_height()
            new_size = (int(w * 2 / 3), int(h * 2 / 3))
            scaled = pygame.transform.smoothscale(frame, new_size)
            if getattr(scaled, 'get_alpha', lambda: None)() is not None or scaled.get_bitsize() == 32:
                bg_frames_converted.append(scaled.convert_alpha())
            else:
                bg_frames_converted.append(scaled.convert())
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
    # box_rect 未使用，删除
    box_manual_hide = False  # 玩家主动收起文字框后，保持隐藏直到离开碰撞区

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
                # 鼠标左键点击时，如果文字框可见并且点击在框内，则切换文字或收起文字框
                if event.button == 1 and show_box:
                    mx, my = event.pos
                    try:
                        h = screen.get_height() // 3
                        bx = 0
                        by = screen.get_height() - h
                        bw = screen.get_width()
                        if bx <= mx <= bx + bw and by <= my <= by + h:
                            if box_page == 0:
                                box_page = 1
                            else:
                                show_box = False
                                box_page = 0
                                box_manual_hide = True
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
        if collided:
            if not box_manual_hide:
                show_box = True
        else:
            show_box = False
            box_manual_hide = False

        # 如果文字框可见，则绘制（支持分页）
        if show_box:
            try:
                box_w = screen.get_width()
                h = screen.get_height() // 3
                dialogue_img = pygame.image.load("Zammis-Delivery/assets/Dialogue box materials/Pig Dialogue Box1_Worried.png").convert_alpha()
                dw = int(box_w * 0.8)
                dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                dx = (box_w - dw) // 2
                dy = screen.get_height() - dh
                screen.blit(dialogue_img, (dx, dy))

                # 根据 box_page 显示不同内容
                if box_page == 0:
                    text = "Thanks for delivering the letter..."
                else:
                    text = "My apples are almost sold out... Can you help me pick some more from the tree?"
                font_size = max(8, dh // 20)
                txt_font = pygame.font.SysFont(None, font_size)
                txt_surf = txt_font.render(text, True, (0, 0, 0))
                txt_x = dx + (dw - txt_surf.get_width()) // 2 - 40
                txt_y = dy + (dh - txt_surf.get_height()) // 2 + 200
                screen.blit(txt_surf, (txt_x, txt_y))
            except Exception as e:
                print(f"对话框图片或文字绘制失败: {e}")

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

        # 到达最右边，自动运行长颈鹿关卡脚本
        if character_center_x >= screen.get_width():
            import subprocess
            subprocess.Popen([
                sys.executable,
                "Zammis-Delivery/Giraffe_PANJIANI/mainGiraffe.py"
            ])
            running = False

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


def run_giraffe_level(screen):
    def detect_wave_action():
        """摄像头检测挥手动作，简单实现：检测画面中是否有大面积移动（模拟挥手）"""
        import cv2
        # 这里应返回 True/False，具体实现略
        return True
        # 蓝点对话框显示逻辑已删除
        if floor2_challenge_completed:
            # 多页对话框逻辑：
            try:
                if dialogue_page == 0:
                    dialogue_img_path = Path(__file__).parent / "assets" / "Dialogue box materials" / "Giraffe Dialogue Box1_Sleeping_New.png"
                    dialogue_img = pygame.image.load(str(dialogue_img_path)).convert_alpha()
                    dw = int(screen.get_width() * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (screen.get_width() - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
                    font_size = max(12, dh // 18)
                    txt_font = pygame.font.SysFont(None, font_size)
                    txt_surf = txt_font.render("...what's the matter?", True, (0, 0, 0))
                    txt_x = dx + (dw - txt_surf.get_width()) // 2
                    txt_y = dy + (dh - txt_surf.get_height()) // 2 + 120
                    screen.blit(txt_surf, (txt_x, txt_y))
                elif dialogue_page == 1:
                    dialogue_img_path = Path(__file__).parent / "assets" / "Dialogue box materials" / "Giraffe Dialogue Box2_Awakened_New.png"
                    dialogue_img = pygame.image.load(str(dialogue_img_path)).convert_alpha()
                    dw = int(screen.get_width() * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (screen.get_width() - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
                    font_size = max(12, dh // 18)
                    txt_font = pygame.font.SysFont(None, font_size)
                    txt_surf = txt_font.render("Oh, I’ve got a letter!", True, (0, 0, 0))
                    txt_x = dx + (dw - txt_surf.get_width()) // 2
                    txt_y = dy + (dh - txt_surf.get_height()) // 2 + 120
                    screen.blit(txt_surf, (txt_x, txt_y))
                elif dialogue_page == 2:
                    dialogue_img_path = Path(__file__).parent / "assets" / "Dialogue box materials" / "Giraffe Dialogue Box3_Happy_New.png"
                    dialogue_img = pygame.image.load(str(dialogue_img_path)).convert_alpha()
                    dw = int(screen.get_width() * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (screen.get_width() - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
                    font_size = max(12, dh // 18)
                    txt_font = pygame.font.SysFont(None, font_size)
                    txt_surf = txt_font.render("thank you!", True, (0, 0, 0))
                    txt_x = dx + (dw - txt_surf.get_width()) // 2
                    txt_y = dy + (dh - txt_surf.get_height()) // 2 + 120
                    screen.blit(txt_surf, (txt_x, txt_y))
            except Exception as e:
                print(f"长颈鹿家多页对话框绘制失败: {e}")
    # 资源路径
    FOREGROUND_FRAMES_PATTERN = "Zammis-Delivery/zammi_*.png"
    BACKGROUND_GIF_PATH = "Zammis-Delivery/Giraffe_PANJIANI/giraffe home.gif"
    VIDEO_PATH = Path("875b55be8f5a0e72b6e28c650a49a795.mp4")

    def load_png_frames(pattern: str):
        frame_files = sorted(glob.glob(pattern))
        if not frame_files:
            raise FileNotFoundError(f"找不到匹配的PNG文件: {pattern}")
        frames = []
        for frame_file in frame_files:
            surface = pygame.image.load(frame_file).convert_alpha()
            frames.append(surface)
        durations = [100] * len(frames)
        return frames, durations

    def load_gif_frames(gif_path: str, target_size=(1280, 720)):
        if not Path(gif_path).exists():
            raise FileNotFoundError(f"找不到GIF文件: {gif_path}")
        pil_img = Image.open(gif_path)
        frames = []
        durations = []
        try:
            for i in range(getattr(pil_img, "n_frames", 1)):
                pil_img.seek(i)
                frame = pil_img.convert("RGBA")
                frame = frame.resize(target_size, Image.Resampling.LANCZOS)
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                py_image = pygame.image.fromstring(data, size, mode)
                frames.append(py_image)
                duration = pil_img.info.get('duration', 100)
                durations.append(duration)
        except Exception:
            frame = pil_img.convert("RGBA")
            frame = frame.resize(target_size, Image.Resampling.LANCZOS)
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)
            durations.append(100)
        return frames, durations

    # 复用主窗口，不再新建
    bg_frames, bg_durations = load_gif_frames(BACKGROUND_GIF_PATH, target_size=screen.get_size())
    bg_current_frame = 0
    bg_frame_timer = 0
    fg_frames, fg_durations = load_png_frames(FOREGROUND_FRAMES_PATTERN)
    fg_current_frame = 0
    fg_frame_timer = 0
    bg = bg_frames[0]
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
    circle_radius = 40
    visual_radius = 10
    floor1_trigger_x = 550
    floor1_trigger_y = 585
    floor2_trigger_x = 1000
    floor2_trigger_y = 385
    # 蓝点相关变量已删除
    pygame.display.set_caption("长颈鹿关卡 | Esc 返回主场景")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    fg = fg_frames[fg_current_frame]
    center_x, center_y = 140, 495
    x = center_x - fg.get_width() // 2
    y = center_y - fg.get_height() // 2
    speed = 5
    x = int(x)
    y = int(y)
    show_box = False
    box_page = 0
    # giraffe_dialogue_manual_hide 未使用，删除
    # 动态导入 001secondfloor_pose 模块，确保 Giraffe_PANJIANI 目录在 sys.path
    import importlib
    import sys
    from pathlib import Path
    giraffe_dir = str(Path(__file__).parent / "Giraffe_PANJIANI")
    if giraffe_dir not in sys.path:
        sys.path.insert(0, giraffe_dir)
    secondfloor_pose_module = importlib.import_module('001secondfloor_pose')
    SecondFloorPoseChallenge = secondfloor_pose_module.PoseChallenge
    floor1_challenge_completed = False
    floor2_challenge_completed = False
    dialogue_page = 0
    running = True
    prev_collided = False
    prev_collided_floor2 = False
    floor1_manual_hide = False  # 新增：一楼白点弹窗主动隐藏标记
    action_challenge_popup = False  # 是否弹出动作挑战弹窗
    action_challenge_done = False  # 动作挑战完成标志，防止未定义错误
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 新增：空格关闭长颈鹿家对话框
                elif event.key == pygame.K_SPACE:
                    show_giraffe_dialogue = False
                elif event.key == pygame.K_SPACE and floor2_challenge_completed:
                    if dialogue_page < 2:
                        dialogue_page += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 左键点击长颈鹿家对话框关闭（优先处理，点击后即使还在触碰点范围也不再弹出）
                # 蓝点相关事件处理已删除
                # 新增：左键点击一楼白点弹窗关闭（优先处理，点击后即使还在触碰点范围也不再弹出）
                if event.button == 1 and show_box:
                    # 弹窗区域与主关卡一致，底部 1/3 区域
                    h = screen.get_height() // 3
                    bx = 0
                    by = screen.get_height() - h
                    bw = screen.get_width()
                    mx, my = event.pos
                    if bx <= mx <= bx + bw and by <= my <= by + h:
                        show_box = False
                        box_page = 0
                        floor1_manual_hide = True
                if event.button == 3 and floor2_challenge_completed:
                    if dialogue_page < 2:
                        dialogue_page += 1
        bg_frame_timer += clock.get_time()
        if bg_frame_timer >= bg_durations[bg_current_frame]:
            bg_frame_timer = 0
            bg_current_frame = (bg_current_frame + 1) % len(bg_frames)
            bg = bg_frames[bg_current_frame]
        keys = pygame.key.get_pressed()
        is_moving = False
        if not floor2_challenge_completed:
            # old_x 未使用，删除
            if keys[pygame.K_a]:
                x -= speed
                is_moving = True
            if keys[pygame.K_d]:
                x += speed
                is_moving = True
        if is_moving:
            fg_frame_timer += clock.get_time()
            if fg_frame_timer >= fg_durations[fg_current_frame]:
                fg_frame_timer = 0
                fg_current_frame = (fg_current_frame + 1) % len(fg_frames)
                fg = fg_frames[fg_current_frame]
        else:
            fg_current_frame = 0
            fg = fg_frames[0]
            fg_frame_timer = 0
        left_limit = -fg.get_width() // 2
        right_limit = 1280 - fg.get_width() // 2
        x = max(left_limit, min(right_limit, x))
        if x <= left_limit or x >= right_limit:
            print("长颈鹿关卡结束，返回主场景！")
            running = False
        screen.fill((50, 50, 50))
        try:
            screen.blit(bg, (0, 0))
        except Exception as e:
            pass
        screen.blit(fg, (int(x), int(y)))
        character_center_x = int(x) + fg.get_width() // 2
        character_center_y = int(y) + fg.get_height() // 2
        detect_x = character_center_x - 40
        detect_y = character_center_y + 100
        dist_x = detect_x - floor1_trigger_x
        dist_y = detect_y - floor1_trigger_y
        distance = (dist_x ** 2 + dist_y ** 2) ** 0.5
        collided = distance <= circle_radius

        # 新增：检测长颈鹿家对话框触碰点
        # 蓝点相关碰撞检测已删除
        try:
            pygame.draw.circle(screen, (255, 0, 0), (detect_x, detect_y), 4)
        except Exception:
            pass
        dbg_text = font.render(f"Floor1 dist={int(distance)} r={circle_radius} collided={collided}", True, (255, 255, 255))
        dbg_bg = pygame.Surface((dbg_text.get_width() + 8, dbg_text.get_height() + 6), pygame.SRCALPHA)
        dbg_bg.fill((0, 0, 0, 160))
        screen.blit(dbg_bg, (8, 40))
        screen.blit(dbg_text, (12, 42))
        dist_x_floor2 = detect_x - floor2_trigger_x
        dist_y_floor2 = detect_y - floor2_trigger_y
        distance_floor2 = (dist_x_floor2 ** 2 + dist_y_floor2 ** 2) ** 0.5
        collided_floor2 = distance_floor2 <= circle_radius
        dbg_text2 = font.render(f"Floor2 dist={int(distance_floor2)} r={circle_radius} collided={collided_floor2}", True, (255, 255, 255))
        dbg_bg2 = pygame.Surface((dbg_text2.get_width() + 8, dbg_text2.get_height() + 6), pygame.SRCALPHA)
        dbg_bg2.fill((0, 0, 0, 160))
        screen.blit(dbg_bg2, (8, 65))
        screen.blit(dbg_text2, (12, 67))
        # 一楼白点弹窗逻辑修复：首次进入弹窗弹出，关闭后不会自动弹出，只有离开再进入才弹出
        if collided:
            if not floor1_manual_hide:
                if not prev_collided:
                    print(f"触发：distance={distance:.1f}, circle_radius={circle_radius}, detect=({detect_x},{detect_y}), 一楼触发点=({floor1_trigger_x},{floor1_trigger_y})")
                    show_box = True
                    if not floor1_challenge_completed:
                        # 触发动作挑战
                        try:
                            from pathlib import Path
                            img1 = Path("Zammis-Delivery/assets/4poses/RaiseHighWithOneHand.png")
                            img2 = Path("Zammis-Delivery/assets/4poses/CompareHearts.png")
                            print(f"检测动作挑战图片路径: {img1}")
                            print(f"检测动作挑战图片路径: {img2}")
                            if not img1.exists():
                                print(f"❌ 图片不存在: {img1}")
                            if not img2.exists():
                                print(f"❌ 图片不存在: {img2}")
                            challenge = SecondFloorPoseChallenge(
                                target_image_path=str(img1),
                                pose_config_name="RaiseHighWithOneHand",
                                window_size=(1280, 720),
                                next_challenge={
                                    "image": str(img2),
                                    "config": "CompareHearts"
                                }
                            )
                            challenge_success = challenge.run()
                            if challenge_success:
                                print("✅ 一楼动作挑战完成！")
                                floor1_challenge_completed = True
                                center_x = 620
                                center_y = 290
                                x = center_x - fg.get_width() // 2
                                y = center_y - fg.get_height() // 2
                            else:
                                print("❌ 一楼动作挑战未完成")
                        except Exception as e:
                            print(f"一楼动作挑战错误: {e}")
                            import traceback
                            traceback.print_exc()
        else:
            show_box = False
            box_page = 0
            floor1_manual_hide = False
        prev_collided = collided
        # 修复：确保经过第二个白点时弹窗弹出，且只有挑战完成后才允许继续移动
        if collided_floor2:
            if not floor2_challenge_completed:
                if not action_challenge_popup:
                    print(f"触发二楼：distance={distance_floor2:.1f}, circle_radius={circle_radius}, detect=({detect_x},{detect_y}), 二楼触发点=({floor2_trigger_x},{floor2_trigger_y})")
                    # 动态导入 000firstfloor_pose.py 并触发动作挑战
                    try:
                        giraffe_dir = str(Path(__file__).parent / "Giraffe_PANJIANI")
                        if giraffe_dir not in sys.path:
                            sys.path.insert(0, giraffe_dir)
                        firstfloor_pose_module = importlib.import_module('000firstfloor_pose')
                        FirstFloorPoseChallenge = firstfloor_pose_module.PoseChallenge
                        img1 = Path("Zammis-Delivery/assets/4poses/strong_action.png")
                        img2 = Path("Zammis-Delivery/assets/4poses/RiseHighWithTwoHand.png")
                        print(f"检测二楼动作挑战图片路径: {img1}")
                        print(f"检测二楼动作挑战图片路径: {img2}")
                        if not img1.exists():
                            print(f"❌ 图片不存在: {img1}")
                        if not img2.exists():
                            print(f"❌ 图片不存在: {img2}")
                        challenge = FirstFloorPoseChallenge(
                            target_image_path=str(img1),
                            pose_config_name="strong_action",
                            window_size=(1280, 720),
                            next_challenge={
                                "image": str(img2),
                                "config": "RiseHighWithTwoHand"
                            }
                        )
                        challenge_success = challenge.run()
                        if challenge_success:
                            print("✅ 二楼动作挑战完成！")
                            floor2_challenge_completed = True
                        else:
                            print("❌ 二楼动作挑战未完成")
                    except Exception as e:
                        print(f"二楼动作挑战错误: {e}")
                        import traceback
                        traceback.print_exc()
                    action_challenge_popup = True
        else:
            action_challenge_popup = False
        prev_collided_floor2 = collided_floor2
        pygame.draw.circle(screen, (255, 255, 255), (floor1_trigger_x, floor1_trigger_y), visual_radius)
        pygame.draw.circle(screen, (255, 255, 255), (floor2_trigger_x, floor2_trigger_y), visual_radius)
        # 新增：长颈鹿家对话框触碰点
        # 蓝点圆圈绘制已删除

        # 动作挑战弹窗逻辑
        if action_challenge_popup and not action_challenge_done:
            # 弹窗提示
            try:
                box_w = screen.get_width()
                h = screen.get_height() // 3
                dialogue_img = pygame.image.load("Zammis-Delivery/assets/Dialogue box materials/Pig Dialogue Box1_Worried.png").convert_alpha()
                dw = int(box_w * 0.8)
                dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                dx = (box_w - dw) // 2
                dy = screen.get_height() - dh
                screen.blit(dialogue_img, (dx, dy))
                font_size = max(12, dh // 18)
                txt_font = pygame.font.SysFont(None, font_size)
                txt_surf1 = txt_font.render("动作挑战：请挥手 (Wave your hand)", True, (0, 0, 0))
                txt_x1 = dx + (dw - txt_surf1.get_width()) // 2
                txt_y1 = dy + (dh - txt_surf1.get_height()) // 2 + 120
                screen.blit(txt_surf1, (txt_x1, txt_y1))
                pygame.display.flip()
            except Exception as e:
                print(f"动作挑战弹窗绘制失败: {e}")
            # 调用摄像头动作识别
            if detect_wave_action():
                action_challenge_done = True
                floor2_challenge_completed = True
                action_challenge_popup = False
                # 恢复原有挑战成功弹窗逻辑
                try:
                    box_w = screen.get_width()
                    h = screen.get_height() // 3
                    dialogue_img = pygame.image.load("Zammis-Delivery/assets/Dialogue box materials/Pig Dialogue Box1_Worried.png").convert_alpha()
                    dw = int(box_w * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (box_w - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
                    font_size = max(12, dh // 18)
                    txt_font = pygame.font.SysFont(None, font_size)
                    txt_surf1 = txt_font.render("挑战成功！Challenge Success!", True, (0, 128, 0))
                    txt_x1 = dx + (dw - txt_surf1.get_width()) // 2
                    txt_y1 = dy + (dh - txt_surf1.get_height()) // 2 + 120
                    screen.blit(txt_surf1, (txt_x1, txt_y1))
                    pygame.display.flip()
                    pygame.time.delay(1200)
                except Exception as e:
                    print(f"挑战成功弹窗绘制失败: {e}")
            else:
                action_challenge_popup = False
                # 挑战失败弹窗
                try:
                    box_w = screen.get_width()
                    h = screen.get_height() // 3
                    dialogue_img = pygame.image.load("Zammis-Delivery/assets/Dialogue box materials/Pig Dialogue Box1_Worried.png").convert_alpha()
                    dw = int(box_w * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (box_w - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
                    font_size = max(12, dh // 18)
                    txt_font = pygame.font.SysFont(None, font_size)
                    txt_surf1 = txt_font.render("挑战失败，请重试 (Try again)", True, (200, 0, 0))
                    txt_x1 = dx + (dw - txt_surf1.get_width()) // 2
                    txt_y1 = dy + (dh - txt_surf1.get_height()) // 2 + 120
                    screen.blit(txt_surf1, (txt_x1, txt_y1))
                    pygame.display.flip()
                    pygame.time.delay(1200)
                except Exception as e:
                    print(f"挑战失败弹窗绘制失败: {e}")
        # 蓝点对话框显示逻辑已删除
        if floor2_challenge_completed:
            # 聊天框切换逻辑：点击后切换到第二个聊天框
            try:
                if dialogue_page == 0:
                    dialogue_img_path = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box1_Sleeping_New.png")
                elif dialogue_page == 1:
                    dialogue_img_path = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box2_Awakened_New.png")
                elif dialogue_page == 2:
                    dialogue_img_path = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box3_Happy_New.png")
                else:
                    dialogue_img_path = None
                dialogue_img = None
                if dialogue_img_path and dialogue_img_path.exists():
                    dialogue_img = pygame.image.load(str(dialogue_img_path)).convert_alpha()
                if dialogue_img:
                    dw = int(screen.get_width() * 0.8)
                    dh = int(dialogue_img.get_height() * (dw / dialogue_img.get_width()))
                    dialogue_img = pygame.transform.smoothscale(dialogue_img, (dw, dh))
                    dx = (screen.get_width() - dw) // 2
                    dy = screen.get_height() - dh
                    screen.blit(dialogue_img, (dx, dy))
            except Exception as e:
                print(f"Giraffe Dialogue Box 切换加载失败: {e}")
            dialogue_color = (139, 69, 19)
            font_size = 32
            txt_font = pygame.font.SysFont(None, font_size)
            if dialogue_page == 0:
                txt_surf = txt_font.render("...what's the matter?", True, dialogue_color)
                screen.blit(txt_surf, (350, 530))
            elif dialogue_page == 1:
                txt_surf = txt_font.render("Oh, I’ve got a letter!", True, dialogue_color)
                screen.blit(txt_surf, (340, 530))
            elif dialogue_page == 2:
                txt_surf = txt_font.render("thank you!", True, dialogue_color)
                screen.blit(txt_surf, (400, 530))
            else:
                txt_surf1 = txt_font.render("Thank you! You are welcome to come to my house often~", True, dialogue_color)
                txt_surf2 = txt_font.render("I'll share with you my favorite fresh grass.", True, dialogue_color)
                screen.blit(txt_surf1, (150, 510))
                screen.blit(txt_surf2, (230, 550))
        ruler_font = pygame.font.SysFont(None, 16)
        ruler_color = (255, 255, 0)
        for y_pos in range(0, screen.get_height() + 1, 50):
            line_length = 15 if y_pos % 100 == 0 else 8
            pygame.draw.line(screen, ruler_color, (0, y_pos), (line_length, y_pos), 2)
            if y_pos % 100 == 0 or y_pos in [250, 279, 300, 319, 350]:
                y_text = ruler_font.render(str(y_pos), True, ruler_color)
                screen.blit(y_text, (line_length + 2, y_pos - 8))
        for x_pos in range(0, screen.get_width() + 1, 50):
            line_length = 15 if x_pos % 100 == 0 else 8
            pygame.draw.line(screen, ruler_color, (x_pos, 0), (x_pos, line_length), 2)
            if x_pos % 100 == 0 or x_pos in [500, 550, 600]:
                x_text = ruler_font.render(str(x_pos), True, ruler_color)
                screen.blit(x_text, (x_pos - 10, line_length + 2))
        pygame.draw.line(screen, ruler_color, (0, 0), (0, screen.get_height()), 2)
        pygame.draw.line(screen, ruler_color, (0, 0), (screen.get_width(), 0), 2)
        axis_label_font = pygame.font.SysFont(None, 14)
        x_label = axis_label_font.render("X ->", True, ruler_color)
        y_label = axis_label_font.render("Y", True, ruler_color)
        y_label_down = axis_label_font.render("|", True, ruler_color)
        y_label_arrow = axis_label_font.render("v", True, ruler_color)
        screen.blit(x_label, (20, 2))
        screen.blit(y_label, (2, 20))
        screen.blit(y_label_down, (5, 30))
        screen.blit(y_label_arrow, (4, 38))
        pos_text = ruler_font.render(f"Center: ({character_center_x}, {character_center_y})", True, (255, 255, 0))
        pos_bg = pygame.Surface((pos_text.get_width() + 8, pos_text.get_height() + 4), pygame.SRCALPHA)
        pos_bg.fill((0, 0, 0, 150))
        screen.blit(pos_bg, (screen.get_width() - pos_text.get_width() - 12, screen.get_height() - 30))
        screen.blit(pos_text, (screen.get_width() - pos_text.get_width() - 8, screen.get_height() - 28))
        clamp_active = fg_current_frame < 8
        frame_status = f"Frame: {fg_current_frame}  Clamp: {'ON' if clamp_active else 'OFF'}"
        frame_text = font.render(frame_status, True, (255, 255, 255))
        frame_bg = pygame.Surface((frame_text.get_width() + 8, frame_text.get_height() + 6), pygame.SRCALPHA)
        frame_bg.fill((0, 0, 0, 140))
        fr_x = screen.get_width() - (frame_text.get_width() + 20)
        screen.blit(frame_bg, (fr_x, 8))
        screen.blit(frame_text, (fr_x + 4, 10))
        info = font.render("WASD 或 箭头 移动 — Esc 返回主场景", True, (255, 255, 255))
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
