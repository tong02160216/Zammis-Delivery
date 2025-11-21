# 壮咪咪的送信之旅 - Python版使用说明

## 🎮 游戏说明

这是一个基于Python的互动游戏，使用摄像头和动作识别技术。

## 📦 安装依赖

```bash
pip3 install -r requirements.txt
```

## 🚀 运行游戏

```bash
python3 app_simple.py
```

然后在浏览器中打开: http://localhost:5001

## 🎯 游戏玩法

1. 点击"开始游戏"
2. 允许摄像头权限
3. 按照屏幕提示模仿5个动物动作
4. 完成动作后按**空格键**确认
5. 完成所有动作，观看结尾动画

## 🔧 macOS 摄像头权限设置

如果摄像头无法启动，请按以下步骤设置：

### 方法1：系统设置
1. 打开"系统设置" (System Settings)
2. 进入"隐私与安全性" (Privacy & Security)
3. 点击"摄像头" (Camera)
4. 确保"终端" (Terminal) 或你使用的IDE有摄像头权限
5. 如果使用VS Code，确保"Code"也有权限

### 方法2：终端命令
```bash
# 重置摄像头权限
tccutil reset Camera

# 然后重新运行程序
python3 app_simple.py
```

### 方法3：关闭其他占用摄像头的应用
- 关闭FaceTime
- 关闭Zoom
- 关闭Teams
- 关闭其他视频会议软件

## 🐛 常见问题

### Q: 摄像头画面是黑的
**A**: 
1. 检查系统摄像头权限
2. 关闭其他使用摄像头的应用
3. 重启Python程序

### Q: OpenCV错误 "not authorized to capture video"
**A**: 
1. 在终端运行时需要授予摄像头权限
2. 首次运行会弹出权限请求，点击"允许"
3. 如果没有弹出，去系统设置手动添加权限

### Q: 端口5001被占用
**A**: 
修改 `app_simple.py` 中的端口号：
```python
app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)
```

## 📁 项目结构

```
Zamimi/
├── app_simple.py              # Python服务器（简化版）
├── templates/
│   └── index_python.html      # 网页模板
├── static/
│   ├── images/               # 动物图片
│   │   ├── 小狗.jpg
│   │   ├── 小猪.jpg
│   │   ├── 小羚羊.jpg
│   │   └── 长颈鹿.jpg
│   ├── SourceHanSansCN-Bold.otf  # 中文字体
│   └── led_counter-7.ttf         # LED字体
├── requirements.txt           # Python依赖
└── README_PYTHON.md          # 本文件
```

## 🎨 技术栈

- **Flask** - Web框架
- **OpenCV** - 摄像头和图像处理
- **NumPy** - 数据处理
- **HTML/CSS/JavaScript** - 前端界面

## 💡 提示

- 游戏使用空格键手动确认动作完成
- 摄像头画面会自动镜像显示
- 画面上会显示当前要模仿的动作提示
- 完成5个动作后会显示结束画面

## 📝 版本信息

- **版本**: 1.0.0
- **日期**: 2025年11月6日
- **Python版本要求**: 3.7+

## 🙏 致谢

感谢使用本游戏！祝你玩得开心！🎉
