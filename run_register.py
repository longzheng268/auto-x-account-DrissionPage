# -*- coding: utf-8 -*-
"""
Twitter/X 自动注册 - 快速启动脚本
一键运行：自动启动外部服务 + 注册系统
"""
import sys
import logging
import subprocess
from pathlib import Path

# 配置日志
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'twitter_register.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 不需要手动启动浏览器了，TwitterRegister 会自动处理


def save_account_info(result: dict, output_file: str = 'accounts_history.txt'):
    """
    保存账号信息到文件（追加模式，不覆盖）
    
    Args:
        result: 注册结果字典
        output_file: 输出文件路径
    """
    from datetime import datetime
    
    try:
        # 确保输出目录存在
        output_path = Path(__file__).parent / output_file
        
        # 追加模式写入
        with open(output_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("=" * 80 + "\n")
            f.write(f"注册时间: {timestamp}\n")
            
            if result['success']:
                f.write("状态: ✓ 注册成功\n")
                f.write(f"邮箱: {result.get('email', 'N/A')}\n")
                f.write(f"密码: {result.get('password', 'N/A')}\n")
                f.write(f"用户名: @{result.get('username', 'N/A')}\n")
            else:
                f.write("状态: ✗ 注册失败\n")
                f.write(f"邮箱: {result.get('email', 'N/A')}\n")
                f.write(f"密码: {result.get('password', 'N/A')}\n")
                f.write(f"错误信息: {result.get('error', '未知错误')}\n")
            
            f.write("=" * 80 + "\n\n")
        
        logger.info(f"✓ 账号信息已保存到: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存账号信息失败: {str(e)}")
        return False


def main():
    """主函数"""
    try:
        from twitter_auto_register import TwitterRegister, HTTPServiceInterface
        
        logger.info("=" * 80)
        logger.info("Twitter/X 自动注册系统 v3.0")
        logger.info("基于 Playwright + Stealth")
        logger.info("=" * 80)
        logger.info("")
        
        # ===== 配置选项 =====
        USE_INCOGNITO = False  # 是否使用无痕模式
        BROWSER_PATH = None  # 浏览器路径（None=自动检测）
        
        # ===== 状态上报配置 =====
        # 无论使用哪种服务模式，都可以向外部API实时上报状态
        ENABLE_STATUS_REPORT = True  # 是否启用状态上报
        STATUS_REPORT_URL = 'http://localhost:8989'  # 状态上报地址
        STATUS_API_KEY = '123456'  # API密钥
        
        # ===== 选择服务模式 =====
        # 模式1: 使用Mock服务（测试/演示）
        # 模式2: 连接到你的外部HTTP API
        USE_MOCK_SERVICE = False  # 改为False使用外部API
        
        if USE_MOCK_SERVICE:
            from twitter_auto_register import MockServiceInterface, StatusReportWrapper
            base_service = MockServiceInterface()
            logger.info("数据模式: Mock服务（测试模式）")
            logger.info("  - 邮箱/密码: 自动生成模拟数据")
            logger.info("  - 人机验证: 需要手动完成")
            logger.info("  - 邮箱验证码: 使用模拟验证码 123456")
        else:
            # 使用外部HTTP服务
            from twitter_auto_register import HTTPServiceInterface, StatusReportWrapper
            EXTERNAL_SERVICE_URL = 'http://localhost:8989'  # 你的服务地址
            EXTERNAL_API_KEY = '123456'  # 你的API密钥
            
            base_service = HTTPServiceInterface(
                base_url=EXTERNAL_SERVICE_URL,
                api_key=EXTERNAL_API_KEY
            )
            logger.info("数据模式: 外部HTTP服务")
            logger.info(f"  - 服务地址: {EXTERNAL_SERVICE_URL}")
            logger.info("  - 连接到你的后端API获取数据")
        
        # 添加状态上报功能
        if ENABLE_STATUS_REPORT:
            service = StatusReportWrapper(
                base_service=base_service,
                status_url=STATUS_REPORT_URL,
                api_key=STATUS_API_KEY
            )
            logger.info("")
            logger.info("✓ 实时状态上报已启用")
            logger.info(f"  → 上报地址: {STATUS_REPORT_URL}/api/status/report")
            logger.info("  → 外部客户端可实时监控注册进度")
        else:
            service = base_service
            logger.info("")
            logger.info("⚠️  状态上报已禁用")
        
        # 提示
        logger.info("")
        if USE_INCOGNITO:
            logger.info("⚠️  启用了无痕模式（不保存数据）")
        logger.info("⚠️  Playwright 会自动管理浏览器启动")
        logger.info("")
        logger.info("提示:")
        logger.info("1. 浏览器会自动启动（Playwright 管理）")
        logger.info("2. 人机验证可手动或API完成")
        logger.info("3. 整个流程约 5-10 分钟")
        logger.info("")
        logger.info("=" * 80)
        logger.info("")
        
        # 创建注册器（Playwright 实现）
        register = TwitterRegister(
            service=service,
            browser_path=BROWSER_PATH,
            use_incognito=USE_INCOGNITO
        )
        
        result = None
        try:
            # 执行注册
            result = register.register()
            
            # 显示结果
            logger.info("")
            logger.info("=" * 80)
            
            if result['success']:
                logger.info("✓ 注册成功！")
                logger.info("")
                logger.info(f"📧 邮箱: {result['email']}")
                logger.info(f"🔒 密码: {result['password']}")
                logger.info(f"👤 用户名: @{result['username']}")
                logger.info("")
                logger.info("请妥善保存以上信息！")
            else:
                logger.error("✗ 注册失败")
                logger.error(f"错误信息: {result.get('error', '未知错误')}")
            
            logger.info("=" * 80)
            logger.info("")
            
            # 保存账号信息到文件（追加模式）
            save_account_info(result)
            
            input("按回车键关闭浏览器并退出...")
        
        except Exception as register_error:
            # 如果注册过程中出现异常，也要记录
            logger.error(f"注册过程出现异常: {str(register_error)}", exc_info=True)
            
            if result is None:
                # 如果连result都没有，创建一个失败记录
                result = {
                    'success': False,
                    'email': 'N/A',
                    'password': 'N/A',
                    'error': f'注册异常: {str(register_error)}'
                }
            
            # 保存失败信息
            save_account_info(result)
            
            input("\n按回车键退出...")
            raise
        
        finally:
            # 清理资源
            register.close()
            logger.info("程序已退出")
    
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {str(e)}", exc_info=True)
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == '__main__':
    main()

