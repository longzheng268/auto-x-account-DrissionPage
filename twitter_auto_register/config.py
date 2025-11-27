# -*- coding: utf-8 -*-
"""
Twitter自动注册系统配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 资源文件路径
RESOURCES_DIR = BASE_DIR / "twitter_auto_register" / "resources" / "images"
CREATE_ACCOUNT_BTN_IMG = RESOURCES_DIR / "create_account_btn.png"
VERIFIER_BTN_IMG = RESOURCES_DIR / "verifier_btn.png"

# 项目内置浏览器路径（便携版）
PROJECT_CHROMIUM_PATH = BASE_DIR / "twitter_auto_register" / "chrome-win" / "chrome.exe"
PROJECT_BROWSER_DATA_DIR = BASE_DIR / "browser_data"

# Twitter URLs
TWITTER_SIGNUP_URL = "https://x.com/i/flow/signup"

# 图像匹配配置
IMAGE_MATCH_THRESHOLD = 0.8  # 图像匹配阈值
SCREENSHOT_TEMP_DIR = BASE_DIR / "temp" / "screenshots"

# 等待时间配置（秒）
TIMEOUT_SHORT = 5
TIMEOUT_MEDIUM = 10
TIMEOUT_LONG = 30
TIMEOUT_CAPTCHA = 300  # 人机验证最长等待时间

# 服务通信配置
SERVICE_REQUEST_TIMEOUT = 30  # 服务请求超时时间
SERVICE_MAX_RETRIES = 3  # 最大重试次数

# 注册配置
MAX_USERNAME_RETRIES = 10  # 用户名设置最大重试次数
RANDOM_INTERESTS_COUNT = 3  # 随机选择兴趣标签数量

# 日志配置
LOG_DIR = BASE_DIR / "logs"
LOG_LEVEL = "INFO"

# 确保必要的目录存在
SCREENSHOT_TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

