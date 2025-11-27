# 外部服务状态API说明

## 🎯 新增：实时状态反馈

现在系统会在每个关键步骤向你的外部服务上报当前状态！

## 📡 状态上报API

### **POST /api/status/report**

系统会在每个关键步骤调用此API上报状态。

#### 请求格式

```json
{
    "status": "need_email",
    "message": "需要邮箱和密码",
    "timestamp": 1764226800.123,
    "data": {
        // 额外的上下文数据
    }
}
```

#### 响应格式

```json
{
    "received": true
}
```

## 📊 状态列表

### 1. **started** - 注册开始
```json
{
    "status": "started",
    "message": "注册流程启动",
    "timestamp": 1764226800.123
}
```

### 2. **visit_page** - 访问页面
```json
{
    "status": "visit_page",
    "message": "正在访问注册页面",
    "timestamp": 1764226805.456
}
```

### 3. **need_email** - 需要邮箱和密码 ⚡
```json
{
    "status": "need_email",
    "message": "需要邮箱和密码",
    "timestamp": 1764226810.789
}
```
**👉 收到此状态后，准备好邮箱和密码，系统马上会调用 `/api/email/request`**

### 4. **filling_form** - 填写表单中
```json
{
    "status": "filling_form",
    "message": "正在填写注册表单",
    "timestamp": 1764226815.012,
    "data": {
        "email": "test@example.com",
        "name": "Test User"
    }
}
```

### 5. **need_captcha** - 需要人机验证 ⚡
```json
{
    "status": "need_captcha",
    "message": "需要人机验证",
    "timestamp": 1764226820.345,
    "data": {
        "page_url": "https://x.com/i/flow/signup"
    }
}
```
**👉 收到此状态后，准备验证方式，系统马上会调用 `/api/captcha/request`**

### 6. **captcha_solving** - 正在解决验证
```json
{
    "status": "captcha_solving",
    "message": "正在处理人机验证",
    "timestamp": 1764226825.678
}
```

### 7. **need_email_code** - 需要邮箱验证码 ⚡
```json
{
    "status": "need_email_code",
    "message": "需要邮箱验证码",
    "timestamp": 1764226830.901,
    "data": {
        "email": "test@example.com"
    }
}
```
**👉 收到此状态后，从邮箱获取验证码，系统马上会调用 `/api/email/code`**

### 8. **setting_password** - 设置密码中
```json
{
    "status": "setting_password",
    "message": "正在设置密码",
    "timestamp": 1764226835.234
}
```

### 9. **setting_username** - 设置用户名中
```json
{
    "status": "setting_username",
    "message": "正在设置用户名",
    "timestamp": 1764226840.567
}
```

### 10. **completed** - 注册完成 ✅
```json
{
    "status": "completed",
    "message": "注册成功",
    "timestamp": 1764226845.890,
    "data": {
        "email": "test@example.com",
        "username": "testuser123"
    }
}
```

### 11. **failed** - 注册失败 ❌
```json
{
    "status": "failed",
    "message": "点击创建账号失败",
    "timestamp": 1764226850.123,
    "data": {
        "email": "test@example.com",
        "username": null
    }
}
```
明白了！你想让系统无论使用哪种模式，都能实时向外部API上报状态，方便客户端监控进度。我来添加一个独立的状态上报机制：

[7 tools called]

完美！✅ 已完成实时状态上报功能！

## 功能说明

现在系统会**持续向外部API上报状态**，无论使用Mock还是HTTP模式。你的外部客户端可以实时监控注册进度！

### 配置位置：`run_register.py` 第 44-48 行

```python
# ===== 状态上报配置 =====
ENABLE_STATUS_REPORT = True  # 是否启用状态上报
STATUS_REPORT_URL = 'http://localhost:8989'  # 状态上报地址
STATUS_API_KEY = '123456'  # API密钥
```

### 工作原理

1. **启用状态上报**：`ENABLE_STATUS_REPORT = True`
2. **系统会在每个关键步骤向你的API发送POST请求**：
   - `POST {STATUS_REPORT_URL}/api/status/report`
3. **上报的状态包括**：
   - `started` - 注册开始
   - `visit_page` - 访问注册页面
   - `need_email` - 需要邮箱
   - `filling_form` - 填写表单中
   - `need_captcha` - 需要人机验证
   - `captcha_solving` - 正在处理验证
   - `need_email_code` - 需要验证码
   - `setting_password` - 设置密码
   - `setting_username` - 设置用户名
   - `completed` - 注册成功 ✅
   - `failed` - 注册失败 ❌

### 请求格式

```json
{
    "status": "need_email",
    "message": "需要邮箱和密码",
    "timestamp": 1732699234.567,
    "data": {
        "page_url": "https://x.com/i/flow/signup"
    }
}
```

### 你的外部API只需要

```python
@app.route('/api/status/report', methods=['POST'])
def handle_status():
    data = request.json
    status = data['status']
    
    # 根据状态判断该准备什么数据
    if status == 'need_email':
        # 准备邮箱和密码
        prepare_email()
    elif status == 'need_email_code':
        # 准备验证码
        prepare_code()
    
    return {'received': True}
```

现在你的客户端能实时知道注册进度，随时准备下一步需要的数据！🎯
## 🔄 完整的API调用流程

```
1. POST /api/status/report
   { "status": "started" }
   ↓
2. POST /api/status/report
   { "status": "visit_page" }
   ↓
3. POST /api/status/report
   { "status": "need_email" }  ⚡
   ↓
4. POST /api/email/request  ← 你需要返回邮箱和密码
   ← { "email": "...", "password": "..." }
   ↓
5. POST /api/status/report
   { "status": "filling_form" }
   ↓
6. POST /api/status/report
   { "status": "need_captcha" }  ⚡
   ↓
7. POST /api/captcha/request  ← 你需要返回验证方式
   ← { "method": "manual" }
   ↓
8. POST /api/status/report
   { "status": "need_email_code" }  ⚡
   ↓
9. POST /api/email/code  ← 你需要返回验证码
   ← { "code": "123456" }
   ↓
10. POST /api/status/report
    { "status": "setting_password" }
    ↓
11. POST /api/status/report
    { "status": "setting_username" }
    ↓
12. POST /api/status/report
    { "status": "completed" }  ✅
```

## 💡 如何使用状态API

### 方式1：被动监听（推荐）

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/status/report', methods=['POST'])
def report_status():
    data = request.json
    status = data.get('status')
    message = data.get('message')
    
    print(f"[状态] {status}: {message}")
    
    # 根据状态做准备
    if status == 'need_email':
        print("  → 准备邮箱和密码...")
    elif status == 'need_captcha':
        print("  → 准备验证方式...")
    elif status == 'need_email_code':
        email = data.get('data', {}).get('email')
        print(f"  → 从 {email} 获取验证码...")
    elif status == 'completed':
        result = data.get('data')
        print(f"  ✅ 注册成功: {result}")
    elif status == 'failed':
        print(f"  ❌ 注册失败: {message}")
    
    return jsonify({'received': True})
```

### 方式2：主动查询

如果你的服务需要主动查询当前状态，可以保存最新状态：

```python
current_status = {
    'status': 'idle',
    'message': '',
    'timestamp': 0,
    'data': {}
}

@app.route('/api/status/report', methods=['POST'])
def report_status():
    global current_status
    current_status = request.json
    return jsonify({'received': True})

@app.route('/api/status/current', methods=['GET'])
def get_current_status():
    """获取当前状态"""
    return jsonify(current_status)
```

## 🚀 外部服务控制启动（推荐）

### **GET /api/register/ready** - 检查是否准备好启动

系统会轮询此API等待外部服务准备就绪。

#### 请求
```
GET /api/register/ready
```

#### 响应格式

**未准备好时：**
```json
{
    "ready": false,
    "message": "等待准备中..."
}
```

**准备好时：**
```json
{
    "ready": true,
    "message": "可以开始注册",
    "data": {
        // 可选：预先提供配置
        "browser_headless": false,
        "timeout": 300
    }
}
```

#### 使用流程

```
1. 启动 run_register.py
   ↓
2. 系统每3秒轮询 GET /api/register/ready
   ↓
3. 外部服务返回 {"ready": true}
   ↓
4. 系统开始注册流程
```

#### 示例实现

```python
from flask import Flask, jsonify

app = Flask(__name__)

# 全局状态
is_ready = False

@app.route('/api/register/ready', methods=['GET'])
def check_ready():
    """检查是否准备好启动"""
    global is_ready
    
    if is_ready:
        return jsonify({
            'ready': True,
            'message': '可以开始注册'
        })
    else:
        return jsonify({
            'ready': False,
            'message': '等待准备中...'
        })

@app.route('/api/register/trigger', methods=['POST'])
def trigger_register():
    """触发注册（由你的系统调用）"""
    global is_ready
    is_ready = True
    return jsonify({'success': True})
```

## 📋 完整API列表

现在你的外部服务需要提供 **5个API**：

1. ✅ **GET /api/register/ready** - 准备状态检查（可选，用于外部控制启动）
2. ✅ **POST /api/status/report** - 接收状态上报
3. ✅ **POST /api/email/request** - 提供邮箱和密码
4. ✅ **POST /api/captcha/request** - 提供验证方式
5. ✅ **POST /api/email/code** - 提供验证码

## 🎯 优势

- **实时监控**: 知道每一步的进展
- **提前准备**: 在需要数据前就收到通知
- **错误追踪**: 知道在哪一步失败了
- **数据记录**: 完整的流程日志
- **灵活控制**: 可以根据状态做决策

## ⚠️ 注意事项

1. **状态上报失败不会中断流程** - 如果你的 `/api/status/report` 返回错误，系统会记录警告但继续执行
2. **timestamp 是Unix时间戳** - 精确到毫秒
3. **data 字段可选** - 不是所有状态都有额外数据
4. **响应格式简单** - 只需返回 `{"received": true}` 即可

---

**现在你的外部服务可以完全掌控整个注册流程的状态！** 🎉

