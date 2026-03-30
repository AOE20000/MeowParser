#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件模块
"""

from .debug_window import DebugWindow
from .floating_window import FloatingInputWindow
from .window_selector import WindowSelector

# 新版编辑器（推荐使用）
from .config_editor import ConfigFileEditor, RuleEditDialog

# 旧版编辑器（已废弃，仅用于向后兼容）
# 警告：ReplacementRuleEditor 和 RuleDialog 已被废弃
# 请使用 ConfigFileEditor 和 RuleEditDialog
from .rule_editor import ReplacementRuleEditor, RuleDialog

from .tray_icon import TrayIconManager
from .styles import StyleManager

__all__ = [
    'DebugWindow',
    'FloatingInputWindow',
    'WindowSelector',
    # 推荐使用
    'ConfigFileEditor',
    'RuleEditDialog',
    # 已废弃（向后兼容）
    'ReplacementRuleEditor',
    'RuleDialog',
    'TrayIconManager',
    'StyleManager',
]
