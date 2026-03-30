#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - 喵语解析器
智能文本处理工具
"""

from .constants import VERSION, APP_NAME
from .app import MeowParser

__version__ = VERSION
__app_name__ = APP_NAME

__all__ = ['__version__', '__app_name__', 'MeowParser']
