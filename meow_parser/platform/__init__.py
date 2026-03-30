#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台特定功能模块
"""

from ..constants import IS_WINDOWS, IS_LINUX, IS_MACOS

# 根据平台导入对应的模块
if IS_WINDOWS:
    from . import windows as platform
elif IS_LINUX:
    from . import linux as platform
elif IS_MACOS:
    from . import macos as platform
else:
    # 未知平台，使用空实现
    from . import macos as platform

# 导出平台函数
get_active_window_info = platform.get_active_window_info
enumerate_windows = platform.enumerate_windows
set_foreground_window = platform.set_foreground_window
click_position = platform.click_position
set_window_topmost = platform.set_window_topmost

__all__ = [
    'platform',
    'IS_WINDOWS',
    'IS_LINUX',
    'IS_MACOS',
    'get_active_window_info',
    'enumerate_windows',
    'set_foreground_window',
    'click_position',
    'set_window_topmost',
]
