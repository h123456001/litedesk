# LiteDesk NAT 穿透与中继服务器指南

本文档详细说明如何使用 LiteDesk 的中继服务器功能，实现无公网 IP 环境下的远程桌面连接。

## 📖 背景

在实际使用中，很多用户的电脑都位于 NAT 后面，没有公网 IP 地址。传统的 P2P 连接需要至少一方有公网 IP，否则无法建立直接连接。

LiteDesk 的中继服务器解决方案参考了 RustDesk 的架构思想，通过在具有公网 IP 的 VPS 上运行中继服务器，帮助双方：
1. 注册和发现彼此
2. 交换连接信息（公网 IP 和端口）
3. 协调连接建立时机

## 🏗️ 架构说明

### 连接流程

```
步骤 1: 注册
┌────────┐                   ┌────────┐                   ┌────────┐
│ 客户端  │                   │ 中继    │                   │ 服务端  │
│(NAT后) │                   │ 服务器  │                   │(NAT后) │
└───┬────┘                   └───┬────┘                   └───┬────┘
    │ 注册 (peer_id, type)       │                            │
    ├───────────────────────────►│                            │
    │ 注册确认 (public_ip:port)  │                            │
    │◄───────────────────────────┤                            │
    │                            │  注册 (peer_id, type)       │
    │                            │◄───────────────────────────┤
    │                            │  注册确认 (public_ip:port)  │
    │                            ├───────────────────────────►│
    │                            │                            │

步骤 2: 发现
    │ 列出可用服务器            │                            │
    ├───────────────────────────►│                            │
    │ 返回服务器列表            │                            │
    │◄───────────────────────────┤                            │
    │                            │                            │

步骤 3: 连接信息交换
    │ 请求连接到 server_id      │                            │
    ├───────────────────────────►│                            │
    │                            │  通知连接请求               │
    │                            ├───────────────────────────►│
    │  返回服务端连接信息        │                            │
    │◄───────────────────────────┤                            │
    │                            │                            │

步骤 4: 尝试直接连接
    │        尝试直接 TCP 连接 (需要端口转发)                │
    │◄──────────────────────────────────────────────────────►│
```

### 组件说明

**1. relay_server.py (中继服务器)**
- 运行在有公网 IP 的 VPS 上
- 管理已注册的 peer（服务端和客户端）
- 提供 peer 发现和信息交换服务
- 不中转实际的桌面数据流量

**2. relay_client.py (中继客户端库)**
- 被 NetworkServerWithRelay 和 NetworkClientWithRelay 使用
- 处理与中继服务器的通信
- 发送注册、查询、信息交换等请求

**3. NetworkServerWithRelay / NetworkClientWithRelay (增强的网络类)**
- 在原有直接连接基础上添加中继支持
- 自动尝试先连接中继服务器
- 交换信息后尝试建立直接 P2P 连接

## 🚀 部署指南

### 1. 部署中继服务器（VPS）

在你的 VPS 上：

```bash
# 1. 安装 Python 3.7+
sudo apt update
sudo apt install python3 python3-pip

# 2. 上传文件
# 只需要 relay_server.py 文件

# 3. 运行中继服务器
python3 relay_server.py --host 0.0.0.0 --port 8877

# 4. 配置防火墙
sudo ufw allow 8877/tcp
```

**持久化运行（使用 systemd）**：

创建服务文件 `/etc/systemd/system/litedesk-relay.service`：

```ini
[Unit]
Description=LiteDesk Relay Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/litedesk
ExecStart=/usr/bin/python3 /path/to/litedesk/relay_server.py --port 8877
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable litedesk-relay
sudo systemctl start litedesk-relay
sudo systemctl status litedesk-relay
```

### 2. 配置服务端（被控制端）

```bash
# 启动服务端
python3 server.py
```

在 UI 中：
1. ✅ 勾选 "Use Relay Server"
2. 📝 输入 VPS 的公网 IP 地址（例如：`123.45.67.89`）
3. 🚀 点击 "Start Sharing"

服务端会：
- 启动本地服务器监听 9876 端口
- 连接到中继服务器并注册
- 显示分配的 peer_id（例如：`server_hostname`）

**重要提示**：
- 如果服务端也在 NAT 后面，需要配置路由器的端口转发：`外部端口 9876 -> 内部 IP:9876`
- 或者启用 UPnP 自动端口映射

### 3. 配置客户端（控制端）

```bash
# 启动客户端
python3 client.py
```

在 UI 中：
1. 🔄 选择 "Via Relay Server" 模式
2. 📝 输入 VPS 的公网 IP 地址
3. 📋 点击 "List Servers" 查看可用服务器
4. 🎯 选择目标服务器
5. 🔗 点击 "Connect"

客户端会：
- 连接到中继服务器
- 获取目标服务器的连接信息
- 尝试建立直接连接

## 🔍 工作原理

### 协议详解

**消息格式**：所有消息使用 JSON 编码

```
[消息长度:4字节][JSON消息:N字节]
```

**注册消息**（客户端 -> 中继服务器）：
```json
{
  "type": "register",
  "peer_id": "server_hostname",
  "peer_type": "server"
}
```

**注册确认**（中继服务器 -> 客户端）：
```json
{
  "type": "registered",
  "peer_id": "server_hostname",
  "public_ip": "123.45.67.89",
  "public_port": 54321
}
```

**列出 Peers**（客户端 -> 中继服务器）：
```json
{
  "type": "list_peers"
}
```

**Peer 列表**（中继服务器 -> 客户端）：
```json
{
  "type": "peer_list",
  "peers": [
    {"peer_id": "server_hostname", "peer_type": "server"}
  ]
}
```

**获取 Peer 信息**（客户端 -> 中继服务器）：
```json
{
  "type": "get_peer_info",
  "target_id": "server_hostname"
}
```

**Peer 信息响应**（中继服务器 -> 客户端）：
```json
{
  "type": "peer_info",
  "peer_id": "server_hostname",
  "peer_type": "server",
  "public_ip": "123.45.67.89",
  "public_port": 54321
}
```

**连接请求通知**（中继服务器 -> 服务端）：
```json
{
  "type": "connection_request",
  "from_peer_id": "client_hostname",
  "from_peer_type": "client",
  "from_public_ip": "98.76.54.32",
  "from_public_port": 12345
}
```

## ⚠️ 限制和注意事项

### 当前实现的限制

1. **仍需端口转发**：
   - 中继服务器只交换连接信息，不中转数据流量
   - 至少服务端需要配置端口转发或 UPnP
   - 如果双方都完全无法被访问，直接连接会失败

2. **未实现 UDP 打洞**：
   - 当前实现使用 TCP 直接连接
   - 未实现 UDP 打洞技术
   - 未实现 STUN/TURN 协议

3. **无加密通信**：
   - 中继服务器和 peer 之间的通信未加密
   - peer 之间的数据传输也未加密

### 改进方向

**完整的 NAT 穿透方案**需要：

1. **UDP 打洞**：
   - 使用 UDP 进行打洞尝试
   - 实现 simultaneous open 技术
   - 支持多种 NAT 类型

2. **TURN 中继**：
   - 当直接连接失败时
   - 通过中继服务器转发所有流量
   - 牺牲性能换取可用性

3. **UPnP/NAT-PMP**：
   - 自动配置路由器端口映射
   - 无需手动配置

4. **加密传输**：
   - TLS/SSL 加密控制通道
   - 数据流量加密

## 🧪 测试场景

### 场景 1：局域网测试

**目的**：验证基本功能

**步骤**：
1. 在本机运行中继服务器：`python3 relay_server.py`
2. 运行服务端，使用中继：`127.0.0.1`
3. 运行客户端，通过中继连接

**预期**：可以发现服务器并建立连接

### 场景 2：VPS + 局域网设备

**目的**：真实 NAT 环境测试

**设置**：
- VPS（公网）: 运行 relay_server.py
- 服务端（NAT 后）: 配置端口转发 9876
- 客户端（NAT 后）: 通过中继连接

**步骤**：
1. VPS 运行中继服务器
2. 服务端配置路由器端口转发
3. 服务端连接到 VPS 中继
4. 客户端通过中继发现服务端
5. 客户端尝试直接连接服务端公网 IP

**预期**：成功建立连接并传输数据

### 场景 3：双方都在 NAT 后且无端口转发

**目的**：了解限制

**预期结果**：
- 可以通过中继服务器发现彼此
- 尝试直接连接会失败
- 需要手动配置端口转发或等待未来的 TURN 功能

## 📊 性能考虑

### 中继服务器资源消耗

- **CPU**: 极低（仅处理 JSON 消息）
- **内存**: ~10MB + 每个连接 ~1KB
- **网络**: 仅控制消息（KB 级别）
- **推荐配置**: 1核 512MB 内存即可支持数百个并发连接

### 数据传输性能

由于采用直接 P2P 连接，数据传输性能与直接连接相同：
- 帧率：~10 FPS
- 延迟：<100ms（局域网）
- 带宽：1-4 Mbps（1080p）

## 🔧 故障排查

### 问题：无法连接到中继服务器

**检查**：
1. VPS 防火墙是否开放 8877 端口
2. relay_server.py 是否正在运行
3. 网络连接是否正常

### 问题：可以列出服务器但无法连接

**原因**：服务端在 NAT 后面且未配置端口转发

**解决方案**：
1. 配置路由器端口转发：`外部 9876 -> 服务端 IP:9876`
2. 或启用路由器的 UPnP 功能

### 问题：连接速度慢或不稳定

**检查**：
1. 是否通过中继服务器中转数据（当前版本不应该）
2. 网络质量是否良好
3. 服务端和客户端之间的网络路径

## 🔐 安全建议

1. **中继服务器安全**：
   - 使用防火墙限制访问
   - 定期更新系统
   - 监控异常连接

2. **使用 VPN 或 SSH 隧道**：
   - 为中继通道添加加密层
   - 例如：`ssh -L 8877:localhost:8877 vps_ip`

3. **限制访问**：
   - 使用白名单限制可连接的 peer
   - 添加身份验证机制

## 📚 相关资源

- [STUN/TURN 协议](https://tools.ietf.org/html/rfc5389)
- [NAT 穿透技术](https://en.wikipedia.org/wiki/NAT_traversal)
- [WebRTC 连接模型](https://webrtc.org/)
- [RustDesk 架构](https://github.com/rustdesk/rustdesk)

## 🎯 未来改进计划

- [ ] 实现 UDP 打洞
- [ ] 添加 TURN 中继模式（数据中转）
- [ ] 支持 UPnP 自动端口映射
- [ ] 添加加密传输
- [ ] 实现连接质量监控
- [ ] 支持多中继服务器（负载均衡）
