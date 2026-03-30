#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件模块
"""

from .debug_window import DebugWindow
from .floating_window import FloatingInputWindow
from .window_selector import WindowSelector
from .config_editor import ConfigFileEditor, RuleEditDialog
from .rule_editor import ReplacementRuleEditor, RuleDialog
from .tray_icon import TrayIconManager

__all__ = [
    'DebugWindow',
    'FloatingInputWindow',
    'WindowSelector',
    'ConfigFileEditor',
    'RuleEditDialog',
    'ReplacementRuleEditor',
    'RuleDialog',
    'TrayIconManager',
]
