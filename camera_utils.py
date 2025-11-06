"""
摄像头工具函数
简化版摄像头设置
"""
import cv2

def setup_camera(camera_id=0):
    """
    设置并返回摄像头对象
    
    Args:
        camera_id: 摄像头ID，默认为0
    
    Returns:
        cap: OpenCV VideoCapture对象
        camera_id: 使用的摄像头ID
    """
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        raise RuntimeError(f"无法打开摄像头 {camera_id}")
    
    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    return cap, camera_id
