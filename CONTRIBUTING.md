# 如何为 LiteDesk 贡献代码

感谢您对 LiteDesk 项目的关注！我们欢迎所有形式的贡献。

## 贡献方式

1. **报告 Bug**: 在 GitHub Issues 中提交详细的 bug 报告
2. **建议新功能**: 在 Issues 中描述您希望添加的功能
3. **改进文档**: 修复文档中的错误或添加示例
4. **提交代码**: 修复 bug 或实现新功能

## 开发环境设置

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/YOUR_USERNAME/litedesk.git
cd litedesk

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python3 test_litedesk.py
```

## 提交 Pull Request 流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 保持代码简洁易懂

3. **测试您的更改**
   ```bash
   python3 test_litedesk.py
   python3 server.py  # 手动测试
   python3 client.py  # 手动测试
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "简短描述您的更改"
   ```

5. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 详细描述您的更改
   - 关联相关的 Issues

## 代码风格指南

### Python 代码规范

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 类名使用 CamelCase
- 函数名使用 snake_case
- 添加适当的文档字符串

**示例：**
```python
class MyClass:
    """类的简短描述"""
    
    def my_method(self, param):
        """
        方法的简短描述
        
        Args:
            param: 参数描述
            
        Returns:
            返回值描述
        """
        pass
```

### 提交信息规范

使用清晰的提交信息：

```
类型: 简短描述 (50 字符以内)

详细描述您的更改（如果需要）
- 要点 1
- 要点 2

Fixes #123  # 如果修复了某个 issue
```

**类型示例：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或辅助工具的变动

## 功能开发建议

### 潜在的改进方向

1. **安全性增强**
   - 添加密码保护
   - 实现 SSL/TLS 加密
   - 添加连接白名单

2. **性能优化**
   - 实现更高效的视频编码（如 H.264）
   - 添加增量更新（只传输变化区域）
   - 多线程优化

3. **功能扩展**
   - 文件传输
   - 剪贴板同步
   - 音频传输
   - 多显示器支持
   - 聊天功能

4. **用户体验**
   - 添加系统托盘图标
   - 实现自动重连
   - 添加连接历史
   - 多语言支持

5. **跨平台改进**
   - 优化 Windows 性能
   - 改进 macOS 权限处理
   - 支持 Wayland (Linux)

## 项目结构

```
litedesk/
├── screen_capture.py    # 屏幕捕获模块
├── input_control.py     # 输入控制模块
├── network.py           # 网络通信模块
├── server.py            # 服务端应用
├── client.py            # 客户端应用
├── test_litedesk.py     # 测试脚本
├── requirements.txt     # 依赖列表
├── setup.py             # 安装配置
└── README.md            # 项目文档
```

## 测试要求

在提交 PR 之前：

1. 确保所有现有测试通过
2. 为新功能添加测试
3. 在多个平台测试（如果可能）
4. 测试边界情况和错误处理

## 文档要求

- 更新 README.md（如果添加新功能）
- 添加代码注释和文档字符串
- 更新 TROUBLESHOOTING.md（如果相关）
- 提供使用示例（如果适用）

## 问题报告模板

提交 bug 报告时，请包含：

```markdown
### 描述
简要描述问题

### 复现步骤
1. 第一步
2. 第二步
3. ...

### 期望行为
描述您期望发生什么

### 实际行为
描述实际发生了什么

### 环境信息
- 操作系统: 
- Python 版本: 
- LiteDesk 版本: 
- 其他相关信息: 

### 错误日志
```
粘贴错误信息
```
```

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 关注项目目标
- 保持友好和专业

## 获取帮助

如有疑问，请：
1. 查看现有 Issues 和 PR
2. 阅读项目文档
3. 在 Issues 中提问

再次感谢您的贡献！🎉
