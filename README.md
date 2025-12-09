# LiteDesk - 简易远程桌面

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

基于 RustDesk 架构思想实现的简易版点对点(P2P)远程桌面控制软件。支持屏幕共享和远程控制功能。

## ✨ 功能特性

- 🖥️ **屏幕共享**: 实时捕获并传输桌面画面
- 🖱️ **远程控制**: 支持鼠标和键盘远程操作
- 🔄 **点对点连接**: 无需中继服务器的直连方式
- 🎨 **图形界面**: 基于 PyQt5 的友好用户界面
- ⚡ **高效传输**: JPEG 压缩优化网络传输
- 🔒 **轻量级**: 纯 Python 实现，易于部署

## 📋 系统要求

- Python 3.7 或更高版本
- 支持的操作系统：
  - Windows 10/11
  - macOS 10.12+
  - Linux (X11)

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 启动服务端（被控制端）

在需要被远程控制的电脑上运行：

```bash
python server.py
```

1. 点击 "Start Sharing" 按钮开始共享桌面
2. 查看本机 IP 地址并告知客户端
3. 等待客户端连接

### 3. 启动客户端（控制端）

在控制其他电脑的设备上运行：

```bash
python client.py
```

1. 输入服务端的 IP 地址
2. 点击 "Connect" 按钮建立连接
3. 连接成功后即可看到远程桌面并进行控制

## 📖 使用说明

### 服务端操作

- **开始共享**: 点击 "Start Sharing" 按钮，服务器将监听 9876 端口
- **停止共享**: 点击 "Stop Sharing" 按钮断开连接
- **查看状态**: 界面显示当前连接状态和客户端信息

### 客户端操作

- **鼠标控制**: 在远程桌面窗口中移动鼠标即可控制远程鼠标
- **点击操作**: 左键和右键点击都会同步到远程端
- **滚轮操作**: 鼠标滚轮可以滚动远程桌面
- **键盘输入**: 在远程桌面窗口中输入键盘内容会发送到远程端
- **断开连接**: 点击 "Disconnect" 按钮或关闭窗口

## 🏗️ 架构设计

```
┌─────────────────┐              ┌─────────────────┐
│   客户端 (Client) │              │  服务端 (Server)  │
│                 │              │                 │
│  ┌───────────┐  │              │  ┌───────────┐  │
│  │ UI Layer  │  │              │  │ UI Layer  │  │
│  └─────┬─────┘  │              │  └─────┬─────┘  │
│        │        │              │        │        │
│  ┌─────▼─────┐  │   TCP/IP     │  ┌─────▼─────┐  │
│  │  Network  │◄─┼──────────────┼─►│  Network  │  │
│  │  Client   │  │  Port 9876   │  │  Server   │  │
│  └─────┬─────┘  │              │  └─────┬─────┘  │
│        │        │              │        │        │
│  ┌─────▼─────┐  │              │  ┌─────▼─────┐  │
│  │  Display  │  │              │  │  Screen   │  │
│  │  & Input  │  │              │  │  Capture  │  │
│  └───────────┘  │              │  └───────────┘  │
│                 │              │        │        │
│                 │              │  ┌─────▼─────┐  │
│                 │              │  │   Input   │  │
│                 │              │  │ Controller│  │
│                 │              │  └───────────┘  │
└─────────────────┘              └─────────────────┘
```

### 核心模块

1. **screen_capture.py**: 屏幕捕获模块
   - 使用 `mss` 库高效捕获屏幕
   - JPEG 压缩降低网络带宽需求

2. **network.py**: 网络通信模块
   - TCP Socket 实现可靠的 P2P 连接
   - 自定义协议处理帧传输和命令传递

3. **input_control.py**: 输入控制模块
   - 使用 `pynput` 库模拟鼠标和键盘操作
   - 支持跨平台的输入控制

4. **server.py**: 服务端应用
   - PyQt5 图形界面
   - 多线程处理连接和数据传输

5. **client.py**: 客户端应用
   - PyQt5 图形界面
   - 实时显示远程桌面并发送控制命令

## 🔧 配置说明

### 端口配置

默认使用端口 `9876`，如需修改可在代码中调整：

```python
# server.py
self.server = NetworkServer(host='0.0.0.0', port=9876)

# client.py
self.client.connect(ip_address, 9876)
```

### 图像质量

在 `server.py` 中可调整 JPEG 压缩质量（1-100）：

```python
self.screen_capture = ScreenCapture(quality=50)
```

- 较低值：更小的带宽占用，但画质下降
- 较高值：更好的画质，但需要更多带宽

### 帧率控制

在 `server.py` 的 `server_loop` 方法中调整：

```python
time.sleep(0.1)  # 约 10 FPS
```

## 🛠️ 技术栈

- **Python 3.7+**: 主要开发语言
- **PyQt5**: 图形用户界面
- **mss**: 跨平台屏幕截图
- **Pillow**: 图像处理和压缩
- **pynput**: 跨平台输入控制
- **socket**: TCP 网络通信

## 📝 网络协议

### 帧传输协议

```
Header (12 bytes):
  - Width (4 bytes, unsigned int, big-endian)
  - Height (4 bytes, unsigned int, big-endian)
  - Data Length (4 bytes, unsigned int, big-endian)
Data:
  - JPEG compressed image data
```

### 命令协议

```
Header (4 bytes):
  - Command Length (4 bytes, unsigned int, big-endian)
Data:
  - JSON encoded command
  
Command Format:
{
  "type": "mouse_move|mouse_click|mouse_scroll|key_press",
  "data": {
    // Type-specific data
  }
}
```

## ⚠️ 注意事项

1. **防火墙配置**: 确保服务端的 9876 端口未被防火墙阻止
2. **网络连接**: 客户端和服务端需要在同一网络或能够互相访问
3. **权限要求**: 
   - macOS 需要授予屏幕录制和辅助功能权限
   - Linux 需要 X11 显示服务器支持
4. **安全警告**: 此为演示项目，未实现加密和身份验证，不建议在公网使用

## 🔒 安全建议

当前版本为演示性质，如需在生产环境使用，建议添加：

- 🔐 连接密码验证
- 🔒 SSL/TLS 加密传输
- 🚪 端口敲门机制
- 📝 连接日志记录
- ⏱️ 会话超时机制

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目架构参考了 [RustDesk](https://github.com/rustdesk/rustdesk) 的设计思想。

## 📧 联系方式

如有问题或建议，请提交 Issue。