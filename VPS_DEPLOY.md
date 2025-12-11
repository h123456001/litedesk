# LiteDesk VPS 中继服务器部署指南

本指南说明如何在 VPS 上部署 LiteDesk 中继服务器，支持 NAT 穿透功能。

## 📋 准备工作

### VPS 要求
- 具有公网 IP 地址
- 支持的操作系统：Linux (推荐 Ubuntu/Debian/CentOS)、Windows Server、或任何支持 Python 的系统
- 至少 512MB RAM
- 开放端口：8877 (默认，可配置)

### 两种部署方式

#### 方式一：使用可执行文件（推荐）
- ✅ 无需安装 Python
- ✅ 部署简单快速
- ✅ 适合生产环境

#### 方式二：从源码运行
- ✅ 便于调试和定制
- ✅ 可以查看和修改代码
- ⚠️ 需要 Python 3.7+ 环境

## 🚀 快速部署（使用可执行文件）

### Linux VPS 部署

```bash
# 1. 下载最新 Release
wget https://github.com/h123456001/litedesk/releases/latest/download/litedesk-linux-x64.zip

# 2. 解压
unzip litedesk-linux-x64.zip
cd litedesk-linux-x64

# 3. 赋予执行权限
chmod +x litedesk-relay

# 4. 直接运行（前台）
./litedesk-relay --port 8877

# 或后台运行
nohup ./litedesk-relay --port 8877 > relay.log 2>&1 &
```

### 使用配置文件

```bash
# 1. 复制配置模板
cp vps.ini.example vps.ini

# 2. 编辑配置文件
nano vps.ini

# 3. 运行（自动读取 vps.ini 配置）
./litedesk-relay
```

### Windows Server 部署

```cmd
REM 1. 下载 litedesk-windows-x64.zip
REM 2. 解压到目录，例如 C:\litedesk\
REM 3. 运行中继服务器

cd C:\litedesk\litedesk-windows-x64
litedesk-relay.exe --port 8877

REM 或使用配置文件
copy vps.ini.example vps.ini
notepad vps.ini
litedesk-relay.exe
```

## 🔧 使用 systemd 服务（Linux 推荐）

创建 systemd 服务以实现开机自启和进程管理。

### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/litedesk-relay.service
```

### 2. 添加以下内容

```ini
[Unit]
Description=LiteDesk Relay Server
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/opt/litedesk
ExecStart=/opt/litedesk/litedesk-relay --port 8877
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/litedesk

[Install]
WantedBy=multi-user.target
```

### 3. 部署可执行文件

```bash
# 创建部署目录
sudo mkdir -p /opt/litedesk
cd /opt/litedesk

# 下载并解压
sudo wget https://github.com/h123456001/litedesk/releases/latest/download/litedesk-linux-x64.zip
sudo unzip litedesk-linux-x64.zip
sudo mv litedesk-linux-x64/* .
sudo chmod +x litedesk-relay

# 配置（可选）
sudo cp vps.ini.example vps.ini
sudo nano vps.ini
```

### 4. 启动服务

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start litedesk-relay

# 设置开机自启
sudo systemctl enable litedesk-relay

# 查看状态
sudo systemctl status litedesk-relay

# 查看日志
sudo journalctl -u litedesk-relay -f
```

## 🐳 Docker 部署

### 创建 Dockerfile

```dockerfile
FROM ubuntu:22.04

# 安装必要的库
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 下载并解压 LiteDesk
RUN wget https://github.com/h123456001/litedesk/releases/latest/download/litedesk-linux-x64.zip \
    && unzip litedesk-linux-x64.zip \
    && mv litedesk-linux-x64/* . \
    && rm -rf litedesk-linux-x64 litedesk-linux-x64.zip \
    && chmod +x litedesk-relay

# 暴露端口
EXPOSE 8877

# 启动中继服务器
CMD ["./litedesk-relay", "--port", "8877"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t litedesk-relay .

# 运行容器
docker run -d \
  --name litedesk-relay \
  -p 8877:8877 \
  --restart unless-stopped \
  litedesk-relay

# 查看日志
docker logs -f litedesk-relay
```

### 使用 docker-compose

创建 `docker-compose.yml`:

```yaml
version: '3'
services:
  litedesk-relay:
    image: litedesk-relay
    container_name: litedesk-relay
    ports:
      - "8877:8877"
    restart: unless-stopped
    volumes:
      - ./vps.ini:/app/vps.ini:ro
```

运行：
```bash
docker-compose up -d
```

## 🔒 防火墙配置

### iptables (Linux)

```bash
# 允许中继服务器端口
sudo iptables -A INPUT -p tcp --dport 8877 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### firewalld (CentOS/RHEL)

```bash
sudo firewall-cmd --permanent --add-port=8877/tcp
sudo firewall-cmd --reload
```

### ufw (Ubuntu)

```bash
sudo ufw allow 8877/tcp
sudo ufw reload
```

### 云服务商安全组

如果使用云服务器（AWS、阿里云、腾讯云等），还需要在控制台配置安全组规则：

- **协议**: TCP
- **端口**: 8877
- **源地址**: 0.0.0.0/0 (允许所有 IP)

## 📝 配置文件详解 (vps.ini)

```ini
[relay]
# 监听地址（通常保持 0.0.0.0 以接受所有网络接口的连接）
host = 0.0.0.0

# 监听端口
port = 8877

[connection]
# 客户端连接超时（秒）
timeout = 30

# 最大重连次数
max_retries = 3

# 重试延迟（秒）
retry_delay = 5

[advanced]
# 保活间隔（秒）
keepalive_interval = 30

# 网络缓冲区大小
buffer_size = 65536

# 是否启用压缩
compression = false
```

## 🔍 监控和维护

### 查看运行状态

```bash
# systemd 服务
sudo systemctl status litedesk-relay

# 进程状态
ps aux | grep litedesk-relay

# 端口监听状态
sudo netstat -tlnp | grep 8877
# 或
sudo ss -tlnp | grep 8877
```

### 查看日志

```bash
# systemd 日志
sudo journalctl -u litedesk-relay -f

# 如果是手动运行，查看 nohup.out 或自定义日志文件
tail -f relay.log
```

### 性能监控

```bash
# CPU 和内存使用
top -p $(pgrep litedesk-relay)

# 网络连接数
netstat -an | grep 8877 | wc -l
```

## 🧪 测试中继服务器

### 测试连接

```bash
# 使用 telnet 测试端口
telnet your-vps-ip 8877

# 使用 nc (netcat)
nc -zv your-vps-ip 8877

# 使用 nmap
nmap -p 8877 your-vps-ip
```

### 验证功能

1. 启动中继服务器
2. 在本地运行 LiteDesk Server，勾选 "Use Relay Server"，填入 VPS IP
3. 在另一台机器运行 LiteDesk Client，同样配置中继服务器
4. 尝试连接

## 🛠️ 故障排查

### 问题：无法连接到中继服务器

**解决方案：**
1. 检查防火墙设置
2. 确认端口已开放
3. 检查云服务商安全组规则
4. 验证 VPS 的公网 IP 是否正确

```bash
# 查看公网 IP
curl ifconfig.me
# 或
curl ipinfo.io/ip
```

### 问题：服务意外停止

**解决方案：**
1. 查看日志找出原因
2. 确保 systemd 服务配置了自动重启
3. 检查系统资源（内存、磁盘空间）

```bash
# 查看系统资源
free -h
df -h
```

### 问题：连接数过多导致性能下降

**解决方案：**
1. 增加 VPS 配置（CPU、内存）
2. 优化系统参数：

```bash
# 增加最大文件描述符
sudo nano /etc/security/limits.conf
# 添加：
* soft nofile 65535
* hard nofile 65535

# 优化网络参数
sudo nano /etc/sysctl.conf
# 添加：
net.ipv4.tcp_max_syn_backlog = 8192
net.core.somaxconn = 1024
net.ipv4.tcp_tw_reuse = 1

# 应用更改
sudo sysctl -p
```

## 📊 多实例部署

如需提高可用性，可以部署多个中继服务器：

```bash
# 在不同的 VPS 上部署多个实例
VPS1: litedesk-relay --port 8877
VPS2: litedesk-relay --port 8877

# 客户端可以配置多个中继服务器地址
# 在配置中添加备用服务器
```

## 🔐 安全建议

1. **使用防火墙**：只开放必要的端口
2. **定期更新**：保持系统和软件更新
3. **监控日志**：定期检查异常连接
4. **限制连接**：可以使用 iptables 限制连接速率
5. **使用 HTTPS/TLS**：对于生产环境，考虑添加加密层

```bash
# 限制每个 IP 的连接数
sudo iptables -A INPUT -p tcp --dport 8877 -m connlimit --connlimit-above 10 -j REJECT
```

## 📚 从源码部署（可选）

如果需要从源码运行（用于开发或定制）：

```bash
# 1. 安装 Python 和依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 2. 克隆仓库
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# 3. 安装依赖（relay 服务器不需要 PyQt5）
pip3 install -r requirements.txt

# 4. 运行
python3 relay_server.py --port 8877
```

## 📞 支持

如有问题：
- 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 提交 [GitHub Issue](https://github.com/h123456001/litedesk/issues)
- 查看 [RELAY_GUIDE.md](RELAY_GUIDE.md) 了解技术细节

## 📄 许可证

LiteDesk 使用 MIT 许可证。详见 [LICENSE](LICENSE)。
