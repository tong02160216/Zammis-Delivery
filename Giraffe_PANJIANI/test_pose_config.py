"""
测试姿势配置工具
用于可视化和调整姿势关键点坐标（像素坐标系统）
"""
import cv2
import numpy as np
from PIL import Image
from pose_configs import get_pose_landmarks, POSE_CONFIGS, WINDOW_WIDTH, WINDOW_HEIGHT

# 自定义身体连接（与 firstfloor_pose.py 保持一致）
BODY_CONNECTIONS = [
    (0, 11), (0, 12),           # 头部到肩膀
    (11, 12),                    # 肩膀连接
    (11, 23), (12, 24), (23, 24), # 躯干
    (11, 13), (13, 15),          # 左臂
    (12, 14), (14, 16),          # 右臂
    (23, 25), (25, 27),          # 左腿
    (24, 26), (26, 28),          # 右腿
]

def visualize_pose(pose_name, image_path=None, window_size=(1280, 720)):
    """
    可视化姿势配置
    
    Args:
        pose_name: 姿势配置名称
        image_path: 可选的背景图片路径
        window_size: 窗口大小
    """
    print(f"\n正在可视化姿势: {pose_name}")
    
    # 获取姿势关键点
    try:
        landmarks = get_pose_landmarks(pose_name)
    except ValueError as e:
        print(f"错误: {e}")
        print(f"可用的姿势: {list(POSE_CONFIGS.keys())}")
        return
    
    # 创建画布
    if image_path:
        # 加载背景图片
        pil_img = Image.open(image_path)
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        max_width, max_height = window_size
        pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        img_array = np.array(pil_img)
        canvas = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        
        # 如果图片小于窗口，居中放置
        if canvas.shape[0] < window_size[1] or canvas.shape[1] < window_size[0]:
            temp_canvas = np.zeros((window_size[1], window_size[0], 3), dtype=np.uint8)
            y_offset = (window_size[1] - canvas.shape[0]) // 2
            x_offset = (window_size[0] - canvas.shape[1]) // 2
            temp_canvas[y_offset:y_offset+canvas.shape[0], x_offset:x_offset+canvas.shape[1]] = canvas
            canvas = temp_canvas
    else:
        # 黑色背景
        canvas = np.zeros((window_size[1], window_size[0], 3), dtype=np.uint8)
    
    # 绘制网格（每100像素）
    grid_color = (50, 50, 50)
    for y in range(0, window_size[1], 100):
        cv2.line(canvas, (0, y), (window_size[0], y), grid_color, 1)
    for x in range(0, window_size[0], 100):
        cv2.line(canvas, (x, 0), (x, window_size[1]), grid_color, 1)
    
    # 绘制骨骼连接
    for connection in BODY_CONNECTIONS:
        start_idx, end_idx = connection
        start_coords = POSE_CONFIGS[pose_name]['landmarks'].get(start_idx, [0, 0])
        end_coords = POSE_CONFIGS[pose_name]['landmarks'].get(end_idx, [0, 0])
        
        start_x, start_y = start_coords[0], start_coords[1]
        end_x, end_y = end_coords[0], end_coords[1]
        
        if start_x > 0 and start_y > 0 and end_x > 0 and end_y > 0:
            start_point = (int(start_x), int(start_y))
            end_point = (int(end_x), int(end_y))
            cv2.line(canvas, start_point, end_point, (0, 255, 0), 3)
    
    # 绘制关键点
    important_indices = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for idx in important_indices:
        coords = POSE_CONFIGS[pose_name]['landmarks'].get(idx, [0, 0])
        x_pixel, y_pixel = coords[0], coords[1]
        if x_pixel > 0 and y_pixel > 0:
            x_pixel = int(x_pixel)
            y_pixel = int(y_pixel)
            
            # 绘制圆点
            cv2.circle(canvas, (x_pixel, y_pixel), 10, (0, 0, 255), -1)
            cv2.circle(canvas, (x_pixel, y_pixel), 10, (255, 255, 255), 2)
            
            # 绘制编号
            cv2.putText(canvas, str(idx), (x_pixel + 15, y_pixel - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 绘制坐标（像素坐标）
            coord_text = f"({x_pixel}, {y_pixel})"
            cv2.putText(canvas, coord_text, (x_pixel + 15, y_pixel + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # 显示标尺
    ruler_color = (255, 255, 255)
    for y in range(0, window_size[1] + 1, 100):
        cv2.line(canvas, (0, y), (20, y), ruler_color, 2)
        cv2.putText(canvas, str(y), (25, y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, ruler_color, 1)
    
    for x in range(0, window_size[0] + 1, 100):
        cv2.line(canvas, (x, 0), (x, 20), ruler_color, 2)
        cv2.putText(canvas, str(x), (x - 10, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, ruler_color, 1)
    
    # 显示关键点索引说明
    info_text = [
        f"Pose: {POSE_CONFIGS[pose_name]['name']}",
        f"Description: {POSE_CONFIGS[pose_name]['description']}",
        "",
        "Key Points:",
        "0=Head, 11/12=Shoulders",
        "13/14=Elbows, 15/16=Wrists",
        "23/24=Hips, 25/26=Knees, 27/28=Ankles",
        "",
        "Press ESC to exit"
    ]
    
    y_offset = 50
    for line in info_text:
        cv2.putText(canvas, line, (window_size[0] - 400, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 25
    
    # 显示窗口
    window_name = f"Pose Config: {pose_name}"
    cv2.imshow(window_name, canvas)
    
    print(f"\n姿势信息:")
    print(f"  名称: {POSE_CONFIGS[pose_name]['name']}")
    print(f"  描述: {POSE_CONFIGS[pose_name]['description']}")
    print(f"  关键点数量: {len(POSE_CONFIGS[pose_name]['landmarks'])}")
    print(f"\n关键点坐标（像素坐标）:")
    for idx in important_indices:
        pixel_coords = POSE_CONFIGS[pose_name]['landmarks'].get(idx, [0, 0])
        x_pixel, y_pixel = pixel_coords[0], pixel_coords[1]
        print(f"  点 {idx:2d}: X={x_pixel:4d}, Y={y_pixel:3d}")
    
    print(f"\n窗口已打开，按 ESC 退出...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # 测试所有姿势配置
    print("可用的姿势配置:")
    for i, pose_name in enumerate(POSE_CONFIGS.keys(), 1):
        print(f"{i}. {pose_name}: {POSE_CONFIGS[pose_name]['name']}")
    
    print("\n" + "="*60)
    
    # 可视化每个姿势
    for pose_name in POSE_CONFIGS.keys():
        # 尝试加载对应的图片
        image_path = f"../assets/4poses/{pose_name}.png"
        visualize_pose(pose_name, image_path)
