# -*- coding: utf-8 -*-
"""
外部服务通信模块
包含服务接口定义、HTTP客户端实现、Flask服务端实现
"""
import json
import time
import logging
import random
from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ==================== 服务接口定义 ====================

class ServiceInterface(ABC):
    """服务接口基类"""
    
    @abstractmethod
    def report_status(self, status: str, message: str = "", data: Optional[Dict] = None) -> None:
        """
        上报当前状态给外部服务
        
        Args:
            status: 状态标识
                - 'started': 注册开始
                - 'visit_page': 访问页面
                - 'need_email': 需要邮箱和密码
                - 'filling_form': 填写表单中
                - 'need_captcha': 需要人机验证
                - 'captcha_solving': 正在解决验证
                - 'need_email_code': 需要邮箱验证码
                - 'setting_password': 设置密码中
                - 'setting_username': 设置用户名中
                - 'completed': 注册完成
                - 'failed': 注册失败
            message: 状态描述
            data: 额外数据（如当前页面URL、错误信息等）
        """
        pass
    
    @abstractmethod
    def request_email(self) -> Tuple[str, str]:
        """
        请求邮箱和密码
        
        Returns:
            Tuple[str, str]: (邮箱地址, 密码)
        """
        pass
    
    @abstractmethod
    def request_captcha_solution(self, captcha_type: str, site_key: str, page_url: str) -> Dict:
        """
        请求人机验证解决方案
        
        Args:
            captcha_type: 验证码类型（如 'funcaptcha'）
            site_key: 站点密钥
            page_url: 页面URL
            
        Returns:
            Dict: 包含验证方式和token的字典
                {
                    'method': 'manual' | 'api',
                    'token': str (如果是API方式),
                    'status': 'pending' | 'solved' | 'failed'
                }
        """
        pass
    
    @abstractmethod
    def request_email_code(self, email: str) -> str:
        """
        请求邮箱验证码
        
        Args:
            email: 邮箱地址
            
        Returns:
            str: 6位验证码
        """
        pass
    
    @abstractmethod
    def wait_for_captcha_solution(self, task_id: str, timeout: int = 300) -> Optional[str]:
        """
        等待验证码解决（用于异步打码平台）
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            Optional[str]: 验证token，失败返回None
        """
        pass


# ==================== HTTP客户端实现 ====================

class HTTPServiceInterface(ServiceInterface):
    """
    基于HTTP的服务接口实现（客户端）
    可以通过HTTP请求与外部服务通信
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化HTTP服务接口
        
        Args:
            base_url: 服务基础URL
            api_key: API密钥（可选）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def _post_request(self, endpoint: str, data: Dict) -> Dict:
        """发送POST请求"""
        import requests
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP请求失败: {endpoint}, 错误: {str(e)}")
            raise
    
    def report_status(self, status: str, message: str = "", data: Optional[Dict] = None) -> None:
        """上报状态给外部服务"""
        try:
            payload = {
                'status': status,
                'message': message,
                'timestamp': time.time()
            }
            if data:
                payload['data'] = data
            
            self._post_request('api/status/report', payload)
            logger.info(f"状态已上报: {status} - {message}")
        except Exception as e:
            logger.warning(f"状态上报失败: {str(e)}")
            # 状态上报失败不应该中断流程
    
    def _get_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """发送GET请求"""
        import requests
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP请求失败: {endpoint}, 错误: {str(e)}")
            raise
    
    def request_email(self) -> Tuple[str, str]:
        """请求邮箱和密码"""
        logger.info("正在请求邮箱和密码...")
        response = self._post_request('/api/email/request', {})
        
        email = response.get('email')
        password = response.get('password')
        
        if not email or not password:
            raise ValueError("服务返回的邮箱或密码为空")
        
        logger.info(f"成功获取邮箱: {email}")
        return email, password
    
    def request_captcha_solution(self, captcha_type: str, site_key: str, page_url: str) -> Dict:
        """请求人机验证解决方案"""
        logger.info(f"正在请求验证码解决方案: {captcha_type}")
        
        response = self._post_request('/api/captcha/request', {
            'type': captcha_type,
            'site_key': site_key,
            'page_url': page_url
        })
        
        return {
            'method': response.get('method', 'manual'),
            'task_id': response.get('task_id'),
            'token': response.get('token'),
            'status': response.get('status', 'pending')
        }
    
    def request_email_code(self, email: str) -> str:
        """请求邮箱验证码"""
        logger.info(f"正在请求邮箱验证码: {email}")
        
        response = self._post_request('/api/email/code', {
            'email': email
        })
        
        code = response.get('code')
        if not code:
            raise ValueError("服务返回的验证码为空")
        
        logger.info(f"成功获取验证码: {code}")
        return code
    
    def wait_for_captcha_solution(self, task_id: str, timeout: int = 300) -> Optional[str]:
        """等待验证码解决"""
        logger.info(f"等待验证码解决: task_id={task_id}")
        
        start_time = time.time()
        check_interval = 5  # 每5秒检查一次
        
        while time.time() - start_time < timeout:
            try:
                response = self._get_request(f'/api/captcha/status/{task_id}')
                
                status = response.get('status')
                if status == 'solved':
                    token = response.get('token')
                    logger.info(f"验证码已解决: {token}")
                    return token
                elif status == 'failed':
                    logger.error("验证码解决失败")
                    return None
                
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"检查验证码状态失败: {str(e)}")
                time.sleep(check_interval)
        
        logger.error(f"等待验证码超时: {timeout}秒")
        return None


# ==================== Mock客户端实现 ====================

class MockServiceInterface(ServiceInterface):
    """
    模拟服务接口（用于测试和演示）
    """
    
    def __init__(self):
        """初始化模拟服务"""
        self.mock_email = "test_user_{}@example.com".format(int(time.time()))
        self.mock_password = "TestPassword123!"
        self.mock_code = "123456"
    
    def report_status(self, status: str, message: str = "", data: Optional[Dict] = None) -> None:
        """上报状态（模拟）"""
        logger.info(f"[模拟状态] {status}: {message}")
        if data:
            logger.debug(f"[模拟数据] {data}")
    
    def request_email(self) -> Tuple[str, str]:
        """返回模拟的邮箱和密码"""
        logger.info(f"[模拟] 获取邮箱: {self.mock_email}")
        return self.mock_email, self.mock_password
    
    def request_captcha_solution(self, captcha_type: str, site_key: str, page_url: str) -> Dict:
        """返回模拟的验证码解决方案"""
        logger.info(f"[模拟] 请求验证码解决: {captcha_type}")
        return {
            'method': 'manual',  # 默认使用人工验证
            'task_id': 'mock_task_123',
            'token': None,
            'status': 'pending'
        }
    
    def request_email_code(self, email: str) -> str:
        """返回模拟的验证码"""
        logger.info(f"[模拟] 获取验证码: {self.mock_code}")
        return self.mock_code
    
    def wait_for_captcha_solution(self, task_id: str, timeout: int = 300) -> Optional[str]:
        """模拟等待验证码解决"""
        logger.info(f"[模拟] 等待人工验证，请在浏览器中手动完成验证...")
        logger.info(f"等待最多 {timeout} 秒")
        return None  # 返回None表示需要人工处理


# ==================== 状态上报包装器 ====================

class StatusReportWrapper(ServiceInterface):
    """
    状态上报包装器
    无论使用哪种服务（Mock或HTTP），都能向外部API上报状态
    """
    
    def __init__(self, base_service: ServiceInterface, status_url: str, api_key: Optional[str] = None):
        """
        初始化状态上报包装器
        
        Args:
            base_service: 基础服务（Mock或HTTP）
            status_url: 状态上报API地址
            api_key: API密钥
        """
        self.base_service = base_service
        self.status_url = status_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def report_status(self, status: str, message: str = "", data: Optional[Dict] = None) -> None:
        """上报状态到外部API"""
        # 先调用基础服务的上报
        self.base_service.report_status(status, message, data)
        
        # 再向独立的状态API上报
        try:
            import requests
            
            payload = {
                'status': status,
                'message': message,
                'timestamp': time.time()
            }
            if data:
                payload['data'] = data
            
            url = f"{self.status_url}/api/status/report"
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            logger.debug(f"状态已上报到外部API: {status}")
        except Exception as e:
            logger.warning(f"状态上报失败 ({self.status_url}): {str(e)}")
            # 上报失败不影响主流程
    
    def request_email(self) -> Tuple[str, str]:
        """委托给基础服务"""
        return self.base_service.request_email()
    
    def request_captcha_solution(self, captcha_type: str, site_key: str, page_url: str) -> Dict:
        """委托给基础服务"""
        return self.base_service.request_captcha_solution(captcha_type, site_key, page_url)
    
    def request_email_code(self, email: str) -> str:
        """委托给基础服务"""
        return self.base_service.request_email_code(email)
    
    def wait_for_captcha_solution(self, task_id: str, timeout: int = 300) -> Optional[str]:
        """委托给基础服务"""
        return self.base_service.wait_for_captcha_solution(task_id, timeout)


# ==================== 使用说明 ====================
"""
此模块提供三种服务实现：

1. HTTPServiceInterface: 连接到外部HTTP服务（你自己的后端API）
   - 适用于有独立后端服务的场景
   - 通过HTTP请求获取邮箱、密码、验证码等

2. MockServiceInterface: 模拟服务（用于测试）
   - 适用于开发和测试
   - 返回模拟数据，需要手动完成人机验证

3. StatusReportWrapper: 状态上报包装器
   - 包装任何服务，添加实时状态上报功能
   - 让外部客户端能实时监控注册进度

使用示例：
    # 方式1: Mock服务 + 状态上报
    base = MockServiceInterface()
    service = StatusReportWrapper(
        base_service=base,
        status_url='http://your-monitor.com',
        api_key='your-key'
    )
    
    # 方式2: HTTP服务（已包含状态上报）
    service = HTTPServiceInterface(
        base_url='http://your-api.com',
        api_key='your-key'
    )
"""
