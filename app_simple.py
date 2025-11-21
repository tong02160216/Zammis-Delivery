from flask import Flask, render_template, Response, jsonify, send_from_directory
import cv2
import numpy as np
import time
import os
import threading
import math

# 设置环境变量以跳过OpenCV的授权检查
os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'

app = Flask(__name__)

# 简单的姿态追踪器（使用颜色检测模拟关键点）
class SimplePoseTracker:
    def __init__(self):
        self.prev_frame = None
        self.keypoints = {}
        
    def detect_pose(self, frame):
        """简单的姿态检测 - 检测运动区域并生成模拟关键点"""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return self.generate_default_keypoints(w, h)
        
        # 检测运动
        diff = cv2.absdiff(self.prev_frame, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # 查找运动区域的质心
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大的运动区域
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # 生成基于运动中心的关键点
                keypoints = self.generate_keypoints_from_center(cx, cy, w, h)
                self.prev_frame = gray
                return keypoints
        
        self.prev_frame = gray
        return self.generate_default_keypoints(w, h)
    
    def generate_default_keypoints(self, w, h):
        """生成默认的站立姿态关键点"""
        center_x = w // 2
        return {
            'nose': (center_x, int(h * 0.15)),
            'left_shoulder': (center_x - 50, int(h * 0.3)),
            'right_shoulder': (center_x + 50, int(h * 0.3)),
            'left_elbow': (center_x - 70, int(h * 0.5)),
            'right_elbow': (center_x + 70, int(h * 0.5)),
            'left_wrist': (center_x - 80, int(h * 0.7)),
            'right_wrist': (center_x + 80, int(h * 0.7)),
            'left_hip': (center_x - 30, int(h * 0.6)),
            'right_hip': (center_x + 30, int(h * 0.6)),
            'left_knee': (center_x - 35, int(h * 0.8)),
            'right_knee': (center_x + 35, int(h * 0.8)),
        }
    
    def generate_keypoints_from_center(self, cx, cy, w, h):
        """基于检测到的中心点生成关键点"""
        offset_y = cy - h // 2
        return {
            'nose': (cx, max(10, cy - 100 + offset_y)),
            'left_shoulder': (cx - 50, cy - 50 + offset_y),
            'right_shoulder': (cx + 50, cy - 50 + offset_y),
            'left_elbow': (cx - 70, cy + offset_y),
            'right_elbow': (cx + 70, cy + offset_y),
            'left_wrist': (cx - 80, cy + 50 + offset_y),
            'right_wrist': (cx + 80, cy + 50 + offset_y),
            'left_hip': (cx - 30, cy + 100 + offset_y),
            'right_hip': (cx + 30, cy + 100 + offset_y),
            'left_knee': (cx - 35, cy + 200 + offset_y),
            'right_knee': (cx + 35, cy + 200 + offset_y),
        }

pose_tracker = SimplePoseTracker()

# 游戏状态
game_state = {
    'current_round': 0,
    'total_rounds': 5,
    'action_matched': False,
    'current_action': None,
    'pose_data': None,  # 当前姿态数据
    'match_frames': 0,  # 连续匹配的帧数
    'required_frames': 8  # 需要连续匹配8帧（约0.3秒）才算成功 - 降低难度
}

# 动物动作定义和检测函数
def check_kangaroo_jump(keypoints):
    """袋鼠跳：双手在胸前 - 简化版"""
    if not all(k in keypoints for k in ['left_wrist', 'right_wrist', 'left_shoulder', 'right_shoulder']):
        return False
    
    left_wrist_y = keypoints['left_wrist'][1]
    right_wrist_y = keypoints['right_wrist'][1]
    left_shoulder_y = keypoints['left_shoulder'][1]
    right_shoulder_y = keypoints['right_shoulder'][1]
    shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
    
    # 双手在肩膀附近或更低的位置（放宽条件）
    hands_at_chest = (left_wrist_y > shoulder_y - 100 and right_wrist_y > shoulder_y - 100)
    return hands_at_chest

def check_elephant_trunk(keypoints):
    """大象甩鼻子：一只手臂伸到前方 - 简化版"""
    if not all(k in keypoints for k in ['left_wrist', 'right_wrist', 'nose', 'left_shoulder', 'right_shoulder']):
        return False
    
    left_wrist_y = keypoints['left_wrist'][1]
    right_wrist_y = keypoints['right_wrist'][1]
    nose_y = keypoints['nose'][1]
    shoulder_y = (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
    
    # 只要有一只手在脸部到肩膀之间的高度就算
    hand_at_face = (abs(left_wrist_y - nose_y) < 150 or abs(right_wrist_y - nose_y) < 150 or
                    abs(left_wrist_y - shoulder_y) < 100 or abs(right_wrist_y - shoulder_y) < 100)
    return hand_at_face

def check_giraffe_stretch(keypoints):
    """长颈鹿伸脖子：双手举高 - 简化版"""
    if not all(k in keypoints for k in ['left_wrist', 'right_wrist', 'left_shoulder', 'right_shoulder']):
        return False
    
    left_wrist_y = keypoints['left_wrist'][1]
    right_wrist_y = keypoints['right_wrist'][1]
    shoulder_y = (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
    
    # 只要双手都在肩膀上方就算（降低难度）
    hands_up = (left_wrist_y < shoulder_y and right_wrist_y < shoulder_y)
    return hands_up

def check_penguin_walk(keypoints):
    """企鹅走路：双臂贴身体两侧 - 简化版"""
    if not all(k in keypoints for k in ['left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']):
        return False
    
    left_wrist_x = keypoints['left_wrist'][0]
    right_wrist_x = keypoints['right_wrist'][0]
    left_hip_x = keypoints['left_hip'][0]
    right_hip_x = keypoints['right_hip'][0]
    left_shoulder_x = keypoints['left_shoulder'][0]
    right_shoulder_x = keypoints['right_shoulder'][0]
    
    # 手在肩膀和臀部之间的水平范围内（放宽条件）
    hands_at_side = (abs(left_wrist_x - left_shoulder_x) < 80 and abs(right_wrist_x - right_shoulder_x) < 80)
    return hands_at_side

def check_monkey_scratch(keypoints):
    """猴子挠头：一只手在头上 - 简化版"""
    if not all(k in keypoints for k in ['left_wrist', 'right_wrist', 'nose', 'left_shoulder', 'right_shoulder']):
        return False
    
    left_wrist_y = keypoints['left_wrist'][1]
    right_wrist_y = keypoints['right_wrist'][1]
    nose_y = keypoints['nose'][1]
    shoulder_y = (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
    
    # 只要有一只手在头部附近或之上就算
    hand_on_head = (left_wrist_y < shoulder_y or right_wrist_y < shoulder_y)
    return hand_on_head

animal_actions = [
    {
        'name': '袋鼠跳',
        'image': 'images/小羚羊.jpg',
        'hint': '双手在胸前，做跳跃动作',
        'check_func': check_kangaroo_jump
    },
    {
        'name': '大象甩鼻子',
        'image': 'images/小狗.jpg',
        'hint': '一只手臂伸直，左右摆动',
        'check_func': check_elephant_trunk
    },
    {
        'name': '长颈鹿伸脖子',
        'image': 'images/长颈鹿.jpg',
        'hint': '站直，双手举高',
        'check_func': check_giraffe_stretch
    },
    {
        'name': '企鹅走路',
        'image': 'images/小猪.jpg',
        'hint': '双臂贴身体两侧',
        'check_func': check_penguin_walk
    },
    {
        'name': '猴子挠头',
        'image': 'images/小狗.jpg',
        'hint': '一只手放在头上',
        'check_func': check_monkey_scratch
    }
]

# 摄像头
camera = None
camera_lock = threading.Lock()

def get_camera():
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            # 等待摄像头初始化
            time.sleep(0.5)
            if camera.isOpened():
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("[OK] 摄像头已成功启动！")
            else:
                print("[ERROR] 摄像头启动失败，请检查权限设置")
        return camera

def draw_skeleton(frame, keypoints):
    """在画面上绘制骨架"""
    # 检查是否能看到下半身
    h, w = frame.shape[:2]
    can_see_lower_body = False
    
    if 'left_hip' in keypoints and 'right_hip' in keypoints:
        hip_y = (keypoints['left_hip'][1] + keypoints['right_hip'][1]) / 2
        # 如果臀部在画面下半部分，说明能看到下半身
        if hip_y > h * 0.5:
            can_see_lower_body = True
    
    # 如果看不到下半身，显示提醒
    if not can_see_lower_body:
        # 半透明红色背景
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//2 - 200, 50), (w//2 + 200, 120), (0, 0, 200), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # 白色文字提醒
        cv2.putText(frame, 'Please Stand Back', (w//2 - 180, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(frame, 'Qing Zhan Yuan Yi Dian', (w//2 - 180, 115), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 定义骨架连接
    connections = [
        ('nose', 'left_shoulder'), ('nose', 'right_shoulder'),
        ('left_shoulder', 'right_shoulder'),
        ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
        ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist'),
        ('left_shoulder', 'left_hip'), ('right_shoulder', 'right_hip'),
        ('left_hip', 'right_hip'),
        ('left_hip', 'left_knee'), ('right_hip', 'right_knee'),
    ]
    
    # 绘制连接线
    for connection in connections:
        if connection[0] in keypoints and connection[1] in keypoints:
            pt1 = keypoints[connection[0]]
            pt2 = keypoints[connection[1]]
            cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
    
    # 绘制关键点（小圆点）
    for joint_name, point in keypoints.items():
        cv2.circle(frame, point, 6, (0, 0, 255), -1)  # 红色实心圆
        cv2.circle(frame, point, 8, (255, 255, 255), 2)  # 白色边框
    
    return can_see_lower_body

def generate_frames():
    """生成视频流"""
    camera = get_camera()
    
    if not camera or not camera.isOpened():
        print("[WARNING] 警告：摄像头未能正确打开")
        # 生成一个黑色画面作为替代
        while True:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, 'Camera Not Available', (100, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    while True:
        success, frame = camera.read()
        if not success:
            print("[WARNING] 无法读取摄像头画面")
            time.sleep(0.1)
            continue
        
        # 镜像翻转
        frame = cv2.flip(frame, 1)
        
        # 检测姿态并绘制骨架
        keypoints = pose_tracker.detect_pose(frame)
        can_see_lower_body = draw_skeleton(frame, keypoints)
        
        # 保存姿态数据用于动作识别
        game_state['pose_data'] = keypoints
        
        # 如果正在游戏中，检查动作是否匹配（只有能看到下半身时才进行识别）
        if game_state['current_action'] is not None and can_see_lower_body:
            action_index = game_state['current_action']
            if 0 <= action_index < len(animal_actions):
                action = animal_actions[action_index]
                is_match = action['check_func'](keypoints)
                
                if is_match:
                    game_state['match_frames'] += 1
                    # 显示匹配进度
                    progress = min(100, int(game_state['match_frames'] / game_state['required_frames'] * 100))
                    cv2.rectangle(frame, (10, 10), (10 + progress * 2, 30), (0, 255, 0), -1)
                    cv2.rectangle(frame, (10, 10), (210, 30), (255, 255, 255), 2)
                    
                    # 如果连续匹配足够多帧，标记为成功
                    if game_state['match_frames'] >= game_state['required_frames']:
                        game_state['action_matched'] = True
                else:
                    # 重置计数
                    game_state['match_frames'] = 0
        
        # 编码为 JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """主页"""
    import random
    from flask import make_response
    version = random.randint(1000, 9999)
    response = make_response(render_template('index_python.html', cache_bust=version))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/video_feed')
def video_feed():
    """视频流"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

@app.route('/api/start_round/<int:round_num>')
def start_round(round_num):
    """开始新一轮"""
    if 0 <= round_num < len(animal_actions):
        game_state['current_round'] = round_num
        game_state['current_action'] = round_num
        game_state['action_matched'] = False
        game_state['match_frames'] = 0  # 重置匹配帧数
        action = animal_actions[round_num]
        return jsonify({
            'success': True,
            'action': {
                'name': action['name'],
                'image': action['image'],
                'hint': action['hint']
            }
        })
    return jsonify({'success': False})

@app.route('/api/check_action')
def check_action():
    """检查动作是否匹配（自动识别）"""
    matched = game_state['action_matched']
    if matched:
        # 重置匹配状态
        game_state['action_matched'] = False
        game_state['match_frames'] = 0
    return jsonify({
        'matched': matched
    })

@app.route('/api/reset')
def reset_game():
    """重置游戏"""
    game_state['current_round'] = 0
    game_state['current_action'] = None
    game_state['action_matched'] = False
    game_state['manual_success'] = False
    return jsonify({'success': True})

if __name__ == '__main__':
    print("=" * 50)
    print("壮咪咪的送信之旅 - Python版")
    print("=" * 50)
    print("服务器启动在: http://localhost:5001")
    print("请在浏览器中打开上面的地址")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
