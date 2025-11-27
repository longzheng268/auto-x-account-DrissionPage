# -*- coding: utf-8 -*-
"""
测试 undetected-chromedriver 是否正常工作
"""
import undetected_chromedriver as uc
from pathlib import Path

print("=" * 60)
print("测试 undetected-chromedriver")
print("=" * 60)

# 配置
options = uc.ChromeOptions()
options.add_argument('--lang=zh-CN')

# 使用项目 Chrome
project_chrome = Path(__file__).parent / "twitter_auto_register" / "chrome-win" / "chrome.exe"
if project_chrome.exists():
    options.binary_location = str(project_chrome)
    print(f"✓ 使用项目 Chrome: {project_chrome}")
else:
    print("⚠ 使用系统 Chrome")

print("\n正在启动浏览器...")
print("⚡ undetected-chromedriver 将:")
print("   1. 下载 ChromeDriver 144")
print("   2. 自动修补移除自动化特征")
print("   3. 绕过反爬虫检测")
print()

try:
    # 启动浏览器
    driver = uc.Chrome(
        options=options,
        use_subprocess=True,
        version_main=144,
        driver_executable_path=None
    )
    
    print("✓ 浏览器启动成功！")
    print(f"✓ 窗口标题: {driver.title}")
    
    # 访问测试页面
    print("\n正在访问 X.com...")
    driver.get('https://x.com')
    
    import time
    time.sleep(3)
    
    print(f"✓ 页面标题: {driver.title}")
    print("\n✅ 测试成功！undetected-chromedriver 工作正常")
    print("浏览器将保持打开 10 秒...")
    
    time.sleep(10)
    driver.quit()
    print("✓ 浏览器已关闭")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
