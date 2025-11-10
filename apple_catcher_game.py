#!/usr/bin/env python3
"""
像素风格接苹果游戏 - 手势交互版
通过摄像头识别手势来移动篮子接苹果
"""

import cv2
import mediapipe as mp
import pygame
import random
import sys
from pathlib import Path

# 游戏配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义（像素风格）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
SKY_BLUE = (135, 206, 235)
DARK_GREEN = (0, 100, 0)

class Apple:
    """苹果类"""
    def __init__(self):
        self.size = 20
        self.x = random.randint(self.size, SCREEN_WIDTH - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 5)
        
        # 使用加权随机：红苹果稀有(10%)，绿苹果正常(30%)，黄苹果常见(60%)
        rand_num = random.random()
        if rand_num < 0.1:  # 10% 概率红苹果
            self.color = RED
            self.points = 3
        elif rand_num < 0.4:  # 30% 概率绿苹果 (0.1 + 0.3 = 0.4)
            self.color = GREEN
            self.points = 2
        else:  # 60% 概率黄苹果
            self.color = YELLOW
            self.points = 1
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        # 像素风格的苹果
        # 苹果身体
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, self.y - self.size//2, 
                         self.size, self.size))
        # 苹果高光
        pygame.draw.rect(screen, WHITE, 
                        (self.x - self.size//4, self.y - self.size//3, 
                         self.size//4, self.size//4))
        # 苹果柄
        pygame.draw.rect(screen, BROWN, 
                        (self.x - 2, self.y - self.size//2 - 5, 4, 6))
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + self.size
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, 
                          self.size, self.size)

class Basket:
    """篮子类"""
    def __init__(self):
        self.width = 80
        self.height = 40
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 80
        self.color = BROWN
    
    def update_position(self, hand_x):
        """根据手势位置更新篮子位置"""
        if hand_x is not None:
            self.x = hand_x
            # 限制在屏幕范围内
            self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
    
    def draw(self, screen):
        # 像素风格的篮子
        # 篮子底部
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.width//2, self.y, self.width, 8))
        # 左边框
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.width//2, self.y - self.height, 8, self.height))
        # 右边框
        pygame.draw.rect(screen, self.color, 
                        (self.x + self.width//2 - 8, self.y - self.height, 8, self.height))
        # 篮子网格装饰
        for i in range(3):
            y_pos = self.y - 10 - i * 10
            pygame.draw.line(screen, (160, 82, 45), 
                           (self.x - self.width//2 + 8, y_pos),
                           (self.x + self.width//2 - 8, y_pos), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height, 
                          self.width, self.height)

class HandTracker:
    """手势追踪器"""
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1
        )
        self.cap = None
        self.camera_width = 640
        self.camera_height = 480
    
    def setup_camera(self):
        """初始化摄像头"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        return True
    
    def get_hand_position(self):
        """获取手掌中心位置"""
        if self.cap is None:
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        # 翻转镜像
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理手势
        results = self.hands.process(rgb_frame)
        
        hand_x = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 获取手掌中心（手腕到中指根部的中点）
                wrist = hand_landmarks.landmark[0]
                middle_base = hand_landmarks.landmark[9]
                
                center_x = (wrist.x + middle_base.x) / 2
                
                # 转换到游戏屏幕坐标
                hand_x = int(center_x * SCREEN_WIDTH)
                
                # 在摄像头画面上绘制追踪点
                h, w, _ = frame.shape
                cx, cy = int(center_x * w), int((wrist.y + middle_base.y) / 2 * h)
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)
                cv2.putText(frame, "Hand Center", (cx - 50, cy - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 显示摄像头画面（缩小版）
        small_frame = cv2.resize(frame, (200, 150))
        cv2.imshow('Hand Tracking (Press Q to quit)', small_frame)
        cv2.waitKey(1)
        
        return hand_x, frame
    
    def cleanup(self):
        """清理资源"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

class Game:
    """游戏主类"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🍎 像素接苹果 - 手势控制版")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # 游戏对象
        self.basket = Basket()
        self.apples = []
        self.hand_tracker = HandTracker()
        
        # 游戏状态
        self.score = 0
        self.missed = 0
        self.game_over = False
        self.game_won = False  # 新增：胜利状态
        self.spawn_timer = 0
        self.spawn_delay = 40  # 帧数
        
    def spawn_apple(self):
        """生成新苹果"""
        self.apples.append(Apple())
    
    def draw_background(self):
        """绘制像素风格背景"""
        # 天空渐变
        for y in range(SCREEN_HEIGHT):
            color_value = int(135 + (235 - 135) * (y / SCREEN_HEIGHT))
            pygame.draw.line(self.screen, (color_value, 206, 235), 
                           (0, y), (SCREEN_WIDTH, y))
        
        # 像素云朵
        cloud_positions = [(100, 80), (300, 120), (500, 60), (650, 100)]
        for cx, cy in cloud_positions:
            for dx, dy in [(-20, 0), (0, -10), (20, 0), (0, 10)]:
                pygame.draw.rect(self.screen, WHITE, (cx + dx, cy + dy, 15, 15))
        
        # 草地
        pygame.draw.rect(self.screen, DARK_GREEN, 
                        (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        # 草地装饰
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(self.screen, GREEN, 
                           (i, SCREEN_HEIGHT - 50), (i, SCREEN_HEIGHT - 40), 3)
    
    def draw_ui(self):
        """绘制UI"""
        # 分数（左上角，显示目标）- 添加半透明背景，使用小字体
        score_text = self.font_small.render(f"Score: {self.score}/15", True, WHITE)
        score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
        score_bg.set_alpha(150)
        score_bg.fill(BLACK)
        self.screen.blit(score_bg, (5, 5))
        self.screen.blit(score_text, (15, 10))
        
        # 失误（右上角）- 添加半透明背景，使用小字体
        missed_text = self.font_small.render(f"Miss: {self.missed}/3", True, WHITE)
        missed_bg = pygame.Surface((missed_text.get_width() + 20, missed_text.get_height() + 10))
        missed_bg.set_alpha(150)
        missed_bg.fill((139, 0, 0))  # 深红色背景
        self.screen.blit(missed_bg, (SCREEN_WIDTH - missed_text.get_width() - 25, 5))
        self.screen.blit(missed_text, (SCREEN_WIDTH - missed_text.get_width() - 15, 10))
        
        # 提示
        hint_text = self.font_small.render("Move Hand to Control", True, WHITE)
        hint_bg = pygame.Surface((hint_text.get_width() + 10, hint_text.get_height() + 6))
        hint_bg.set_alpha(120)
        hint_bg.fill(BLACK)
        self.screen.blit(hint_bg, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2 - 5, 50))
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 53))
        
        # 苹果分值说明（右下角）- 使用像素方块代替emoji
        points_info = [
            (RED, 3),
            (GREEN, 2),
            (YELLOW, 1)
        ]
        y_offset = SCREEN_HEIGHT - 120
        for color, points in points_info:
            # 绘制像素苹果图标
            apple_size = 15
            apple_x = SCREEN_WIDTH - 120
            apple_y = y_offset
            # 苹果身体
            pygame.draw.rect(self.screen, color, 
                           (apple_x, apple_y, apple_size, apple_size))
            # 苹果高光
            pygame.draw.rect(self.screen, WHITE, 
                           (apple_x + 2, apple_y + 2, 5, 5))
            # 苹果柄
            pygame.draw.rect(self.screen, BROWN, 
                           (apple_x + apple_size//2 - 1, apple_y - 3, 3, 4))
            
            # 绘制分数文字
            info_text = self.font_small.render(f"= {points} fen", True, BLACK)
            self.screen.blit(info_text, (apple_x + apple_size + 10, apple_y))
            y_offset += 25
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 根据胜负显示不同文字
        if self.game_won:
            # 胜利画面
            game_over_text = self.font_large.render("Victory!", True, YELLOW)
            result_text = self.font_medium.render("恭喜获胜！", True, GREEN)
        else:
            # 失败画面
            game_over_text = self.font_large.render("Game Over!", True, RED)
            result_text = self.font_medium.render("游戏失败", True, RED)
        
        score_text = self.font_medium.render(f"最终得分: {self.score}", True, WHITE)
        restart_text = self.font_small.render("按 R 重新开始 | 按 ESC 退出", True, YELLOW)
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 180))
        self.screen.blit(result_text, 
                        (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 240))
        self.screen.blit(score_text, 
                        (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 290))
        self.screen.blit(restart_text, 
                        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
    
    def reset_game(self):
        """重置游戏"""
        self.basket = Basket()
        self.apples = []
        self.score = 0
        self.missed = 0
        self.game_over = False
        self.game_won = False
        self.spawn_timer = 0
    
    def run(self):
        """运行游戏主循环"""
        try:
            # 初始化摄像头
            print("🎮 正在初始化游戏...")
            print("📹 正在启动摄像头...")
            self.hand_tracker.setup_camera()
            print("✅ 摄像头就绪!")
            print("🖐️  请将手放在摄像头前，移动手掌控制篮子")
            print("🍎 游戏开始！")
            
        except RuntimeError as e:
            print(f"❌ 摄像头错误: {e}")
            print("💡 请确保摄像头已连接并可用")
            return
        
        running = True
        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
            
            if not self.game_over:
                # 获取手势位置
                hand_x, _ = self.hand_tracker.get_hand_position()
                
                # 更新篮子位置
                self.basket.update_position(hand_x)
                
                # 生成苹果
                self.spawn_timer += 1
                if self.spawn_timer >= self.spawn_delay:
                    self.spawn_apple()
                    self.spawn_timer = 0
                    # 难度递增
                    if self.spawn_delay > 20:
                        self.spawn_delay -= 0.1
                
                # 更新苹果
                basket_rect = self.basket.get_rect()
                for apple in self.apples[:]:
                    apple.update()
                    
                    # 检测碰撞
                    if apple.get_rect().colliderect(basket_rect):
                        self.apples.remove(apple)
                        self.score += apple.points
                        # 根据苹果颜色显示不同信息
                        if apple.points == 3:
                            print(f"🍎 红苹果！+{apple.points}分 总分: {self.score}")
                        elif apple.points == 2:
                            print(f"🍏 绿苹果！+{apple.points}分 总分: {self.score}")
                        else:
                            print(f"🍋 黄苹果！+{apple.points}分 总分: {self.score}")
                        
                        # 检测胜利条件：达到15分
                        if self.score >= 15:
                            self.game_over = True
                            self.game_won = True
                            print(f"🎉 恭喜获胜！最终得分: {self.score}")
                    
                    # 检测掉落
                    elif apple.is_off_screen():
                        self.apples.remove(apple)
                        self.missed += 1
                        print(f"💔 失误 {self.missed}/3")
                        
                        # 检测失败条件：错过3个苹果
                        if self.missed >= 3:
                            self.game_over = True
                            self.game_won = False
                            print(f"💀 游戏失败！最终得分: {self.score}")
            
            # 绘制
            self.draw_background()
            
            # 绘制苹果
            for apple in self.apples:
                apple.draw(self.screen)
            
            # 绘制篮子
            self.basket.draw(self.screen)
            
            # 绘制UI
            self.draw_ui()
            
            # 游戏结束画面
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # 清理
        self.hand_tracker.cleanup()
        pygame.quit()
        print("👋 游戏结束，感谢游玩！")

def main():
    print("=" * 50)
    print("🍎 像素风格接苹果游戏 - 手势控制版")
    print("=" * 50)
    print("📖 游戏说明：")
    print("  • 移动手掌控制篮子左右移动")
    print("  • 接住苹果得分（红🍎=3分 绿🍏=2分 黄🍋=1分）")
    print("  • 得分达到15分获胜！")
    print("  • 错过3个苹果失败！")
    print("  • 按 R 重新开始")
    print("  • 按 ESC 退出游戏")
    print("=" * 50)
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
