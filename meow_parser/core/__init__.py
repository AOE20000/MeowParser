#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能模块
"""

from .config_manager import ConfigFileManager
from .text_processor import TextProcessor
from .instance_lock import check_single_instance
from .privilege import is_admin, ensure_admin

__all__ = ['ConfigFileManager', 'TextProcessor', 'check_single_instance', 'is_admin', 'ensure_admin']
