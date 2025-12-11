# LiteDesk Quick Start Guide

快速开始使用 LiteDesk 进行远程桌面控制。

## 📥 下载

访问 [GitHub Releases](https://github.com/h123456001/litedesk/releases/latest) 下载适合你系统的版本：

| 操作系统 | 下载文件 | 说明 |
|---------|---------|------|
| Windows | `litedesk-windows-x64.zip` | Windows 10/11 64位 |
| macOS (Intel) | `litedesk-macos-x64.zip` | Intel 芯片的 Mac |
| macOS (Apple Silicon) | `litedesk-macos-arm64.zip` | M1/M2/M3 芯片的 Mac |
| Linux | `litedesk-linux-x64.zip` | Ubuntu/Debian/CentOS 等 |

## 🚀 基本使用

### 场景一：局域网内直接连接

**步骤 1：在被控端（要被远程控制的电脑）**

```bash
# 下载并解压后
./litedesk-server    # macOS/Linux
litedesk-server.exe  # Windows

# 点击 "Start Sharing" 按钮
# 记下显示的 IP 地址（例如：192.168.1.100）
```

**步骤 2：在控制端（用来控制的电脑）**

```bash
# 下载并解压后
./litedesk-client    # macOS/Linux
litedesk-client.exe  # Windows

# 选择 "Direct Connection" 模式
# 输入服务端 IP：192.168.1.100
# 点击 "Connect" 按钮
```

✅ 完成！现在你可以看到并控制远程桌面了。

### 场景二：通过中继服务器连接（双方都没有公网IP）

**前置条件：**
- 需要一台有公网 IP 的 VPS 服务器

**步骤 1：在 VPS 上部署中继服务器**

```bash
# 下载 Linux 版本到 VPS
wget https://github.com/h123456001/litedesk/releases/latest/download/litedesk-linux-x64.zip
unzip litedesk-linux-x64.zip
cd litedesk-linux-x64

# 运行中继服务器
./litedesk-relay --port 8877

# 记下 VPS 的公网 IP（例如：123.45.67.89）
```

**步骤 2：在被控端**

```bash
./litedesk-server    # macOS/Linux
litedesk-server.exe  # Windows

# 勾选 "Use Relay Server"
# 输入中继服务器地址：123.45.67.89
# 点击 "Start Sharing"
```

**步骤 3：在控制端**

```bash
./litedesk-client    # macOS/Linux
litedesk-client.exe  # Windows

# 选择 "Via Relay Server" 模式
# 输入中继服务器地址：123.45.67.89
# 点击 "List Servers" 查看可用服务器
# 选择目标服务器并点击 "Connect"
```

✅ 完成！通过中继服务器成功连接。

## 🔧 常见问题

### Windows: 安全警告

首次运行时 Windows 可能会显示安全警告：

1. 点击 "更多信息"
2. 点击 "仍要运行"
3. 允许防火墙访问

### macOS: 无法打开

首次运行时 macOS 可能会阻止：

1. 右键点击应用
2. 选择 "打开"
3. 点击 "打开" 确认
4. 在 系统偏好设置 > 安全性与隐私 > 隐私 中授予：
   - 屏幕录制权限
   - 辅助功能权限

### Linux: 权限问题

```bash
# 确保可执行
chmod +x litedesk-*

# 如果遇到依赖问题
sudo apt-get install libxcb-xinerama0
```

### 连接失败

**检查清单：**

- [ ] 服务端已启动并显示 "Waiting for connection"
- [ ] IP 地址输入正确
- [ ] 双方在同一网络（或使用中继服务器）
- [ ] 防火墙未阻止连接
- [ ] 端口 9876 未被占用

## 🎮 使用技巧

### 键盘快捷键

- **Esc**: 断开连接
- **F11**: 全屏模式（如支持）

### 鼠标操作

- **左键**: 正常点击
- **右键**: 右键菜单
- **滚轮**: 滚动页面
- **拖拽**: 拖动元素

### 提高性能

1. **降低质量**: 在设置中降低图像质量可提高帧率
2. **关闭不必要的程序**: 释放系统资源
3. **使用有线网络**: 比 WiFi 更稳定

## 📚 更多资源

- 📖 [完整使用说明](README.md)
- 🔧 [故障排除](TROUBLESHOOTING.md)
- 🌐 [VPS 部署指南](VPS_DEPLOY.md)
- 🏗️ [构建说明](BUILD.md)

## 🆘 获取帮助

遇到问题？

1. 查看 [故障排除文档](TROUBLESHOOTING.md)
2. 搜索 [已有 Issues](https://github.com/h123456001/litedesk/issues)
3. 提交新的 [Issue](https://github.com/h123456001/litedesk/issues/new)

## 🔒 安全提示

⚠️ **注意：** LiteDesk 目前是演示项目，未实现加密。建议：

- ✅ 仅在受信任的网络中使用
- ✅ 不要传输敏感信息
- ✅ 使用完毕后立即断开连接
- ❌ 不要在公网环境直接暴露

## 📱 支持的平台

| 平台 | 被控端 | 控制端 |
|------|-------|-------|
| Windows 10/11 | ✅ | ✅ |
| macOS 10.12+ | ✅ | ✅ |
| Linux (X11) | ✅ | ✅ |

## 📝 许可证

LiteDesk 使用 MIT 许可证。详见 [LICENSE](LICENSE)。

---

**享受使用 LiteDesk！** 🎉

如有问题或建议，欢迎提交 Issue。
