# -*- coding: utf-8 -*-
"""
浏览器辅助工具
Playwright 版本 - 简化版
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_chromium_browser() -> Optional[Path]:
    """
    查找可用的 Chromium 浏览器
    
    在 Playwright 模式下，我们优先使用 Playwright 管理的浏览器。
    此函数保留是为了兼容性，但现在主要返回 None，让 Playwright 自动处理。
    """
    return None


def get_browser_info(browser_path: Path) -> dict:
    """获取浏览器信息"""
    return {
        'path': str(browser_path) if browser_path else 'Playwright Managed',
        'exists': True,
        'browser': 'Chromium (Playwright)'
    }


def check_project_chromium() -> dict:
    """检查项目内置 Chromium 状态"""
    return {
        'exists': False,
        'path': 'Playwright Managed',
        'data_dir': 'Auto Managed',
        'data_dir_exists': True,
    }


def print_browser_status():
    """打印浏览器状态信息"""
    print("\n" + "=" * 60)
    print("浏览器检测状态 (Playwright Mode)")
    print("=" * 60)
    print("Playwright 将自动管理浏览器下载和更新。")
    print("无需手动配置本地浏览器路径。")
    print("\n" + "=" * 60)
    print()


if __name__ == '__main__':
    print_browser_status()

