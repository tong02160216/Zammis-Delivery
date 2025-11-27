"""
姿态识别挑战模块
使用 MediaPipe 进行姿态识别，对比玩家姿态和目标图片轮廓
"""
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from PIL import Image
from pose_configs import get_pose_landmarks, get_pose_tolerance, get_key_points


class PoseChallenge:
    def __init__(self, target_image_path, pose_config_name=None, window_size=(1280, 720), next_challenge=None):
        """
        初始化姿态挑战
        
        Args:
            target_image_path: 目标姿势图片路径（透明PNG，仅用于显示）
            pose_config_name: 姿势配置名称（从 pose_configs.py 中选择）
                            如果为 None，将尝试从文件名推断
            window_size: 窗口大小 (width, height)
            next_challenge: 下一个挑战的配置字典 {"image": 路径, "config": 配置名}
        """
        self.window_size = window_size
        self.target_image_path = target_image_path
        self.next_challenge = next_challenge
        
        # 如果未指定配置名称，从文件名推断
        if pose_config_name is None:
            filename = Path(target_image_path).stem
            self.pose_config_name = filename
        else:
            self.pose_config_name = pose_config_name
        
        # 加载容差和关键点配置
        self.tolerance = get_pose_tolerance(self.pose_config_name)
        self.key_points = get_key_points(self.pose_config_name)
        
        # 初始化 MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 自定义连接 - 只显示主要身体部位（包括头部，不包括脸部细节）
        self.body_connections = [
            # 头部到肩膀
            (0, 11),   # 鼻子 - 左肩
            (0, 12),   # 鼻子 - 右肩
            # 躯干
            (11, 12),  # 左肩 - 右肩
            (11, 23),  # 左肩 - 左臀
            (12, 24),  # 右肩 - 右臀
            (23, 24),  # 左臀 - 右臀
            # 左臂
            (11, 13),  # 左肩 - 左肘
            (13, 15),  # 左肘 - 左手腕
            # 右臂
            (12, 14),  # 右肩 - 右肘
            (14, 16),  # 右肘 - 右手腕
            # 左腿
            (23, 25),  # 左臀 - 左膝
            (25, 27),  # 左膝 - 左脚踝
            # 右腿
            (24, 26),  # 右臀 - 右膝
            (26, 28),  # 右膝 - 右脚踝
        ]
        
        # 加载目标图片
        self.target_image = self._load_target_image()
        
        # 挑战状态
        self.is_completed = False
        self.similarity_threshold = 0.50  # 相似度阈值
        self.current_similarity = 0.0
        
    def _load_target_image(self):
        """加载目标姿势图片（保持透明度）"""
        # 转换为绝对路径（相对于此脚本文件的位置）
        script_dir = Path(__file__).parent
        img_path = (script_dir / self.target_image_path).resolve()
        
        if not img_path.exists():
            raise FileNotFoundError(f"找不到目标图片: {img_path}")
        
        # 使用 PIL 加载带透明通道的图片
        pil_img = Image.open(img_path).convert("RGBA")
        
        # 调整大小以适应窗口（保持宽高比），放大到200%但不超过窗口
        max_width = self.window_size[0]  # 窗口宽度
        max_height = self.window_size[1]  # 窗口高度
        
        pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # 转换为 numpy 数组
        img_array = np.array(pil_img)
        
        # 转换 RGBA 到 BGRA (OpenCV 格式)
        img_bgra = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
        
        return img_bgra
    
    def _extract_pose_from_target(self):
        """从配置文件加载目标姿态关键点"""
        try:
            # 从 pose_configs.py 加载预定义的关键点
            target_landmarks = get_pose_landmarks(self.pose_config_name)
            return target_landmarks
        except ValueError as e:
            print(f"警告: {e}")
            print(f"可用的姿势配置: {list(get_pose_landmarks.__globals__['POSE_CONFIGS'].keys())}")
            return None
    
    def _landmarks_to_array(self, landmarks):
        """将姿态关键点转换为归一化数组"""
        points = []
        for landmark in landmarks.landmark:
            points.append([landmark.x, landmark.y, landmark.z])
        return np.array(points)
    
    def _calculate_pose_similarity(self, pose1, pose2):
        """
        计算两个姿态的相似度（基于容差的宽松匹配）
        
        Args:
            pose1: 当前姿态关键点数组 (33, 3) - 归一化坐标
            pose2: 目标姿态关键点数组 (33, 3) - 归一化坐标
        
        Returns:
            similarity: 相似度 (0-1)
        """
        if pose1 is None or pose2 is None:
            return 0.0
        
        # 只使用 X, Y 坐标
        pose1_2d = pose1[:, :2]
        pose2_2d = pose2[:, :2]
        
        # 计算容差（归一化到 0-1 范围）
        # tolerance 是像素值，需要转换为归一化坐标
        tolerance_x = self.tolerance / self.window_size[0]  # X方向容差
        tolerance_y = self.tolerance / self.window_size[1]  # Y方向容差
        
        # 头部特殊容差（如果配置了）
        head_tolerance = get_pose_tolerance(self.pose_config_name)
        try:
            from pose_configs import POSE_CONFIGS
            head_tolerance_pixels = POSE_CONFIGS[self.pose_config_name].get("head_tolerance", self.tolerance)
            wrist_tolerance_pixels = POSE_CONFIGS[self.pose_config_name].get("wrist_tolerance", self.tolerance)
        except:
            head_tolerance_pixels = self.tolerance
            wrist_tolerance_pixels = self.tolerance
        
        head_tolerance_x = head_tolerance_pixels / self.window_size[0]
        head_tolerance_y = head_tolerance_pixels / self.window_size[1]
        wrist_tolerance_x = wrist_tolerance_pixels / self.window_size[0]
        wrist_tolerance_y = wrist_tolerance_pixels / self.window_size[1]
        
        # 只关注上半身关键点
        important_indices = [0, 11, 12, 13, 14, 15, 16]
        
        # 计算每个关键点的匹配度
        matches = []
        debug_info = []  # 用于调试
        for idx in important_indices:
            # 计算距离
            diff_x = abs(pose1_2d[idx][0] - pose2_2d[idx][0])
            diff_y = abs(pose1_2d[idx][1] - pose2_2d[idx][1])
            
            # 选择容差（头部、手腕使用特殊容差）
            if idx == 0:  # 头部
                tol_x, tol_y = head_tolerance_x, head_tolerance_y
            elif idx in [15, 16]:  # 左右手腕
                tol_x, tol_y = wrist_tolerance_x, wrist_tolerance_y
            else:
                tol_x, tol_y = tolerance_x, tolerance_y
            
            # 判断是否在容差范围内
            is_match_x = diff_x <= tol_x
            is_match_y = diff_y <= tol_y
            
            # 计算该点的相似度（在容差内为1，超出则递减）
            if is_match_x and is_match_y:
                point_similarity = 1.0
            else:
                # 计算超出容差的比例，转换为相似度
                exceed_x = max(0, diff_x - tol_x) / tol_x if tol_x > 0 else 0
                exceed_y = max(0, diff_y - tol_y) / tol_y if tol_y > 0 else 0
                exceed_total = (exceed_x + exceed_y) / 2
                point_similarity = max(0, 1.0 - exceed_total)
            
            # 关键点（手腕等）权重更高
            weight = 2.0 if idx in self.key_points else 1.0
            matches.append(point_similarity * weight)
            
            # 调试信息（转换回像素显示）
            diff_x_pixels = diff_x * self.window_size[0]
            diff_y_pixels = diff_y * self.window_size[1]
            debug_info.append(f"[{idx}] dx:{diff_x_pixels:.0f} dy:{diff_y_pixels:.0f} sim:{point_similarity:.2f}")
        
        # 打印调试信息（每10帧打印一次）
        if hasattr(self, '_debug_counter'):
            self._debug_counter += 1
        else:
            self._debug_counter = 0
        
        if self._debug_counter % 10 == 0:
            print("\n=== 关键点匹配详情 ===")
            print("目标坐标 vs 当前坐标 (像素):")
            for i, idx in enumerate(important_indices):
                target_x = int(pose2_2d[idx][0] * self.window_size[0])
                target_y = int(pose2_2d[idx][1] * self.window_size[1])
                current_x = int(pose1_2d[idx][0] * self.window_size[0])
                current_y = int(pose1_2d[idx][1] * self.window_size[1])
                print(f"[{idx}] 目标:({target_x},{target_y}) 当前:({current_x},{current_y}) {debug_info[i]}")
        
        # 计算加权平均相似度
        total_weight = sum(2.0 if idx in self.key_points else 1.0 for idx in important_indices)
        similarity = sum(matches) / total_weight
        
        return similarity
    
    def _normalize_pose(self, pose):
        """归一化姿态（消除位置和缩放差异）"""
        # 计算中心点
        center = np.mean(pose, axis=0)
        
        # 平移到中心
        centered = pose - center
        
        # 缩放到单位大小
        scale = np.max(np.abs(centered))
        if scale > 0:
            normalized = centered / scale
        else:
            normalized = centered
        
        return normalized
    
    def _overlay_transparent(self, background, overlay, x, y):
        """将透明图片叠加到背景上"""
        h, w = overlay.shape[:2]
        
        # 确保不超出边界
        if x + w > background.shape[1]:
            w = background.shape[1] - x
            overlay = overlay[:, :w]
        if y + h > background.shape[0]:
            h = background.shape[0] - y
            overlay = overlay[:h, :]
        
        # 提取 alpha 通道
        alpha = overlay[:, :, 3] / 255.0
        
        # 叠加图像
        for c in range(3):
            background[y:y+h, x:x+w, c] = (
                alpha * overlay[:, :, c] +
                (1 - alpha) * background[y:y+h, x:x+w, c]
            )
        
        return background
    
    def run(self):
        """
        运行姿态挑战
        
        Returns:
            success: 挑战是否成功
        """
        # 初始化摄像头
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.window_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.window_size[1])
        
        if not cap.isOpened():
            print("无法打开摄像头")
            return False
        
        # 尝试从目标图片提取姿态（用于对比）
        target_pose = self._extract_pose_from_target()
        
        # 打印目标坐标用于调试
        if target_pose is not None:
            print("\n=== 目标姿势坐标 (归一化) ===")
            important_indices = [0, 11, 12, 13, 14, 15, 16]
            for idx in important_indices:
                x_norm, y_norm = target_pose[idx][0], target_pose[idx][1]
                x_pixel = int(x_norm * self.window_size[0])
                y_pixel = int(y_norm * self.window_size[1])
                print(f"关键点 {idx}: 归一化({x_norm:.3f}, {y_norm:.3f}) -> 像素({x_pixel}, {y_pixel})")
            print()
        
        print("姿态挑战开始！")
        print("请模仿屏幕右侧的姿势")
        # 窗口说明已在界面显示
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 调整帧大小
            frame = cv2.resize(frame, self.window_size)
            
            # 水平翻转（镜像效果）
            frame = cv2.flip(frame, 1)
            
            # 转换为 RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 检测姿态
            results = self.pose.process(frame_rgb)
            
            # 绘制姿态骨架（只显示主要身体部位）
            if results.pose_landmarks:
                # 手动绘制连接线（不包括脸部和手部细节）
                h, w = frame.shape[:2]
                for connection in self.body_connections:
                    start_idx, end_idx = connection
                    start = results.pose_landmarks.landmark[start_idx]
                    end = results.pose_landmarks.landmark[end_idx]
                    
                    # 转换为像素坐标
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    
                    # 绘制连接线
                    cv2.line(frame, start_point, end_point, (0, 255, 255), 2)
                
                # 绘制关键点（上半身关键点）
                important_indices = [0, 11, 12, 13, 14, 15, 16]
                for idx in important_indices:
                    landmark = results.pose_landmarks.landmark[idx]
                    point = (int(landmark.x * w), int(landmark.y * h))
                    cv2.circle(frame, point, 4, (0, 255, 0), -1)
                
                # 提取当前姿态
                current_pose = self._landmarks_to_array(results.pose_landmarks)
                
                # 计算相似度
                if target_pose is not None:
                    self.current_similarity = self._calculate_pose_similarity(current_pose, target_pose)
                else:
                    # 如果目标图片无法提取姿态，使用简化判断
                    self.current_similarity = 0.0
            
            # 叠加目标图片（窗口正中间，图片中心对齐窗口中心）
            target_h, target_w = self.target_image.shape[:2]
            target_x = (self.window_size[0] - target_w) // 2
            target_y = (self.window_size[1] - target_h) // 2
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            frame = self._overlay_transparent(frame, self.target_image, target_x, target_y)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # 绘制目标姿势的关键点（红色圆点）
            if target_pose is not None:
                important_indices = [0, 11, 12, 13, 14, 15, 16]
                for idx in important_indices:
                    if idx < len(target_pose):
                        # 目标姿势已经是归一化坐标
                        x_norm, y_norm = target_pose[idx][0], target_pose[idx][1]
                        if x_norm > 0 and y_norm > 0:  # 只绘制有效的点
                            # 转换为像素坐标
                            x_pixel = int(x_norm * self.window_size[0])
                            y_pixel = int(y_norm * self.window_size[1])
                            # 绘制红色圆点（较大，便于观察）
                            cv2.circle(frame, (x_pixel, y_pixel), 8, (0, 0, 255), -1)
                            # 绘制白色外圈
                            cv2.circle(frame, (x_pixel, y_pixel), 8, (255, 255, 255), 2)
                            # 添加关键点编号和坐标信息
                            cv2.putText(frame, f"{idx}({x_pixel},{y_pixel})", (x_pixel + 10, y_pixel - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # 绘制目标姿势的骨骼连接（红色线条）
                for connection in self.body_connections:
                    start_idx, end_idx = connection
                    if start_idx < len(target_pose) and end_idx < len(target_pose):
                        start_x, start_y = target_pose[start_idx][0], target_pose[start_idx][1]
                        end_x, end_y = target_pose[end_idx][0], target_pose[end_idx][1]
                        if start_x > 0 and start_y > 0 and end_x > 0 and end_y > 0:
                            start_point = (int(start_x * self.window_size[0]), int(start_y * self.window_size[1]))
                            end_point = (int(end_x * self.window_size[0]), int(end_y * self.window_size[1]))
                            cv2.line(frame, start_point, end_point, (0, 0, 255), 2)
            
            # 绘制坐标标尺（白色）
            h, w = frame.shape[:2]
            ruler_color = (255, 255, 255)
            
            # 左侧 Y 轴标尺（每50像素一个刻度）
            for y_pos in range(0, h + 1, 50):
                line_length = 15 if y_pos % 100 == 0 else 8
                cv2.line(frame, (0, y_pos), (line_length, y_pos), ruler_color, 2)
                if y_pos % 100 == 0:
                    cv2.putText(frame, str(y_pos), (line_length + 2, y_pos + 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, ruler_color, 1)
            
            # 顶部 X 轴标尺（每50像素一个刻度）
            for x_pos in range(0, w + 1, 50):
                line_length = 15 if x_pos % 100 == 0 else 8
                cv2.line(frame, (x_pos, 0), (x_pos, line_length), ruler_color, 2)
                if x_pos % 100 == 0:
                    cv2.putText(frame, str(x_pos), (x_pos - 10, line_length + 12), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, ruler_color, 1)
            
            # 绘制坐标轴线
            cv2.line(frame, (0, 0), (0, h), ruler_color, 2)  # Y轴
            cv2.line(frame, (0, 0), (w, 0), ruler_color, 2)  # X轴
            
            # 显示相似度
            similarity_text = f"Similarity: {self.current_similarity:.1%}"
            cv2.putText(frame, similarity_text, (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            
            # 显示需要达到的阈值
            threshold_text = f"Need: {self.similarity_threshold:.1%}"
            cv2.putText(frame, threshold_text, (20, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # 显示提示
            instruction_text = "Match the pose!"
            cv2.putText(frame, instruction_text, (20, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # 显示进度条
            bar_width = 400
            bar_height = 30
            bar_x = 20
            bar_y = self.window_size[1] - 60
            
            # 背景
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (50, 50, 50), -1)
            
            # 进度
            progress_width = int(bar_width * self.current_similarity)
            color = (0, 255, 0) if self.current_similarity >= self.similarity_threshold else (0, 165, 255)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), 
                         color, -1)
            
            # 阈值线
            threshold_x = bar_x + int(bar_width * self.similarity_threshold)
            cv2.line(frame, (threshold_x, bar_y), (threshold_x, bar_y + bar_height), 
                    (255, 255, 255), 2)
            
            # 检查是否完成
            if self.current_similarity >= self.similarity_threshold:
                self.is_completed = True
                
                # 在窗口中央显示SUCCESS
                success_text = "SUCCESS!"
                text_size = cv2.getTextSize(success_text, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 6)[0]
                text_x = (self.window_size[0] - text_size[0]) // 2
                text_y = (self.window_size[1] + text_size[1]) // 2
                
                # 绘制文字背景
                padding = 30
                cv2.rectangle(frame, 
                            (text_x - padding, text_y - text_size[1] - padding),
                            (text_x + text_size[0] + padding, text_y + padding),
                            (0, 200, 0), -1)
                cv2.rectangle(frame, 
                            (text_x - padding, text_y - text_size[1] - padding),
                            (text_x + text_size[0] + padding, text_y + padding),
                            (255, 255, 255), 3)
                
                # 绘制SUCCESS文字
                cv2.putText(frame, success_text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 255), 6)
                
                # 显示画面
                cv2.imshow('Pose Challenge', frame)
                cv2.waitKey(1500)  # 显示1.5秒
                
                # 如果有下一个挑战，切换到下一个动作
                if self.next_challenge:
                    # 重置完成状态
                    self.is_completed = False
                    self.current_similarity = 0.0
                    
                    # 切换到下一个挑战的配置
                    self.target_image_path = self.next_challenge["image"]
                    self.pose_config_name = self.next_challenge["config"]
                    
                    # 重新加载目标图片和姿势配置
                    self.target_image = self._load_target_image()
                    self.tolerance = get_pose_tolerance(self.pose_config_name)
                    self.key_points = get_key_points(self.pose_config_name)
                    
                    # 动作二使用更低的阈值
                    self.similarity_threshold = 0.25  # 动作二阈值设为25%
                    target_pose = self._extract_pose_from_target()
                    
                    # 清空下一个挑战（避免无限循环）
                    self.next_challenge = None
                    
                    # 打印新目标坐标
                    if target_pose is not None:
                        print("\n=== 切换到动作二 ===")
                        print("=== 目标姿势坐标 (归一化) ===")
                        important_indices = [0, 11, 12, 13, 14, 15, 16]
                        for idx in important_indices:
                            x_norm, y_norm = target_pose[idx][0], target_pose[idx][1]
                            x_pixel = int(x_norm * self.window_size[0])
                            y_pixel = int(y_norm * self.window_size[1])
                            print(f"关键点 {idx}: 归一化({x_norm:.3f}, {y_norm:.3f}) -> 像素({x_pixel}, {y_pixel})")
                        print()
                    
                    # 继续循环，不关闭窗口
                    continue
                else:
                    # 最后一个挑战完成
                    break
            
            # 显示画面
            cv2.imshow('Pose Challenge', frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            
            # 检查窗口是否被关闭
            if cv2.getWindowProperty('Pose Challenge', cv2.WND_PROP_VISIBLE) < 1:
                # 窗口被关闭，退出挑战
                self.is_completed = False
                break
        
        # 清理资源
        cap.release()
        cv2.destroyAllWindows()
        self.pose.close()
        
        return self.is_completed


def test_pose_challenge():
    """测试姿态挑战 - 两个连续动作"""
    # 配置两个动作的挑战
    challenge = PoseChallenge(
        target_image_path="../assets/4poses/strong_action.png",
        pose_config_name="strong_action",
        window_size=(1280, 720),
        next_challenge={
            "image": "../assets/4poses/RiseHighWithTwoHand.png",
            "config": "RiseHighWithTwoHand"
        }
    )
    
    success = challenge.run()
    
    if success:
        print("挑战成功！")
    else:
        print("挑战未完成")
    
    return success


if __name__ == "__main__":
    test_pose_challenge()
