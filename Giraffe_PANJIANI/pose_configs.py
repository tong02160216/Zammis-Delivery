"""
姿势配置文件
手动定义每个姿势的关键点坐标（像素坐标，基于 1280x720 窗口）

关键点索引说明：
0: 鼻子(头部)
11, 12: 左肩, 右肩
13, 14: 左肘, 右肘
15, 16: 左手腕, 右手腕
23, 24: 左臀, 右臀
25, 26: 左膝, 右膝
27, 28: 左脚踝, 右脚踝

坐标说明：
- X 坐标范围: 0 (最左边) 到 1280 (最右边)
- Y 坐标范围: 0 (最上面) 到 720 (最下面)
- 窗口中心点: (640, 360)
"""

import numpy as np

# 窗口尺寸
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# 姿势配置字典
# 坐标格式: [x像素, y像素]，基于 1280×720 窗口
POSE_CONFIGS = {
    "strong_action": {
        "name": "Strong Action",
        "description": "双手举高展示力量 - 动作一",
        "tolerance": 50,  # 容差范围（像素），关键点在此范围内都算正确
        "head_tolerance": 50,  # 头部特殊容差范围
        "wrist_tolerance": 50,  # 手腕特殊容差范围
        "key_points": [15, 16],  # 最关键的点（双手腕），权重更高
        "landmarks": {
            0:  [700, 280],    # 头部（鼻子）
            11: [560, 410],    # 左肩
            12: [800, 410],    # 右肩
            13: [450, 370],    # 左肘（举高）
            14: [970, 340],    # 右肘（举高）
            15: [550, 230],    # 左手腕（举高）
            16: [850, 230],    # 右手腕（举高）
        }
    },
    
    "RaiseHighWithOneHand": {
        "name": "Raise High With One Hand",
        "description": "单手举高",
        "tolerance": 50,  # 容差范围（像素）
        "key_points": [15],  # 最关键的点（左手腕举高）
        "landmarks": {
            0:  [680, 270],    # 头部（鼻子）
            11: [600, 360],    # 左肩
            12: [780, 360],    # 右肩
            13: [490, 480],    # 左肘（举高）
            14: [820, 250],    # 右肘（举高）
            15: [580, 550],    # 左手腕（举高）
            16: [820, 70],     # 右手腕（举高）
        }
    },
    
    "RiseHighWithTwoHand": {
        "name": "Rise High With Two Hands",
        "description": "双手高举过头 - 动作二",
        "tolerance": 50,  # 容差范围（像素）
        "head_tolerance": 50,  # 头部特殊容差范围
        "wrist_tolerance": 50,  # 手腕特殊容差范围
        "key_points": [15, 16],  # 最关键的点（双手腕）
        "landmarks": {
            0:  [705, 250],    # 头部
            11: [560, 410],    # 左肩
            12: [800, 410],    # 右肩
            13: [550, 250],    # 左肘（举高）
            14: [830, 250],    # 右肘（举高）
            15: [550, 50],     # 左手腕（举高）
            16: [830, 50],     # 右手腕（举高）
        }
    },
    
    "CompareHearts": {
        "name": "Compare Hearts",
        "description": "双手比心",
        "tolerance": 50,  # 容差范围（像素）
        "key_points": [15, 16],  # 最关键的点（双手腕比心位置）
        "landmarks": {
            0:  [700, 280],    # 头部（鼻子）
            11: [560, 410],    # 左肩
            12: [800, 410],    # 右肩
            13: [480, 250],    # 左肘（举高）
            14: [930, 250],    # 右肘（举高）
            15: [670, 150],    # 左手腕（举高）
            16: [705, 150],    # 右手腕（举高）
        }
    }
}


def get_pose_landmarks(pose_name):
    """
    获取指定姿势的关键点数组（归一化坐标）
    
    Args:
        pose_name: 姿势名称（配置键）
    
    Returns:
        numpy array: (33, 3) 的关键点数组，坐标已归一化到 0-1 范围
    """
    if pose_name not in POSE_CONFIGS:
        raise ValueError(f"未找到姿势配置: {pose_name}")
    
    # 创建 33 个关键点的数组（MediaPipe 标准）
    landmarks = np.zeros((33, 3))
    
    # 填充已定义的关键点，并转换为归一化坐标
    config = POSE_CONFIGS[pose_name]
    for idx, coords in config["landmarks"].items():
        x_pixel, y_pixel = coords[0], coords[1]
        # 转换为归一化坐标（0-1）
        x_norm = x_pixel / WINDOW_WIDTH
        y_norm = y_pixel / WINDOW_HEIGHT
        # 水平翻转X坐标以匹配镜像模式
        x_norm = 1.0 - x_norm
        landmarks[idx] = [x_norm, y_norm, 0]
    
    return landmarks


def list_available_poses():
    """列出所有可用的姿势配置"""
    return list(POSE_CONFIGS.keys())


def get_pose_info(pose_name):
    """获取姿势的详细信息"""
    if pose_name not in POSE_CONFIGS:
        raise ValueError(f"未找到姿势配置: {pose_name}")
    
    config = POSE_CONFIGS[pose_name]
    return {
        "name": config["name"],
        "description": config["description"],
        "landmark_count": len(config["landmarks"]),
        "tolerance": config.get("tolerance", 50),
        "key_points": config.get("key_points", [])
    }


def get_pose_tolerance(pose_name):
    """获取姿势的容差范围（像素）"""
    if pose_name not in POSE_CONFIGS:
        return 50  # 默认容差
    return POSE_CONFIGS[pose_name].get("tolerance", 50)


def get_key_points(pose_name):
    """获取姿势的关键点索引列表（这些点权重更高）"""
    if pose_name not in POSE_CONFIGS:
        return []
    return POSE_CONFIGS[pose_name].get("key_points", [])
