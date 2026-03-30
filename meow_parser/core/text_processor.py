#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本处理引擎模块
"""

import re


class TextProcessor:
    """文本处理引擎"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def process(self, text):
        """处理文本 - 按规则顺序依次应用"""
        if not text or len(text.strip()) == 0:
            return text
        
        result = text
        rules = self.config_manager.get_all_rules()
        
        for rule in rules:
            pattern = rule.get("pattern", "")
            replacement = rule.get("replacement", "")
            is_regex = rule.get("is_regex", False)
            
            if not pattern:
                continue
            
            try:
                if is_regex:
                    result = re.sub(pattern, replacement, result)
                else:
                    result = result.replace(pattern, replacement)
            except re.error as e:
                print(f"正则表达式错误 '{pattern}': {e}")
                continue
        
        return result
