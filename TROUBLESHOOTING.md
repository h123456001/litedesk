# LiteDesk 故障排除指南

## 常见问题

### 1. 依赖安装问题

#### 问题：`pip install` 失败

**解决方案：**
```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 使用国内镜像源（可选）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题：PyQt5 安装失败

**解决方案：**
- **Ubuntu/Debian**: 
  ```bash
  sudo apt-get install python3-pyqt5
  ```
- **macOS**: 
  ```bash
  brew install pyqt5
  ```
- **Windows**: 使用预编译包
  ```bash
  pip install PyQt5
  ```

### 2. 权限问题

#### macOS 权限问题

**问题：** 无法捕获屏幕或控制鼠标键盘

**解决方案：**
1. 打开"系统偏好设置" > "安全性与隐私" > "隐私"
2. 在"屏幕录制"中添加 Terminal/Python
3. 在"辅助功能"中添加 Terminal/Python
4. 重启应用程序

#### Linux X11 问题

**问题：** 屏幕捕获失败

**解决方案：**
```bash
# 安装必要的 X11 开发包
sudo apt-get install python3-dev python3-xlib libx11-dev

# 确保运行在 X11 会话（非 Wayland）
echo $XDG_SESSION_TYPE
```

### 3. 网络连接问题

#### 无法连接到服务器

**检查清单：**
1. 确认服务端和客户端在同一网络
2. 检查防火墙设置
3. 验证 IP 地址正确
4. 确认端口 9876 未被占用

**测试连接：**
```bash
# 在服务端查看监听状态
netstat -an | grep 9876

# 在客户端测试连接
telnet <server-ip> 9876
# 或
nc -zv <server-ip> 9876
```

**开放防火墙端口：**
```bash
# Ubuntu/Debian
sudo ufw allow 9876/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=9876/tcp --permanent
sudo firewall-cmd --reload

# Windows PowerShell (管理员)
New-NetFirewallRule -DisplayName "LiteDesk" -Direction Inbound -Protocol TCP -LocalPort 9876 -Action Allow
```

### 4. 性能问题

#### 画面卡顿

**解决方案：**

1. **降低图像质量**（在 server.py 中）：
   ```python
   self.screen_capture = ScreenCapture(quality=30)  # 降低到 30
   ```

2. **降低帧率**（在 server.py 的 server_loop 中）：
   ```python
   time.sleep(0.2)  # 从 0.1 改为 0.2（约 5 FPS）
   ```

3. **减小分辨率**：考虑在较小的窗口中运行需要共享的应用

#### 高带宽占用

**解决方案：**
- 降低 JPEG 质量（参数 20-40）
- 降低帧率（sleep 0.15-0.25）
- 使用有线连接而非 WiFi

### 5. 运行时错误

#### 导入错误：`ModuleNotFoundError`

**解决方案：**
```bash
# 确认在正确的目录
cd /path/to/litedesk

# 重新安装依赖
pip install -r requirements.txt

# 验证安装
python3 test_litedesk.py
```

#### 端口已被占用

**解决方案：**
```bash
# 查找占用端口的进程
# Linux/macOS
lsof -i :9876

# Windows
netstat -ano | findstr :9876

# 结束进程或修改代码使用其他端口
```

### 6. 显示问题

#### 客户端窗口显示黑屏

**可能原因：**
1. 服务端尚未开始共享
2. 网络连接中断
3. 防火墙阻止了数据传输

**解决方案：**
- 检查服务端状态显示
- 查看命令行输出的错误信息
- 重新建立连接

#### 远程桌面画面比例失真

**说明：** 这是正常的，客户端会自动缩放以适应窗口大小

**如需调整：**
- 调整客户端窗口大小
- 代码中使用 `Qt.KeepAspectRatio` 保持比例

## 获取帮助的日志信息

如果遇到问题需要帮助，请提供以下信息：

```bash
# 1. Python 版本
python3 --version

# 2. 操作系统信息
# Linux
uname -a
cat /etc/os-release

# macOS
sw_vers

# Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# 3. 已安装的包版本
pip list | grep -E "mss|Pillow|pynput|PyQt5"

# 4. 运行测试脚本
python3 test_litedesk.py

# 5. 错误信息
# 复制完整的错误堆栈信息
```

## 最佳实践

1. **首次使用**：先在本地测试（服务端和客户端在同一台机器）
2. **安全使用**：仅在可信网络环境中使用
3. **性能优化**：根据网络状况调整质量和帧率
4. **及时更新**：保持依赖包为最新稳定版本

## 已知限制

1. **无加密传输**：数据未加密，不适合公网使用
2. **单客户端**：一次只支持一个客户端连接
3. **基础功能**：不支持文件传输、剪贴板同步等高级功能
4. **平台兼容**：在某些 Linux 发行版上可能需要额外配置

## 报告问题

如果问题未在此列出，请在 GitHub 仓库提交 Issue，包含：
- 问题描述
- 操作系统和版本
- Python 版本
- 完整的错误信息
- 复现步骤
