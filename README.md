# Twitter/X 自动注册系统 v2.0

**100% 基于 DrissionPage，简洁高效！**

## ✨ 特点

- ✅ **纯 DrissionPage** - 不造轮子，只用官方API
- ✅ **自动启动浏览器** - 无需手动操作
- ✅ **零额外依赖** - 只需一个 DrissionPage
- ✅ **一键运行** - 极简使用

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install DrissionPage
```

### 2. 运行

```bash
python run_register.py
```

**就这么简单！** DrissionPage 会自动：
- 查找浏览器（项目内置 Chromium > 系统浏览器）
- 启动浏览器
- 执行注册流程

## 📁 项目结构

```
DrissionPage/
├── twitter_auto_register/
│   ├── __init__.py
│   ├── twitter_register.py    ⭐ 核心注册器（纯DrissionPage）
│   ├── service_interface.py   - 服务接口
│   ├── config.py               - 配置
│   └── chrome-win/             - 项目内置浏览器
│
├── run_register.py             ⭐ 一键运行
└── README.md
```

## 💻 使用方法

### 基础使用

```python
from twitter_auto_register import TwitterRegister, MockServiceInterface

# 创建服务（模拟）
service = MockServiceInterface()

# 创建注册器（自动启动浏览器）
register = TwitterRegister(service)

# 执行注册
result = register.register()

if result['success']:
    print(f"✓ 注册成功！")
    print(f"邮箱: {result['email']}")
    print(f"用户名: @{result['username']}")
```

### 自定义配置

```python
# 指定浏览器路径
register = TwitterRegister(
    service=service,
    browser_path=r'D:\...\chrome.exe'
)

# 使用无痕模式
register = TwitterRegister(
    service=service,
    use_incognito=True
)
```

### 重用浏览器会话

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# 手动创建页面
options = ChromiumOptions(read_file=False)
options.set_browser_path('chrome.exe')
options.auto_port()
page = ChromiumPage(options)

# 重用页面对象
register = TwitterRegister(service, page=page)
result = register.register()
```

## 🎯 DrissionPage 功能展示

### 元素定位（100% 原生）

```python
# 文本定位
self.page.ele('text:创建账号')

# 标签+属性定位
self.page.ele('tag:input@type=email')

# 遍历元素
all_buttons = self.page.eles('tag:button')
```

### 等待功能（100% 原生）

```python
# 等待元素可见
ele = self.page.wait.ele_displayed('tag:input', timeout=30)

# 自动超时重试
btn = self.page.ele('tag:button', timeout=10)
```

### 元素操作（100% 原生）

```python
# 滚动到可见
ele.scroll.to_see()

# 输入、点击
ele.input('text')
ele.click()

# 下拉选择
select.select.by_value('value')
```

### 浏览器管理（100% 原生）

```python
# 自动启动
options.auto_port()
page = ChromiumPage(options)

# 无痕模式
options.incognito()

# 关闭
page.quit()
```

## ⚙️ 配置选项

在 `run_register.py` 中：

```python
# 使用无痕模式
USE_INCOGNITO = False

# 指定浏览器（None=自动检测）
BROWSER_PATH = None
```

## 📦 依赖

**只需一个！**

```txt
DrissionPage>=4.0.0
```

## 🔧 注册流程

1. ✅ 访问首页（建立历史）
2. ✅ 访问注册页面
3. ✅ 点击「创建账号」
4. ✅ 切换到邮箱注册
5. ✅ 填写表单（姓名、邮箱、生日）
6. ✅ 处理人机验证（手动/API）
7. ✅ 输入邮箱验证码
8. ✅ 设置密码
9. ✅ 跳过头像上传
10. ✅ 设置用户名
11. ✅ 跳过可选步骤
12. ✅ 完成注册

## 🎉 v2.0 改进

### 移除的"轮子"

- ❌ 图像匹配（opencv）
- ❌ 自定义工具函数
- ❌ 手动浏览器启动
- ❌ 所有 bat 脚本

### 使用的 DrissionPage 功能

- ✅ 自动浏览器管理
- ✅ 原生元素定位
- ✅ 内置等待机制
- ✅ 自动滚动和点击

## 📚 相关资源

- [DrissionPage 官网](https://www.drissionpage.cn/)
- [DrissionPage Gitee](https://gitee.com/g1879/DrissionPage)
- [DrissionPage GitHub](https://github.com/g1879/DrissionPage)

---

**极简、纯粹、强大！** 🚀
