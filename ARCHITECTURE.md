# LiteDesk Architecture and Workflow Diagrams

## Release Workflow

```
Developer                   GitHub                    End User
    |                          |                          |
    | 1. Create version tag    |                          |
    |------------------------->|                          |
    |   git push v1.0.0        |                          |
    |                          |                          |
    |                          | 2. Trigger GitHub Actions|
    |                          |    - Build Windows       |
    |                          |    - Build macOS         |
    |                          |    - Build Linux         |
    |                          |                          |
    |                          | 3. Create Release        |
    |                          |    - Upload executables  |
    |                          |    - Generate notes      |
    |                          |                          |
    |                          |                          | 4. Download
    |                          |<-------------------------|
    |                          |   from Releases page     |
    |                          |                          |
```

## Build Process

```
┌─────────────────────────────────────────────────────────────┐
│                     build_all.py                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
                ▼          ▼          ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Server  │ │  Client  │ │  Relay   │
        │   .spec  │ │   .spec  │ │   .spec  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │PyInstaller│
                    └─────┬────┘
                          │
                ┌─────────┼─────────┐
                │         │         │
                ▼         ▼         ▼
        ┌────────────┬──────────┬──────────┐
        │litedesk-   │litedesk- │litedesk- │
        │server      │client    │relay     │
        └────────────┴──────────┴──────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  release/        │
                │  {platform-arch}/│
                │    └─ .zip       │
                └──────────────────┘
```

## GitHub Actions Workflow

```
┌────────────────────────────────────────────────────────────┐
│              Push tag v*.*.* to GitHub                     │
└───────────────────────┬────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│  Windows   │  │   macOS    │  │   Linux    │
│   Runner   │  │   Runner   │  │   Runner   │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │                │                │
       │ Setup Python   │ Setup Python   │ Setup Python
       │ Install deps   │ Install deps   │ Install deps
       │ Build all      │ Build all      │ Build all
       │                │                │
       ▼                ▼                ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│  Upload    │  │  Upload    │  │  Upload    │
│  Artifact  │  │  Artifact  │  │  Artifact  │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                ┌────────────┐
                │  Create    │
                │  Release   │
                │  Job       │
                └──────┬─────┘
                       │
                       │ Download all artifacts
                       │ Create GitHub Release
                       │ Upload to release
                       │
                       ▼
                ┌────────────┐
                │  Release   │
                │  Published │
                └────────────┘
```

## Connection Modes

### Direct Connection (LAN)

```
┌────────────┐                          ┌────────────┐
│  Client    │                          │  Server    │
│            │                          │            │
│  User      │  1. Connect request     │  Waiting   │
│  enters IP │─────────────────────────>│  on :9876  │
│            │                          │            │
│            │  2. TCP connection       │            │
│            │<────────────────────────>│            │
│            │                          │            │
│  Display   │  3. Screen frames        │  Capture   │
│  received  │<─────────────────────────│  screen    │
│  frames    │                          │            │
│            │  4. Mouse/Keyboard       │  Control   │
│            │─────────────────────────>│  input     │
│            │                          │            │
└────────────┘                          └────────────┘
```

### Relay Mode (NAT Traversal)

```
Client (NAT)            Relay Server (VPS)         Server (NAT)
    │                          │                         │
    │  1. Register            │                         │
    │  (peer_id, type)        │                         │
    ├────────────────────────>│                         │
    │                          │  1. Register            │
    │                          │<────────────────────────┤
    │                          │  (peer_id, type)        │
    │                          │                         │
    │  2. List servers         │                         │
    ├────────────────────────>│                         │
    │<─────────────────────────┤                         │
    │  [server list]           │                         │
    │                          │                         │
    │  3. Request connection   │                         │
    ├────────────────────────>│                         │
    │                          │  Notify request         │
    │                          ├────────────────────────>│
    │                          │                         │
    │  4. Exchange info        │  Exchange info          │
    │<─────────────────────────┼────────────────────────>│
    │  (public_ip:port)        │  (public_ip:port)       │
    │                          │                         │
    │  5. Attempt direct P2P connection                 │
    │<──────────────────────────────────────────────────>│
    │  (requires port forwarding or UPnP)               │
    │                          │                         │
```

## Deployment Options

### Option 1: Download Executable (Recommended)

```
User
  │
  ▼
Download from GitHub Releases
  │
  ▼
Extract .zip
  │
  ▼
Run executable
  │
  ├─> litedesk-server (被控端)
  ├─> litedesk-client (控制端)
  └─> litedesk-relay  (中继服务器)
```

### Option 2: Build from Source

```
Developer
  │
  ▼
Clone repository
  │
  ▼
Install dependencies
  pip install -r requirements.txt
  │
  ▼
Run from Python
  │
  ├─> python server.py
  ├─> python client.py
  └─> python relay_server.py
```

### Option 3: Build Executables Locally

```
Developer
  │
  ▼
Clone repository
  │
  ▼
Install PyInstaller
  pip install pyinstaller
  │
  ▼
Build all
  python build_all.py
  │
  ▼
Executables in release/
  │
  └─> {platform-arch}/
      ├─> litedesk-server
      ├─> litedesk-client
      └─> litedesk-relay
```

## VPS Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    VPS (Public IP)                         │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │            litedesk-relay                         │    │
│  │          Listening on :8877                       │    │
│  └────────────────┬─────────────────────────────────┘    │
│                   │                                        │
└───────────────────┼────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Client 1 │  │ Client 2 │  │ Server 1 │
│  (NAT)   │  │  (NAT)   │  │  (NAT)   │
└──────────┘  └──────────┘  └──────────┘

Deployment Options:
1. Direct executable: ./litedesk-relay --port 8877
2. Systemd service: systemctl start litedesk-relay
3. Docker: docker run -p 8877:8877 litedesk-relay
```

## Package Contents

```
litedesk-{platform-arch}.zip
│
├── litedesk-server          # Server executable (被控端)
├── litedesk-client          # Client executable (控制端)
├── litedesk-relay           # Relay server executable (中继)
├── README.md                # Documentation
├── LICENSE                  # MIT License
├── RELAY_GUIDE.md           # Relay server guide
└── vps.ini.example          # Configuration example
```

## Code Structure

```
litedesk/
├── server.py                # Server application
├── client.py                # Client application
├── relay_server.py          # Relay server
├── network.py               # Network protocol
├── screen_capture.py        # Screen capture
├── input_control.py         # Input control
├── platform_utils.py        # Platform utilities
│
├── litedesk_server.spec     # PyInstaller config (server)
├── litedesk_client.spec     # PyInstaller config (client)
├── litedesk_relay.spec      # PyInstaller config (relay)
│
├── build_all.py             # Build script
├── release.py               # Release helper
│
├── .github/
│   └── workflows/
│       ├── build-release.yml    # Release workflow
│       └── build-test.yml       # Test workflow
│
└── docs/
    ├── README.md
    ├── BUILD.md
    ├── VPS_DEPLOY.md
    ├── RELEASE_CHECKLIST.md
    └── QUICKSTART.md
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│           LiteDesk Application              │
├─────────────────────────────────────────────┤
│  GUI Layer        │  PyQt5                  │
├─────────────────────────────────────────────┤
│  Screen Capture   │  mss                    │
├─────────────────────────────────────────────┤
│  Input Control    │  pynput                 │
├─────────────────────────────────────────────┤
│  Image Processing │  Pillow (PIL)           │
├─────────────────────────────────────────────┤
│  Network          │  socket, struct, json   │
├─────────────────────────────────────────────┤
│  Build Tool       │  PyInstaller            │
├─────────────────────────────────────────────┤
│  CI/CD            │  GitHub Actions         │
└─────────────────────────────────────────────┘
```

## Security Considerations

```
Current State (Demo):
┌─────────────┐              ┌─────────────┐
│   Client    │─────────────>│   Server    │
└─────────────┘              └─────────────┘
     No encryption
     No authentication
     
Recommended for Production:
┌─────────────┐              ┌─────────────┐
│   Client    │──────────────│   Server    │
│             │  TLS/SSL     │             │
│  ┌───────┐  │  Password    │  ┌───────┐  │
│  │ Auth  │  │  Session     │  │ Auth  │  │
│  │ Token │  │  Timeout     │  │ Token │  │
│  └───────┘  │              │  └───────┘  │
└─────────────┘              └─────────────┘
```

## Performance Optimization

```
Screen Capture              Network Transfer           Display
     │                            │                        │
     ▼                            ▼                        ▼
┌──────────┐  JPEG      ┌──────────┐  TCP      ┌──────────┐
│  Capture │ Compression│  Socket  │ Protocol  │  Decode  │
│  @ 30fps │───────────>│ Transfer │──────────>│  & Show  │
└──────────┘            └──────────┘           └──────────┘
     │                            │                        │
     │  Quality: 50-95%           │  Buffer: 64KB          │
     │  Format: JPEG              │  Header: 12 bytes      │
     │  Resolution: Variable      │  Compression: Optional │
```

---

This document provides visual representation of LiteDesk's architecture, workflows, and processes.
For more details, see the respective documentation files.
