# 运行说明（Windows / PowerShell）

本示例使用 Pygame 显示一张背景图，并让玩家用 WASD 或方向键控制前景图片移动。图片路径使用绝对路径（用户提供）：

- 前景：F:\code\zammi\Zammis-Delivery\屏幕截图 2025-10-16 105916.png
- 背景：F:\code\zammi\Zammis-Delivery\屏幕截图 2025-10-11 171938.png

步骤：

1. 安装 Python（建议 3.8+）。
2. 在 PowerShell 中安装依赖：

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. 运行程序：

```powershell
python main.py
```

操作：
- 按 W/A/S/D 或 上/下/左/右 来移动前景图片。
- 按 Esc 或关闭窗口退出。

注意：
- 程序会以背景图片大小创建窗口。确保两张图片路径正确且文件存在。若想使用仓库内相对路径，可以修改 `main.py` 中的路径变量。
- 在某些无头/远程环境下（没有显示设备），Pygame 窗口可能无法打开；请在有图形界面的机器上运行。
