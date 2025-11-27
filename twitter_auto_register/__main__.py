# -*- coding: utf-8 -*-
"""
主程序入口
可以通过 python -m twitter_auto_register 运行
"""
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'twitter_register.log', encoding='utf-8')
    ]
)

from .twitter_register import TwitterRegister
from .service_interface import MockServiceInterface, HTTPServiceInterface

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("Twitter/X 自动注册系统启动")
    logger.info("=" * 80)
    
    # 选择服务接口
    # 方式1: 使用模拟服务（用于测试）
    service = MockServiceInterface()
    
    # 方式2: 使用HTTP服务（生产环境）
    # service = HTTPServiceInterface(
    #     base_url='http://your-service-api.com',
    #     api_key='your-api-key'
    # )
    
    # 创建注册器
    register = TwitterRegister(service)
    
    try:
        # 执行注册
        result = register.register()
        
        # 输出结果
        if result['success']:
            logger.info("\n" + "=" * 80)
            logger.info("注册成功！")
            logger.info(f"邮箱: {result['email']}")
            logger.info(f"密码: {result['password']}")
            logger.info(f"用户名: {result['username']}")
            logger.info("=" * 80)
            
            # 可以选择保持浏览器打开以便查看
            input("\n按回车键关闭浏览器...")
        else:
            logger.error("\n" + "=" * 80)
            logger.error("注册失败！")
            logger.error(f"错误: {result.get('error', '未知错误')}")
            logger.error("=" * 80)
            
            input("\n按回车键关闭...")
    
    finally:
        # 清理资源
        register.close()


if __name__ == '__main__':
    main()

