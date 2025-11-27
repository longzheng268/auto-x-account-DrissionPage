# -*- coding: utf-8 -*-
"""
Twitter/X 自动注册系统
100% 基于 DrissionPage，不造轮子
"""

from .twitter_register import TwitterRegister
from .service_interface import (
    ServiceInterface, 
    HTTPServiceInterface, 
    MockServiceInterface,
    StatusReportWrapper
)

__version__ = '3.0.0'
__all__ = [
    'TwitterRegister',
    'ServiceInterface',
    'HTTPServiceInterface',
    'MockServiceInterface',
    'StatusReportWrapper',
]

