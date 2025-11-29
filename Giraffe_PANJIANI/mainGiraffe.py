import pygame
import cv2
import sys
from pathlib import Path
from PIL import Image
import glob
from importlib import import_module
import numpy as np


def draw_pixel_text(surface, text, position, color, pixel_size=3, font_scale=1.0):
    """
    在 Pygame Surface 上绘制像素风格的文字（使用小方块）
    
    Args:
        surface: Pygame Surface
        text: 要显示的文字
        position: (x, y) 左上角位置
        color: RGB颜色元组
        pixel_size: 每个像素块的大小
        font_scale: 字体缩放
    """
    # 创建临时 numpy 图像
    scale_factor = 3
    temp_width = int(len(text) * 50 * font_scale * scale_factor)
    temp_height = int(50 * font_scale * scale_factor)
    temp_img = np.zeros((temp_height, temp_width), dtype=np.uint8)
    
    # 在临时图像上绘制文字
    cv2.putText(temp_img, text, (5, int(35 * font_scale * scale_factor)), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale * scale_factor, 255, 
                int(2 * scale_factor))
    
    # 下采样到像素块大小
    x, y = position
    step = pixel_size
    
    for i in range(0, temp_img.shape[0], step * scale_factor):
        for j in range(0, temp_img.shape[1], step * scale_factor):
            # 采样区域的平均值
            sample_region = temp_img[i:i+step*scale_factor, j:j+step*scale_factor]
            if sample_region.size > 0 and np.mean(sample_region) > 128:
                # 绘制像素块
                block_y = y + i // scale_factor
                block_x = x + j // scale_factor
                if block_y < surface.get_height() - step and block_x < surface.get_width() - step:
                    pygame.draw.rect(surface, color, 
                                   (block_x, block_y, step, step))

# 动态导入 000firstfloor_pose 模块
firstfloor_pose_module = import_module('000firstfloor_pose')
FirstFloorPoseChallenge = firstfloor_pose_module.PoseChallenge

# 动态导入 001secondfloor_pose 模块
secondfloor_pose_module = import_module('001secondfloor_pose')
SecondFloorPoseChallenge = secondfloor_pose_module.PoseChallenge


# 前景与背景图片的路径（确保 GIF 路径为当前脚本同目录下）
FOREGROUND_FRAMES_PATTERN = str(Path(__file__).parent.parent / "zammi_*.png")
BACKGROUND_GIF_PATH = str(Path(__file__).parent / "giraffe home.gif")
VIDEO_PATH = Path(r"875b55be8f5a0e72b6e28c650a49a795.mp4")


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
    
    # 重新排序：将 zammi_0005.png 作为第一帧
    # 新顺序：0005, 0006, 0007, ..., 0016, 0001, 0002, 0003, 0004
    reordered_files = []
    frame_0005 = None
    other_frames = []
    
    for frame_file in frame_files:
        if 'zammi_0005.png' in frame_file:
            frame_0005 = frame_file
        else:
            other_frames.append(frame_file)
    
    # 如果找到了 zammi_0005.png，将它放在最前面
    if frame_0005:
        reordered_files.append(frame_0005)
        # 添加 0006-0016
        for f in other_frames:
            if 'zammi_0006.png' <= f.split('\\')[-1] <= 'zammi_0016.png':
                reordered_files.append(f)
        # 添加 0001-0004
        for f in other_frames:
            if 'zammi_0001.png' <= f.split('\\')[-1] <= 'zammi_0004.png':
                reordered_files.append(f)
    else:
        reordered_files = frame_files
    
    frames = []
    print(f"正在加载 {len(reordered_files)} 个PNG帧...")
    print(f"帧顺序: {[f.split('\\')[-1] for f in reordered_files[:5]]}...")
    
    for frame_file in reordered_files:
        surface = pygame.image.load(frame_file).convert_alpha()
        frames.append(surface)
    
    # 所有帧使用相同的持续时间（100毫秒）
    durations = [100] * len(frames)
    
    return frames, durations


def load_gif_frames(gif_path: str, target_size=(1280, 720)):
    """加载 GIF 文件的所有帧并缩放到目标尺寸"""
    if not Path(gif_path).exists():
        raise FileNotFoundError(f"找不到GIF文件: {gif_path}")
    
    pil_img = Image.open(gif_path)
    frames = []
    durations = []
    
    try:
        for i in range(getattr(pil_img, "n_frames", 1)):
            pil_img.seek(i)
            frame = pil_img.convert("RGBA")
            # 缩放到目标尺寸
            frame = frame.resize(target_size, Image.Resampling.LANCZOS)
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)
            # 获取帧持续时间（毫秒），默认 100ms
            duration = pil_img.info.get('duration', 100)
            durations.append(duration)
    except Exception as e:
        # 如果只有单帧或读取失败，至少返回第一帧
        frame = pil_img.convert("RGBA")
        # 缩放到目标尺寸
        frame = frame.resize(target_size, Image.Resampling.LANCZOS)
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        frames.append(py_image)
        durations.append(100)
    
    print(f"正在加载 GIF：{len(frames)} 帧，缩放至 {target_size[0]}×{target_size[1]}")
    return frames, durations


def main():
    # 设置窗口在屏幕中心显示
    import os
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    pygame.init()

    # 先创建临时窗口以便加载帧
    temp_screen = pygame.display.set_mode((100, 100))
    
    # 加载背景 GIF 动画
    bg_frames, bg_durations = load_gif_frames(BACKGROUND_GIF_PATH)
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

    # 一楿触发点参数
    circle_radius = 40  # 触发判定半径（检测用，较宽松）
    visual_radius = 10  # 白色圆点的视觉半径（较小）
    floor1_trigger_x = 550  # 一楿触发点 X 坐标
    floor1_trigger_y = 585  # 一楿触发点 Y 坐标（590-5）

    # 二楼触发点参数
    floor2_trigger_x = 1000  # 二楼触发点 X 坐标
    floor2_trigger_y = 385   # 二楼触发点 Y 坐标（390-5）

    # 窗口大小固定为 1280×720（与邮局图片相同）
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("WASD 控制 — Esc 退出 | GIF 动画")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    # 初始位置：zamimi 中心点在显示坐标 (140, 495)
    # 红色检测点在中心点左侧40像素、下方100像素处，即 (100, 595)
    fg = fg_frames[fg_current_frame]
    center_x, center_y = 140, 495
    
    # 计算左上角坐标（blit 使用左上角坐标）
    x = center_x - fg.get_width() // 2
    y = center_y - fg.get_height() // 2
    
    print(f"Zamimi初始位置: 中心点({center_x},{center_y}) -> 左上角({x},{y}), 尺寸({fg.get_width()}x{fg.get_height()})")

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
    
    # 姿态挑战状态标志
    floor1_challenge_completed = False  # 一楼挑战是否已完成
    floor2_challenge_completed = False  # 二楼挑战是否已完成
    
    # 加载对话框图片（二楼挑战完成后显示）
    dialogue_box_img1 = None  # 睡觉状态
    dialogue_box_img2 = None  # 醒来状态
    dialogue_box_img3 = None  # 高兴状态
    dialogue_page = 0  # 0: 第一页(Sleeping), 1: 第二页(Awakened), 2: 第三页(Happy)
    
    try:
        dialogue_box_path1 = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box1_Sleeping_New.png")
        if dialogue_box_path1.exists():
            dialogue_box_img1 = pygame.image.load(str(dialogue_box_path1)).convert_alpha()
            print(f"✅ 已加载对话框图片1: {dialogue_box_img1.get_size()}")
        else:
            print(f"❌ 找不到对话框图片1: {dialogue_box_path1}")
        dialogue_box_path2 = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box2_Awakened_New.png")
        if dialogue_box_path2.exists():
            dialogue_box_img2 = pygame.image.load(str(dialogue_box_path2)).convert_alpha()
            print(f"✅ 已加载对话框图片2: {dialogue_box_img2.get_size()}")
        else:
            print(f"❌ 找不到对话框图片2: {dialogue_box_path2}")
        dialogue_box_path3 = Path("Zammis-Delivery/assets/Dialogue box materials/Giraffe Dialogue Box3_Happy_New.png")
        if dialogue_box_path3.exists():
            dialogue_box_img3 = pygame.image.load(str(dialogue_box_path3)).convert_alpha()
            print(f"✅ 已加载对话框图片3: {dialogue_box_img3.get_size()}")
        else:
            print(f"❌ 找不到对话框图片3: {dialogue_box_path3}")
    except Exception as e:
        print(f"❌ 加载对话框图片失败: {e}")

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
    prev_collided_floor2 = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 空格键切换对话框
                elif event.key == pygame.K_SPACE and floor2_challenge_completed:
                    if dialogue_page < 2:
                        dialogue_page += 1
                        print(f"切换到对话框第{dialogue_page + 1}页")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标右键点击也可以切换对话框
                if event.button == 3 and floor2_challenge_completed:  # 3 = 右键
                    if dialogue_page < 2:
                        dialogue_page += 1
                        print(f"切换到对话框第{dialogue_page + 1}页")
                # 鼠标左键点击时，如果文字框可见并且点击在框内，则翻页或播放视频
                elif event.button == 1 and show_box:
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
        
        keys = pygame.key.get_pressed()
        
        # 检测是否正在移动
        is_moving = False
        
        # 只有在二楼挑战未完成时才允许移动
        if not floor2_challenge_completed:
            # A/D 左右移动 - 调试所有按键
            if any(keys):  # 如果有任何按键被按下
                pressed_keys = [i for i, key in enumerate(keys) if key]
                if len(pressed_keys) > 0 and len(pressed_keys) < 10:  # 避免输出过多
                    print(f"检测到按键: {pressed_keys[:5]}")
            
            old_x = x
            # pygame.K_a 是 97, pygame.K_d 是 100
            if keys[pygame.K_a]:
                x -= speed
                is_moving = True
                print(f"按下A键(97): x从{old_x}变为{x}")
            if keys[pygame.K_d]:
                x += speed
                is_moving = True
                print(f"按下D键(100): x从{old_x}变为{x}")
        
        # 更新前景动画帧 - 只有在移动时才播放动画
        if is_moving:
            fg_frame_timer += clock.get_time()
            if fg_frame_timer >= fg_durations[fg_current_frame]:
                fg_frame_timer = 0
                fg_current_frame = (fg_current_frame + 1) % len(fg_frames)
                fg = fg_frames[fg_current_frame]
        else:
            # 静止时显示第一帧（站立姿势）
            fg_current_frame = 0
            fg = fg_frames[0]
            fg_frame_timer = 0

        # X轴边界限制：角色中心点在0到1280范围内移动
        left_limit = -fg.get_width() // 2
        right_limit = 1280 - fg.get_width() // 2
        x = max(left_limit, min(right_limit, x))

        # 检查角色是否走出画面并触发事件
        if x <= left_limit:
            print("角色已离开画面左侧！可以触发自定义事件。")
            # TODO: 在此处添加你需要的触发逻辑（如切换场景、弹窗等）
        elif x >= right_limit:
            print("角色已离开画面右侧！可以触发自定义事件。")
            # TODO: 在此处添加你需要的触发逻辑（如切换场景、弹窗等）

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
        
        # 中心点标记已隐藏（透明度0%）
        # cross_size = 10
        # overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        # cyan_color = (0, 255, 255, 0)  # 0%透明度（完全透明/不可见）
        # pygame.draw.line(overlay, cyan_color, ...)
        # screen.blit(overlay, (0, 0))
        
        # 检测点偏移：向左40像素，向下100像素（与main.py相同）
        detect_x = character_center_x - 40
        detect_y = character_center_y + 100

        # 计算检测点与一楼触发点的距离
        dist_x = detect_x - floor1_trigger_x
        dist_y = detect_y - floor1_trigger_y
        distance = (dist_x ** 2 + dist_y ** 2) ** 0.5

        # 实际触发仅在玩家检测点触碰白点时发生
        collided = distance <= circle_radius

        # 调试：在角色中心画小红点，显示距离与状态文本
        try:
            pygame.draw.circle(screen, (255, 0, 0), (detect_x, detect_y), 4)
        except Exception:
            pass

        dbg_text = font.render(f"Floor1 dist={int(distance)} r={circle_radius} collided={collided}", True, (255, 255, 255))
        dbg_bg = pygame.Surface((dbg_text.get_width() + 8, dbg_text.get_height() + 6), pygame.SRCALPHA)
        dbg_bg.fill((0, 0, 0, 160))
        screen.blit(dbg_bg, (8, 40))
        screen.blit(dbg_text, (12, 42))
        
        # 二楼触发点距离调试信息
        dist_x_floor2 = detect_x - floor2_trigger_x
        dist_y_floor2 = detect_y - floor2_trigger_y
        distance_floor2 = (dist_x_floor2 ** 2 + dist_y_floor2 ** 2) ** 0.5
        collided_floor2 = distance_floor2 <= circle_radius
        
        dbg_text2 = font.render(f"Floor2 dist={int(distance_floor2)} r={circle_radius} collided={collided_floor2}", True, (255, 255, 255))
        dbg_bg2 = pygame.Surface((dbg_text2.get_width() + 8, dbg_text2.get_height() + 6), pygame.SRCALPHA)
        dbg_bg2.fill((0, 0, 0, 160))
        screen.blit(dbg_bg2, (8, 65))
        screen.blit(dbg_text2, (12, 67))

        # 在首次碰撞时在控制台打印一条记录，便于确认触发
        if collided and not prev_collided:
            print(f"触发：distance={distance:.1f}, circle_radius={circle_radius}, detect=({detect_x},{detect_y}), 一楼触发点=({floor1_trigger_x},{floor1_trigger_y})")
            
            # 触发一楼姿态挑战（仅触发一次）
            if not floor1_challenge_completed:
                print("\n=== 启动姿态挑战 ===")
                # 暂停 pygame 以运行挑战
                pygame.event.clear()
                
                try:
                    challenge = FirstFloorPoseChallenge(
                        target_image_path="../assets/4poses/strong_action.png",
                        pose_config_name="strong_action",
                        window_size=(1280, 720),
                        next_challenge={
                            "image": "../assets/4poses/RiseHighWithTwoHand.png",
                            "config": "RiseHighWithTwoHand"
                        }
                    )
                    challenge_success = challenge.run()
                    
                    if challenge_success:
                        print("✅ 姿态挑战完成！")
                        floor1_challenge_completed = True
                        
                        # 传送到二楼位置 - 红点(detect点)在 (580, 390)
                        # detect_x = center_x - 40, detect_y = center_y + 100
                        # 所以 center_x = 620, center_y = 290
                        center_x = 620
                        center_y = 290
                        x = center_x - fg.get_width() // 2
                        y = center_y - fg.get_height() // 2
                        print(f"传送到二楼: 角色中心({center_x},{center_y}), 红点检测位置({center_x-40},{center_y+100})")
                    else:
                        print("❌ 姿态挑战未完成")
                except Exception as e:
                    print(f"姿态挑战错误: {e}")
                    import traceback
                    traceback.print_exc()
                
                print("=== 返回游戏 ===\n")
                # 重新激活 pygame 窗口
                pygame.display.set_mode((1280, 720))
                pygame.display.set_caption("WASD 控制 — Esc 退出 | GIF 动画")
                
        prev_collided = collided
        
        # 在首次碰撞二楼触发点时触发挑战（仅触发一次）
        if collided_floor2 and not prev_collided_floor2:
            print(f"触发二楼：distance={distance_floor2:.1f}, circle_radius={circle_radius}, detect=({detect_x},{detect_y}), 二楼触发点=({floor2_trigger_x},{floor2_trigger_y})")
            # 触发二楼姿态挑战（仅触发一次）
            if not floor2_challenge_completed:
                print("\n=== 启动二楼姿态挑战 ===")
                pygame.event.clear()
                try:
                    challenge = SecondFloorPoseChallenge(
                        target_image_path="../assets/4poses/RaiseHighWithOneHand.png",
                        pose_config_name="RaiseHighWithOneHand",
                        window_size=(1280, 720),
                        next_challenge={
                            "image": "../assets/4poses/CompareHearts.png",
                            "config": "CompareHearts"
                        }
                    )
                    challenge_success = challenge.run()
                    if challenge_success:
                        print("✅ 二楼姿态挑战完成！")
                        floor2_challenge_completed = True
                        dialogue_page = 0  # 立即显示第一页对话框
                    else:
                        print("❌ 二楼姿态挑战未完成")
                except Exception as e:
                    print(f"二楼姿态挑战错误: {e}")
                    import traceback
                    traceback.print_exc()
                print("=== 返回游戏 ===\n")
                pygame.display.set_mode((1280, 720))
                pygame.display.set_caption("WASD 控制 — Esc 退出 | GIF 动画")
        
        prev_collided_floor2 = collided_floor2
        
        # 绘制一楿触发点标记（白色实心圆，较小的视觉半径）
        pygame.draw.circle(screen, (255, 255, 255), (floor1_trigger_x, floor1_trigger_y), visual_radius)
        
        # 绘制二楿触发点标记（白色实心圆）
        pygame.draw.circle(screen, (255, 255, 255), (floor2_trigger_x, floor2_trigger_y), visual_radius)
        # 不再绘制白点周围的额外可视化圈（按要求）
        
        # 如果二楼挑战已完成，显示对话框
        if floor2_challenge_completed:
            # 根据页面选择显示哪个对话框
            if dialogue_page == 0:
                current_dialogue_img = dialogue_box_img1
            elif dialogue_page == 1:
                current_dialogue_img = dialogue_box_img2
            else:
                current_dialogue_img = dialogue_box_img3
            
            if current_dialogue_img:
                # 对话框底部对齐窗口底部
                dialogue_x = 0
                dialogue_y = screen.get_height() - current_dialogue_img.get_height()
                screen.blit(current_dialogue_img, (dialogue_x, dialogue_y))
                
                # 根据页面显示不同的文字（使用像素风格）
                dialogue_color = (139, 69, 19)  # 棕色
                if dialogue_page == 0:
                    # "......what's the matter?" 中心点在 (600, 550)
                    draw_pixel_text(screen, "......what's the matter?", (350, 530), dialogue_color, pixel_size=2, font_scale=0.9)
                elif dialogue_page == 1:
                    # "Oh my god! It's my letter!" 中心点在 (600, 550)
                    draw_pixel_text(screen, "Oh my god! It's my letter!", (340, 530), dialogue_color, pixel_size=2, font_scale=0.9)
                else:
                    # 第三页文字较长，需要分两行显示
                    # 第一行: "Thank you! You are welcome to come to my house often~"
                    draw_pixel_text(screen, "Thank you! You are welcome to come to my house often~", (150, 510), dialogue_color, pixel_size=2, font_scale=0.9)
                    # 第二行: "I'll share with you my favorite fresh grass."
                    draw_pixel_text(screen, "I'll share with you my favorite fresh grass.", (230, 550), dialogue_color, pixel_size=2, font_scale=0.9)

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
