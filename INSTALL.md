# 安装指南

## 环境要求

- Python 3.6 或更高版本
- Windows / Linux / macOS
- Chrome 或 Edge 浏览器

## 安装步骤

### 1. 安装依赖

```bash
# 安装 Twitter 注册系统依赖
pip install -r twitter_auto_register/requirements.txt
```

或者分别安装：

```bash
# 核心依赖
pip install DrissionPage>=4.0.0

# 图像识别依赖（用于图像匹配功能）
pip install opencv-python numpy

# HTTP 请求
pip install requests
```

### 2. 准备图像模板

图像模板已经包含在项目中，位于：
- `twitter_auto_register/resources/images/create_account_btn.png`
- `twitter_auto_register/resources/images/verifier_btn.png`

如果需要更新图像模板：
1. 访问 Twitter/X 注册页面
2. 截取「创建账号」和「验证」按钮的图片
3. 替换对应的 PNG 文件

### 3. 配置服务接口

系统需要外部服务提供：
- 邮箱和密码
- 邮箱验证码
- 人机验证解决方案（可选）

你可以选择以下方式之一：

#### 方式 A: 使用模拟服务（测试）

直接使用内置的 `MockServiceInterface`，无需额外配置。

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

service = MockServiceInterface()
register = TwitterRegister(service)
```

#### 方式 B: 使用 HTTP 服务（生产）

配置你的服务 API：

```python
from twitter_auto_register import HTTPServiceInterface

service = HTTPServiceInterface(
    base_url='http://your-api.com',
    api_key='your-api-key'
)
```

你的 API 需要实现以下端点：

- `POST /api/email/request` - 返回邮箱和密码
- `POST /api/captcha/request` - 请求验证码解决方案
- `POST /api/email/code` - 获取邮箱验证码
- `GET /api/captcha/status/{task_id}` - 查询验证码状态

#### 方式 C: 自定义服务

继承 `ServiceInterface` 实现自己的服务：

```python
from twitter_auto_register import ServiceInterface

class MyService(ServiceInterface):
    def request_email(self):
        # 你的实现
        return email, password
    
    def request_captcha_solution(self, captcha_type, site_key, page_url):
        # 你的实现
        return {...}
    
    def request_email_code(self, email):
        # 你的实现
        return code
    
    def wait_for_captcha_solution(self, task_id, timeout):
        # 你的实现（可选）
        return token
```

## 快速测试

### 方法 1: 运行快速启动脚本

```bash
python run_register.py
```

### 方法 2: 作为模块运行

```bash
python -m twitter_auto_register
```

### 方法 3: 运行示例代码

```bash
python examples/basic_usage.py
```

## 验证安装

运行以下代码验证安装是否成功：

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

print("✓ Twitter 自动注册系统安装成功！")
print("✓ 所有模块导入正常")

# 测试图像匹配功能
try:
    import cv2
    import numpy as np
    print("✓ 图像匹配功能可用")
except ImportError:
    print("⚠ 图像匹配功能不可用（需要安装 opencv-python 和 numpy）")
```

## 常见问题

### 问题 1: 找不到浏览器

**错误**: `Browser not found` 或类似错误

**解决方案**:
- 确保已安装 Chrome 或 Edge 浏览器
- DrissionPage 会自动寻找浏览器，也可以手动指定路径

```python
from DrissionPage import ChromiumOptions

options = ChromiumOptions()
options.set_browser_path('C:/Program Files/Google/Chrome/Application/chrome.exe')
```

### 问题 2: opencv-python 安装失败

**解决方案**:
```bash
# 使用国内镜像源
pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 opencv-python-headless (无 GUI 版本)
pip install opencv-python-headless
```

### 问题 3: 图像匹配失败

**解决方案**:
- 检查图像模板是否存在
- 更新图像模板（截取最新的按钮图片）
- 调整匹配阈值（修改 `config.py` 中的 `IMAGE_MATCH_THRESHOLD`）

### 问题 4: 编码错误

**解决方案**:
```bash
# Windows 系统可能需要设置环境变量
set PYTHONIOENCODING=utf-8
```

## 目录结构检查

确保以下目录存在：

```
twitter_auto_register/
├── resources/images/    # 图像模板
├── logs/                # 日志文件
└── temp/screenshots/    # 临时截图
```

如果不存在，会自动创建。

## 下一步

阅读 [README_TWITTER_REGISTER.md](README_TWITTER_REGISTER.md) 了解详细的使用说明和 API 文档。

查看 `examples/` 目录中的示例代码学习更多用法。

