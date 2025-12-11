# LiteDesk - 简易远程桌面

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)
![Cross-Platform](https://img.shields.io/badge/cross--platform-ready-success.svg)

基于 RustDesk 架构思想实现的简易版点对点(P2P)远程桌面控制软件。支持屏幕共享和远程控制功能。

**🆕 新增 NAT 穿透支持**：通过中继服务器实现无公网 IP 的远程连接！
**✨ 完整跨平台支持**：Mac、Windows、Linux 全平台图形化界面！

## ✨ 功能特性

- 🖥️ **屏幕共享**: 实时捕获并传输桌面画面
- 🖱️ **远程控制**: 支持鼠标和键盘远程操作
- 🔄 **点对点连接**: 无需中继服务器的直连方式
- 🌐 **NAT 穿透**: 通过 VPS 中继服务器连接（双方无公网 IP 时）
- 🎨 **图形界面**: 基于 PyQt5 的友好用户界面
- ⚡ **高效传输**: JPEG 压缩优化网络传输
- 🔒 **轻量级**: 纯 Python 实现，易于部署
- 🌍 **跨平台**: 完整支持 macOS、Windows、Linux

## 🖥️ 平台支持

| 平台 | 被控端 (Server) | 控制端 (Client) | 状态 |
|------|----------------|----------------|------|
| **macOS** | ✅ 完全支持 | ✅ 完全支持 | 10.12+ |
| **Windows** | ✅ 完全支持 | ✅ 完全支持 | 10/11 |
| **Linux** | ✅ 完全支持 | ✅ 完全支持 | X11 |

## 📋 系统要求

- Python 3.7 或更高版本
- 支持的操作系统：
  - **macOS**: 10.12 (Sierra) 或更高
  - **Windows**: Windows 10/11
  - **Linux**: 需要 X11 显示服务器

## 🚀 快速开始

### 快速安装 (推荐)

**macOS / Linux:**
```bash
git clone https://github.com/h123456001/litedesk.git
cd litedesk
./start_server.sh  # 启动被控端
# 或
./start_client.sh  # 启动控制端
```

**Windows:**
```cmd
git clone https://github.com/h123456001/litedesk.git
cd litedesk
start_server.bat  # 启动被控端
REM 或
start_client.bat  # 启动控制端
```

启动脚本会自动：
- 检查 Python 安装
- 安装所需依赖
- 显示平台特定说明
- 启动应用程序

### 1. 安装依赖

如需手动安装：

```bash
# 克隆仓库
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# 安装 Python 依赖
pip install -r requirements.txt
# Windows 使用: pip install -r requirements.txt
# macOS/Linux 使用: pip3 install -r requirements.txt
```

### 2. 启动服务端（被控制端）

在需要被远程控制的电脑上运行：

**使用启动脚本 (推荐):**
```bash
./start_server.sh    # macOS/Linux
start_server.bat     # Windows
```

**或直接运行:**
```bash
python3 server.py    # macOS/Linux
python server.py     # Windows
```

**平台特定注意事项:**
- **macOS**: 首次运行需要授予屏幕录制和辅助功能权限
- **Windows**: 可能需要允许防火墙访问，建议以管理员身份运行
- **Linux**: 需要 X11 显示服务器，确保 DISPLAY 环境变量已设置

操作步骤：
1. 点击 "Start Sharing" 按钮开始共享桌面
2. 查看本机 IP 地址并告知客户端
3. 等待客户端连接

### 3. 启动客户端（控制端）

在控制其他电脑的设备上运行：

**使用启动脚本 (推荐):**
```bash
./start_client.sh    # macOS/Linux
start_client.bat     # Windows
```

**或直接运行:**
```bash
python3 client.py    # macOS/Linux
python client.py     # Windows
```

#### 直接连接模式（局域网）

1. 选择 "Direct Connection" 模式
2. 输入服务端的 IP 地址
3. 点击 "Connect" 按钮建立连接
4. 连接成功后即可看到远程桌面并进行控制

#### 中继模式（无公网 IP）

当服务端和客户端都没有公网 IP 时，可以使用中继服务器：

**第一步：在有公网 IP 的 VPS 上启动中继服务器**

```bash
python relay_server.py --port 8877
```

**第二步：服务端配置**

1. 勾选 "Use Relay Server"
2. 输入 VPS 的公网 IP 地址
3. 点击 "Start Sharing"
4. 服务端会自动注册到中继服务器

**第三步：客户端连接**

1. 选择 "Via Relay Server" 模式
2. 输入 VPS 的公网 IP 地址
3. 点击 "List Servers" 查看可用服务器
4. 选择目标服务器并点击 "Connect"
5. 系统会尝试建立直接连接，如果失败会提示配置端口转发

## 🌐 NAT 穿透架构

```
客户端 (无公网IP)          中继服务器 (VPS)          服务端 (无公网IP)
      │                          │                          │
      │  1. 注册到中继服务器      │                          │
      │─────────────────────────►│                          │
      │                          │◄─────────────────────────│
      │                          │  2. 注册到中继服务器      │
      │                          │                          │
      │  3. 请求服务器列表        │                          │
      │─────────────────────────►│                          │
      │◄─────────────────────────│                          │
      │  4. 返回可用服务器        │                          │
      │                          │                          │
      │  5. 请求连接信息          │                          │
      │─────────────────────────►│                          │
      │                          │──────────────────────────►│
      │                          │  6. 通知连接请求          │
      │                          │                          │
      │  7. 交换连接信息 (IP/Port)                          │
      │◄─────────────────────────┼─────────────────────────►│
      │                          │                          │
      │  8. 尝试直接 P2P 连接     │                          │
      │◄─────────────────────────┼─────────────────────────►│
      │        (需要端口转发或 UPnP)                         │
```

### 中继服务器功能

中继服务器（relay_server.py）提供以下功能：

1. **Peer 注册**: 服务端和客户端注册身份和连接信息
2. **Peer 发现**: 客户端查询可用的服务端列表
3. **信息交换**: 交换公网 IP 和端口信息用于 P2P 连接
4. **连接协调**: 通知双方建立连接的时机

**注意**: 中继服务器仅用于信息交换，不中转实际的桌面数据流量。实际数据传输仍需要至少一方能够被直接访问（通过端口转发或 UPnP）。

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
   - 支持中继模式进行 NAT 穿透

3. **relay_client.py**: 中继客户端模块
   - 连接到中继服务器
   - Peer 注册和发现
   - 连接信息交换

4. **relay_server.py**: 中继服务器
   - Peer 注册和管理
   - 信息交换和连接协调
   - 运行在有公网 IP 的 VPS 上

5. **input_control.py**: 输入控制模块
   - 使用 `pynput` 库模拟鼠标和键盘操作
   - 支持跨平台的输入控制

6. **server.py**: 服务端应用
   - PyQt5 图形界面
   - 多线程处理连接和数据传输
   - 支持直接模式和中继模式

7. **client.py**: 客户端应用
   - PyQt5 图形界面
   - 实时显示远程桌面并发送控制命令
   - 支持直接连接和通过中继连接

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

## 🧪 测试

LiteDesk 提供了完整的测试套件来验证各平台的兼容性：

### 基础组件测试
```bash
python3 test_litedesk.py    # macOS/Linux
python test_litedesk.py     # Windows
```

### 综合测试 (推荐)
```bash
python3 test_comprehensive.py    # macOS/Linux
python test_comprehensive.py     # Windows
```

综合测试包括：
- ✓ 平台检测和信息获取
- ✓ 依赖项可用性检查
- ✓ 网络协议编码/解码
- ✓ Socket 通信测试
- ✓ 图像压缩/解压测试

### 平台信息工具
```bash
python3 platform_utils.py    # macOS/Linux
python platform_utils.py     # Windows
```

显示：
- 当前平台信息
- 权限要求
- 网络配置
- 依赖状态

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
   - **macOS**: 需要授予屏幕录制和辅助功能权限 (系统偏好设置 > 安全性与隐私 > 隐私)
   - **Windows**: 需要允许防火墙访问，建议以管理员身份运行
   - **Linux**: 需要 X11 显示服务器支持，确保 DISPLAY 环境变量已设置
4. **安全警告**: 此为演示项目，未实现加密和身份验证，不建议在公网使用

详细的平台特定说明请参考：
- 📖 [安装指南 (INSTALL.md)](INSTALL.md) - 详细的各平台安装步骤
- 🖥️ [跨平台指南 (PLATFORM.md)](PLATFORM.md) - 平台兼容性和特性说明
- 🔧 [故障排除 (TROUBLESHOOTING.md)](TROUBLESHOOTING.md) - 常见问题解决方案

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