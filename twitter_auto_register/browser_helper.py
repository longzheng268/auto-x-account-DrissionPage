# -*- coding: utf-8 -*-
"""
浏览器辅助工具
用于自动检测和配置浏览器
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_chromium_browser() -> Optional[Path]:
    """
    查找可用的 Chromium 浏览器
    按优先级返回第一个找到的浏览器路径
    
    Returns:
        Path: 浏览器可执行文件路径，未找到返回 None
    """
    from .config import BASE_DIR, PROJECT_CHROMIUM_PATH
    
    # 优先级列表
    possible_paths = [
        # 1. 项目内置浏览器（最高优先级）
        PROJECT_CHROMIUM_PATH,
        
        # 2. Windows 系统浏览器
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        Path(r"C:\Program Files\Chromium\Application\chrome.exe"),
        
        # 3. Linux 系统浏览器
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/snap/bin/chromium"),
        
        # 4. macOS 系统浏览器
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"找到浏览器: {path}")
            
            # 如果是项目内置浏览器，特别标注
            if path == PROJECT_CHROMIUM_PATH:
                logger.info("✓ 使用项目内置 Chromium（便携版）")
            
            return path
    
    logger.warning("未找到任何 Chromium 浏览器")
    return None


def get_browser_info(browser_path: Path) -> dict:
    """
    获取浏览器信息
    
    Args:
        browser_path: 浏览器路径
        
    Returns:
        dict: 浏览器信息
    """
    from .config import PROJECT_CHROMIUM_PATH
    
    info = {
        'path': str(browser_path),
        'exists': browser_path.exists(),
        'is_project_chromium': browser_path == PROJECT_CHROMIUM_PATH,
        'name': browser_path.stem
    }
    
    if 'msedge' in browser_path.name.lower():
        info['browser'] = 'Microsoft Edge'
    elif 'chrome' in browser_path.name.lower():
        if info['is_project_chromium']:
            info['browser'] = 'Chromium (Project)'
        else:
            info['browser'] = 'Google Chrome'
    elif 'brave' in browser_path.name.lower():
        info['browser'] = 'Brave Browser'
    elif 'chromium' in browser_path.name.lower():
        info['browser'] = 'Chromium'
    else:
        info['browser'] = 'Unknown Chromium'
    
    return info


def check_project_chromium() -> dict:
    """
    检查项目内置 Chromium 状态
    
    Returns:
        dict: 状态信息
    """
    from .config import PROJECT_CHROMIUM_PATH, PROJECT_BROWSER_DATA_DIR
    
    status = {
        'exists': PROJECT_CHROMIUM_PATH.exists(),
        'path': str(PROJECT_CHROMIUM_PATH),
        'data_dir': str(PROJECT_BROWSER_DATA_DIR),
        'data_dir_exists': PROJECT_BROWSER_DATA_DIR.exists(),
    }
    
    if status['exists']:
        try:
            size = PROJECT_CHROMIUM_PATH.stat().st_size
            status['size_mb'] = round(size / (1024 * 1024), 2)
        except:
            status['size_mb'] = None
    
    return status


def print_browser_status():
    """打印浏览器状态信息"""
    print("\n" + "=" * 60)
    print("浏览器检测状态")
    print("=" * 60)
    
    # 检查项目内置浏览器
    project_status = check_project_chromium()
    print("\n【项目内置 Chromium】")
    if project_status['exists']:
        print(f"  ✓ 已安装")
        print(f"  路径: {project_status['path']}")
        if project_status['size_mb']:
            print(f"  大小: {project_status['size_mb']} MB")
        print(f"  数据目录: {project_status['data_dir']}")
        print(f"  优势: 独立、便携、版本固定")
    else:
        print(f"  ✗ 未安装")
        print(f"  期望路径: {project_status['path']}")
        print(f"  提示: 可放置 Chromium 到此路径实现便携部署")
    
    # 检查系统浏览器
    print("\n【系统浏览器】")
    browser_path = find_chromium_browser()
    if browser_path:
        info = get_browser_info(browser_path)
        print(f"  ✓ 找到: {info['browser']}")
        print(f"  路径: {info['path']}")
    else:
        print(f"  ✗ 未找到系统 Chromium 浏览器")
    
    print("\n" + "=" * 60)
    print()


if __name__ == '__main__':
    # 命令行运行时显示浏览器状态
    print_browser_status()

