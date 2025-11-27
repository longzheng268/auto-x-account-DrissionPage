# 快速启动指南

## 🚀 一键启动（推荐）

### 完整流程（3个终端）

#### **终端1：启动外部服务**
```powershell
.\start_service.ps1
```
功能：提供邮箱、密码、验证码

#### **终端2：启动注册系统**
```powershell
.\start_register.ps1
```
功能：等待触发，执行自动注册

#### **终端3：触发注册**
```powershell
.\trigger_register.ps1
```
功能：发送启动信号

---

## 📋 脚本说明

### 主要脚本

| 脚本 | 功能 | 用途 |
|------|------|------|
| `start_service.ps1` | 启动外部服务 | 提供数据API |
| `start_register.ps1` | 启动注册系统 | 执行注册流程 |
| `trigger_register.ps1` | 触发注册 | 发送启动信号 |

### 辅助脚本

| 脚本 | 功能 | 用途 |
|------|------|------|
| `check_status.ps1` | 检查状态 | 查看当前进度 |
| `reset_status.ps1` | 重置状态 | 开始新任务 |
| `quick_start.ps1` | 快速启动 | 查看完整说明 |

---

## 🔄 完整流程

```
1. 终端1: .\start_service.ps1
   → 外部服务启动在 http://localhost:8989
   ↓
2. 终端2: .\start_register.ps1
   → 系统等待准备信号
   → 每3秒轮询 /api/register/ready
   ↓
3. 终端3: .\trigger_register.ps1
   → 发送 POST /api/register/trigger
   ↓
4. 终端2: 开始注册
   → 浏览器自动启动
   → 执行注册流程
   → 实时上报状态到外部服务
```

---

## 📊 API流程

```
外部服务 (8989)                     注册系统
     |                                  |
     |  GET /api/register/ready         |
     |  ← {"ready": false} ─────────────|
     |                                  | (等待3秒)
     |  GET /api/register/ready         |
     |  ← {"ready": false} ─────────────|
     |                                  |
[触发] POST /api/register/trigger     |
     |                                  |
     |  GET /api/register/ready         |
     |  ← {"ready": true} ──────────────|
     |                                  | (开始注册)
     |                                  |
     |  POST /api/status/report         |
     |  {"status": "started"} ←─────────|
     |                                  |
     |  POST /api/status/report         |
     |  {"status": "need_email"} ←──────|
     |                                  |
     |  POST /api/email/request         |
     |  → {"email": "...", "password"} ─|
     |                                  |
     |  POST /api/status/report         |
     |  {"status": "need_captcha"} ←────|
     |                                  |
     |  ... 继续流程 ...                |
```

---

## 💡 使用技巧

### 1. 检查状态
```powershell
.\check_status.ps1
```

输出：
```
1. 检查外部服务...
   ✓ 外部服务正在运行
2. 检查准备状态...
   ✓ 已准备就绪，可以注册
3. 当前注册状态...
   状态: need_email
   消息: 需要邮箱和密码
```

### 2. 重置状态（开始新任务）
```powershell
.\reset_status.ps1
```

### 3. 查看完整说明
```powershell
.\quick_start.ps1
```

---

## ⚠️ 注意事项

1. **conda环境**：脚本会自动激活 `x-account` 环境
2. **端口占用**：确保 8989 端口未被占用
3. **保持运行**：外部服务需要持续运行
4. **手动验证**：人机验证需要手动完成

---

## 🎯 常见场景

### 场景1：第一次使用
```powershell
# 1. 查看说明
.\quick_start.ps1

# 2. 按提示打开3个终端，分别运行脚本
```

### 场景2：快速测试
```powershell
# 终端1
.\start_service.ps1

# 终端2
.\start_register.ps1

# 终端3（等终端2显示"等待准备就绪"后）
.\trigger_register.ps1
```

### 场景3：查看进度
```powershell
# 任意终端
.\check_status.ps1
```

### 场景4：重新开始
```powershell
# 重置状态
.\reset_status.ps1

# 触发新任务
.\trigger_register.ps1
```

---

## 📝 文件对应

| Python文件 | 说明 |
|-----------|------|
| `external_service.py` | 外部服务实现（Flask） |
| `run_register.py` | 注册系统主程序 |
| `twitter_auto_register/` | 注册核心模块 |

---

**快速上手，只需3个脚本！** 🎉

