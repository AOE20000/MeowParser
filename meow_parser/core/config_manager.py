#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件管理模块
"""

import json
from pathlib import Path
from datetime import datetime


class ConfigFileManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir=".meowparser/rules"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.current_config = None
        self.current_config_path = None
        
        # 确保有默认配置
        self._ensure_default_config()
    
    def _ensure_default_config(self):
        """确保存在默认配置"""
        default_path = self.config_dir / "default.json"
        if not default_path.exists():
            default_config = {
                "name": "喵语转换（默认）",
                "version": "1.0.0",
                "description": "将文本转换为可爱的喵语",
                "author": "MeowParser",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "groups": [
                    {
                        "name": "喵语转换",
                        "description": "在标点前添加喵",
                        "collapsed": False,
                        "rules": [
                            {
                                "enabled": True,
                                "pattern": "([^喵])([。，！？；、）（：])",
                                "replacement": "\\1喵\\2",
                                "is_regex": True,
                                "description": "标点前添加喵"
                            },
                            {
                                "enabled": True,
                                "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                                "replacement": "\\1喵\\2",
                                "is_regex": True,
                                "description": "换行前添加喵"
                            },
                            {
                                "enabled": True,
                                "pattern": "([^。，！？；、）（：\\n])$",
                                "replacement": "\\1喵",
                                "is_regex": True,
                                "description": "句尾添加喵"
                            }
                        ]
                    }
                ]
            }
            
            with open(default_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def list_configs(self):
        """列出所有配置文件"""
        configs = []
        for file_path in sorted(self.config_dir.glob("*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs.append({
                        "path": file_path,
                        "name": config.get("name", file_path.stem),
                        "description": config.get("description", ""),
                        "version": config.get("version", "1.0.0"),
                        "updated": config.get("updated", ""),
                        "rule_count": sum(len(g.get("rules", [])) for g in config.get("groups", []))
                    })
            except Exception as e:
                print(f"加载配置文件失败 {file_path}: {e}")
        return configs
    
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.current_config = json.load(f)
                self.current_config_path = Path(config_path)
                return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
    
    def save_config(self, config_path=None):
        """保存配置文件"""
        if config_path is None:
            config_path = self.current_config_path
        
        if config_path is None:
            raise ValueError("未指定配置文件路径")
        
        try:
            # 更新时间戳
            self.current_config["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def create_config(self, name, description=""):
        """创建新配置文件"""
        config = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "groups": []
        }
        
        # 生成文件名
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        config_path = self.config_dir / f"{safe_name}.json"
        
        # 避免重名
        counter = 1
        while config_path.exists():
            config_path = self.config_dir / f"{safe_name}_{counter}.json"
            counter += 1
        
        self.current_config = config
        self.current_config_path = config_path
        self.save_config()
        
        return config_path
    
    def delete_config(self, config_path):
        """删除配置文件"""
        try:
            # 不允许删除默认配置
            if Path(config_path).name == "default.json":
                return False, "不能删除默认配置"
            
            Path(config_path).unlink()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"
    
    def get_all_rules(self):
        """获取当前配置的所有启用规则（扁平化，按顺序）"""
        if not self.current_config:
            return []
        
        all_rules = []
        for group in self.current_config.get("groups", []):
            for rule in group.get("rules", []):
                if rule.get("enabled", True):
                    all_rules.append(rule)
        
        return all_rules
    
    def migrate_old_config(self, old_config):
        """迁移旧配置格式"""
        new_config = {
            "name": "迁移的配置",
            "version": "1.0.0",
            "description": "从旧版本迁移",
            "author": "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "groups": []
        }
        
        old_groups = old_config.get("groups", {})
        
        for group_name, group_data in old_groups.items():
            # 只迁移启用的规则组
            if not group_data.get("enabled", True):
                continue
            
            new_group = {
                "name": group_name,
                "description": "",
                "collapsed": False,
                "rules": []
            }
            
            for rule in group_data.get("rules", []):
                new_rule = {
                    "enabled": True,
                    "pattern": rule.get("pattern", ""),
                    "replacement": rule.get("replacement", ""),
                    "is_regex": rule.get("is_regex", False),
                    "description": f"{rule.get('pattern', '')} → {rule.get('replacement', '')}"
                }
                new_group["rules"].append(new_rule)
            
            new_config["groups"].append(new_group)
        
        return new_config
