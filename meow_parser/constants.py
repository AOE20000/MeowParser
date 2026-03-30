#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量定义模块
"""

import sys

# 平台检测
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_MACOS = sys.platform == 'darwin'

# 配置路径
CONFIG_DIR = ".meowparser/rules"
WINDOW_SETTINGS_FILE = ".meowparser/window_settings.json"
OLD_CONFIG_FILE = "replacement_rules.json"  # 旧配置文件（用于迁移）
OLD_WINDOW_SETTINGS_FILE = "window_settings.json"  # 旧窗口配置（用于迁移）

# 版本信息
VERSION = "2.2.0"
APP_NAME = "MeowParser"
ORG_NAME = "MeowParser"

# 默认配置
DEFAULT_CONFIG_NAME = "default.json"

# 单实例锁
if IS_WINDOWS:
    INSTANCE_LOCK_NAME = r"Global\MeowParser_SingleInstance_Event"
else:
    INSTANCE_LOCK_FILE = ".meowparser/instance.lock"
