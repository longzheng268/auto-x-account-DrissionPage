# Twitter/X 自动注册系统

基于 DrissionPage 开发的 Twitter/X 账号自动注册系统。

## ✨ 特性

- 🚀 **基于 DrissionPage**: 充分利用 DrissionPage 的强大功能，无需 webdriver
- 🔄 **服务化设计**: 通过服务接口与外部邮箱、验证码服务解耦
- 🖼️ **图像识别备选**: 当常规方法无法定位元素时，使用图像匹配作为备选方案
- 🤖 **自动化流程**: 完整的注册流程自动化，从创建账号到设置用户名
- 🛡️ **人机验证支持**: 支持人工和API两种验证码解决方案
- 📦 **易于扩展**: 清晰的架构设计，方便二次开发

## 📋 注册流程

系统会自动完成以下步骤：

1. 访问 Twitter 首页建立浏览历史
2. 访问注册页面
3. 点击「创建账号」按钮
4. 切换到邮箱注册模式
5. 填写姓名、邮箱、生日信息
6. 处理人机验证（Arkose FunCaptcha）
   - 支持人工验证
   - 支持打码平台API（Capsolver、Yescaptcha等）
7. 输入邮箱验证码
8. 设置密码
9. 跳过头像上传
10. 设置用户名（自动重试直到可用）
11. 跳过可选步骤（通知权限、兴趣标签、推荐关注等）
12. 注册完成

## 🚀 快速开始

### 安装依赖

```bash
# 安装 Twitter 注册系统依赖
pip install -r twitter_auto_register/requirements.txt

# 或者手动安装核心依赖
pip install DrissionPage>=4.0.0 opencv-python numpy requests
```

### 基础使用

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

# 创建模拟服务（用于测试）
service = MockServiceInterface()

# 创建注册器
register = TwitterRegister(service)

try:
    # 执行注册
    result = register.register()
    
    if result['success']:
        print(f"注册成功！")
        print(f"邮箱: {result['email']}")
        print(f"用户名: {result['username']}")
    else:
        print(f"注册失败: {result['error']}")
finally:
    register.close()
```

### 使用 HTTP 服务

```python
from twitter_auto_register import TwitterRegister, HTTPServiceInterface

# 创建 HTTP 服务接口
service = HTTPServiceInterface(
    base_url='http://your-service-api.com',
    api_key='your-api-key'
)

register = TwitterRegister(service)
result = register.register()
```

### 命令行运行

```bash
# 直接运行
python -m twitter_auto_register

# 或运行示例
python examples/basic_usage.py
```

## 🔧 服务接口

系统通过 `ServiceInterface` 与外部服务通信，需要实现以下方法：

### 1. 请求邮箱和密码

```python
def request_email(self) -> Tuple[str, str]:
    """
    请求邮箱和密码
    Returns: (邮箱地址, 密码)
    """
    pass
```

### 2. 请求人机验证解决方案

```python
def request_captcha_solution(self, captcha_type: str, site_key: str, page_url: str) -> Dict:
    """
    请求人机验证解决方案
    Returns:
        {
            'method': 'manual' | 'api',  # 验证方式
            'task_id': str,              # 任务ID（API方式）
            'token': str,                # 验证token（如果已获取）
            'status': 'pending' | 'solved' | 'failed'
        }
    """
    pass
```

### 3. 请求邮箱验证码

```python
def request_email_code(self, email: str) -> str:
    """
    请求邮箱验证码
    Returns: 6位验证码
    """
    pass
```

### 4. 等待验证码解决（可选）

```python
def wait_for_captcha_solution(self, task_id: str, timeout: int = 300) -> Optional[str]:
    """
    等待验证码解决（用于异步打码平台）
    Returns: 验证token或None
    """
    pass
```

## 📖 自定义服务实现

参考 `examples/custom_service_example.py` 查看如何实现自己的服务接口：

```python
from twitter_auto_register import ServiceInterface

class MyCustomService(ServiceInterface):
    def request_email(self):
        # 从你的邮箱池获取邮箱
        return my_email_pool.get_new_email()
    
    def request_captcha_solution(self, captcha_type, site_key, page_url):
        # 调用你的打码平台
        task_id = my_captcha_service.create_task(...)
        return {'method': 'api', 'task_id': task_id, ...}
    
    def request_email_code(self, email):
        # 从邮箱中读取验证码
        return my_email_service.get_code(email)
    
    def wait_for_captcha_solution(self, task_id, timeout):
        # 等待打码结果
        return my_captcha_service.get_result(task_id)
```

## 🖼️ 图像匹配

当常规的元素定位失败时，系统会使用图像匹配作为备选方案。

图像模板位置：
- `twitter_auto_register/resources/images/create_account_btn.png` - 创建账号按钮
- `twitter_auto_register/resources/images/verifier_btn.png` - 验证按钮

你可以根据需要替换这些图像模板（建议使用中文环境下的按钮截图）。

## ⚙️ 配置说明

主要配置位于 `twitter_auto_register/config.py`：

```python
# 图像匹配阈值（0-1之间，越大越严格）
IMAGE_MATCH_THRESHOLD = 0.8

# 等待时间配置（秒）
TIMEOUT_SHORT = 5
TIMEOUT_MEDIUM = 10
TIMEOUT_LONG = 30
TIMEOUT_CAPTCHA = 300  # 人机验证最长等待时间

# 注册配置
MAX_USERNAME_RETRIES = 10  # 用户名设置最大重试次数
RANDOM_INTERESTS_COUNT = 3  # 随机选择兴趣标签数量
```

## 📁 项目结构

```
twitter_auto_register/
├── __init__.py              # 包初始化
├── __main__.py              # 主程序入口
├── config.py                # 配置文件
├── service_interface.py     # 服务接口定义
├── image_matcher.py         # 图像匹配模块
├── twitter_register.py      # 注册主流程
├── utils.py                 # 工具函数
├── requirements.txt         # 依赖列表
└── resources/               # 资源文件
    └── images/              # 图像模板
        ├── create_account_btn.png
        └── verifier_btn.png

examples/                    # 示例代码
├── basic_usage.py           # 基础使用示例
└── custom_service_example.py # 自定义服务示例
```

## 🎯 使用示例

### 示例1: 基础注册

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

service = MockServiceInterface()
register = TwitterRegister(service)

result = register.register()
print(result)
```

### 示例2: 批量注册

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

for i in range(5):
    print(f"注册第 {i+1} 个账号...")
    service = MockServiceInterface()
    register = TwitterRegister(service)
    
    result = register.register()
    if result['success']:
        print(f"✓ 账号 {i+1} 注册成功: {result['username']}")
    
    register.close()
```

### 示例3: 自定义浏览器配置

```python
from DrissionPage import ChromiumPage, ChromiumOptions
from twitter_auto_register import TwitterRegister, MockServiceInterface

# 配置浏览器
options = ChromiumOptions()
# options.headless(True)  # 无头模式
# options.set_proxy('http://proxy:port')  # 设置代理

page = ChromiumPage(options)

# 使用自定义页面
service = MockServiceInterface()
register = TwitterRegister(service, page=page)

result = register.register()
```

## 🔍 日志说明

系统会生成详细的日志，默认保存在 `logs/twitter_register.log`

日志级别可以在代码中配置：

```python
import logging

logging.basicConfig(level=logging.DEBUG)  # 调试模式
logging.basicConfig(level=logging.INFO)   # 正常模式
```

## ⚠️ 注意事项

1. **使用条款**: 请遵守 Twitter/X 的服务条款，本工具仅供学习和合法用途
2. **频率限制**: 建议控制注册频率，避免触发平台的反爬虫机制
3. **代理使用**: 批量注册时建议使用代理IP
4. **人机验证**: 首次使用时建议选择人工验证模式，熟悉流程后再接入打码平台
5. **环境要求**: 建议在非无头模式下运行，便于观察和调试
6. **图像模板**: 如果界面语言或样式变化，需要更新图像模板

## 🛠️ 故障排查

### 问题1: 无法找到元素

**解决方案**:
- 检查网页是否完全加载
- 增加等待时间 (修改 `config.py` 中的超时配置)
- 更新图像模板

### 问题2: 图像匹配失败

**解决方案**:
- 确保已安装 `opencv-python` 和 `numpy`
- 检查图像模板是否与实际按钮匹配
- 调整 `IMAGE_MATCH_THRESHOLD` 阈值

### 问题3: 验证码处理超时

**解决方案**:
- 增加 `TIMEOUT_CAPTCHA` 配置值
- 检查打码平台API是否正常
- 切换到人工验证模式

## 📄 许可证

本项目基于 DrissionPage 进行二次开发，使用时请遵守 DrissionPage 的许可条款。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看：
- DrissionPage 文档: https://drissionpage.cn
- 项目 Issues

---

**免责声明**: 本工具仅供学习和研究使用，使用者需自行承担使用本工具的风险和责任。

