"""
手动调整姿势关键点坐标的可视化工具
显示图片，让你可以看到当前设置的关键点位置
"""
import cv2
import numpy as np
from PIL import Image

# 窗口尺寸
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# 容差范围（像素）
TOLERANCE = 65
HEAD_TOLERANCE = 100  # 头部特殊容差
WRIST_TOLERANCE = 60  # 手腕特殊容差

# 当前 strong_action 的关键点配置（像素坐标）
# 你可以直接修改这些数值，然后重新运行程序查看效果
LANDMARKS = {
    0:  [700, 280],    # 头部（鼻子）
    11: [560, 410],    # 左肩
    12: [800, 410],    # 右肩
    13: [480, 250],    # 左肘（举高）
    14: [930, 250],    # 右肘（举高）
    15: [670, 150],    # 左手腕（举高）
    16: [705, 150],    # 右手腕（举高）
}

# 骨骼连接
BODY_CONNECTIONS = [
    (0, 11), (0, 12),           # 头部到肩膀
    (11, 12),                    # 肩膀连接
    (11, 13), (13, 15),          # 左臂
    (12, 14), (14, 16),          # 右臂
]

def main():
    # 加载图片
    image_path = "../assets/4poses/CompareHearts.png"
    pil_img = Image.open(image_path)
    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')
    
    # 缩放到窗口大小
    pil_img.thumbnail((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
    img_array = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    
    # 创建画布（黑色背景）
    canvas = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
    
    # 居中放置图片
    img_h, img_w = img_bgr.shape[:2]
    y_offset = (WINDOW_HEIGHT - img_h) // 2
    x_offset = (WINDOW_WIDTH - img_w) // 2
    canvas[y_offset:y_offset+img_h, x_offset:x_offset+img_w] = img_bgr
    
    # 绘制网格（每100像素）
    grid_color = (50, 50, 50)
    for y in range(0, WINDOW_HEIGHT, 100):
        cv2.line(canvas, (0, y), (WINDOW_WIDTH, y), grid_color, 1)
        cv2.putText(canvas, str(y), (5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
    
    for x in range(0, WINDOW_WIDTH, 100):
        cv2.line(canvas, (x, 0), (x, WINDOW_HEIGHT), grid_color, 1)
        cv2.putText(canvas, str(x), (x+5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
    
    # 绘制骨骼连接（红色）
    for connection in BODY_CONNECTIONS:
        start_idx, end_idx = connection
        if start_idx in LANDMARKS and end_idx in LANDMARKS:
            start_x, start_y = LANDMARKS[start_idx]
            end_x, end_y = LANDMARKS[end_idx]
            cv2.line(canvas, (start_x, start_y), (end_x, end_y), (0, 0, 255), 3)
    
    # 绘制关键点
    for idx, (x, y) in LANDMARKS.items():
        # 选择容差（头部、手腕使用特殊容差）
        if idx == 0:  # 头部
            tol = HEAD_TOLERANCE
        elif idx in [15, 16]:  # 左右手腕
            tol = WRIST_TOLERANCE
        else:
            tol = TOLERANCE
        # 白色圆圈表示识别范围
        cv2.circle(canvas, (x, y), tol, (255, 255, 255), 2)
        # 红色圆点表示目标中心点
        cv2.circle(canvas, (x, y), 10, (0, 0, 255), -1)
        # 黄色编号
        cv2.putText(canvas, str(idx), (x + 15, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        # 白色坐标
        coord_text = f"({x}, {y})"
        cv2.putText(canvas, coord_text, (x + 15, y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 显示说明
    info_lines = [
        "Strong Action Pose - Manual Adjustment",
        "",
        f"Tolerance Range: +/-{TOLERANCE} pixels",
        f"Head Tolerance: +/-{HEAD_TOLERANCE} pixels",
        f"Wrist Tolerance: +/-{WRIST_TOLERANCE} pixels",
        "White Circle = Recognition Range",
        "Red Dot = Target Center",
        "",
        "Key Points:",
        "0=Head, 11/12=Shoulders",
        "13/14=Elbows, 15/16=Wrists",
        "",
        "Modify LANDMARKS in adjust_pose.py",
        "Then re-run to see changes",
        "",
        "Press ESC to exit"
    ]
    
    y_pos = 50
    for line in info_lines:
        cv2.putText(canvas, line, (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
    
    # 显示窗口
    cv2.imshow("Adjust Pose - strong_action", canvas)
    
    print("\n=== Strong Action 关键点坐标 ===")
    print("修改下面的 LANDMARKS 字典中的坐标值，然后重新运行此程序\n")
    print("LANDMARKS = {")
    for idx in sorted(LANDMARKS.keys()):
        x, y = LANDMARKS[idx]
        point_name = {
            0: "头部", 11: "左肩", 12: "右肩",
            13: "左肘", 14: "右肘", 15: "左手腕", 16: "右手腕",
            23: "左臀", 24: "右臀", 25: "左膝", 26: "右膝",
            27: "左脚踝", 28: "右脚踝"
        }.get(idx, "")
        print(f"    {idx:2d}: [{x:4d}, {y:3d}],    # {point_name}")
    print("}\n")
    print("窗口已打开，按 ESC 退出...")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n完成调整后，复制上面的坐标到 pose_configs.py 中的 strong_action 配置")

if __name__ == "__main__":
    main()
