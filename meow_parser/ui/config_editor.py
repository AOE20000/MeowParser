#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件编辑器模块
"""

import re
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QMessageBox, QComboBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt


class RuleEditDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent, rule=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑规则" if self.rule else "添加规则")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 描述
        layout.addWidget(QLabel("描述:"))
        self.desc_input = QLineEdit()
        self.desc_input.setText(self.rule.get("description", ""))
        layout.addWidget(self.desc_input)
        
        # 匹配文本
        layout.addWidget(QLabel("匹配文本:"))
        self.pattern_input = QLineEdit()
        self.pattern_input.setText(self.rule.get("pattern", ""))
        layout.addWidget(self.pattern_input)
        
        # 替换为
        layout.addWidget(QLabel("替换为:"))
        self.replacement_input = QLineEdit()
        self.replacement_input.setText(self.rule.get("replacement", ""))
        layout.addWidget(self.replacement_input)
        
        # 正则表达式
        self.regex_checkbox = QCheckBox("使用正则表达式")
        self.regex_checkbox.setChecked(self.rule.get("is_regex", False))
        layout.addWidget(self.regex_checkbox)
        
        # 启用
        self.enabled_checkbox = QCheckBox("启用此规则")
        self.enabled_checkbox.setChecked(self.rule.get("enabled", True))
        layout.addWidget(self.enabled_checkbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def accept(self):
        """验证并接受"""
        pattern = self.pattern_input.text()
        is_regex = self.regex_checkbox.isChecked()
        
        if not pattern:
            QMessageBox.warning(self, "错误", "匹配文本不能为空")
            return
        
        # 验证正则表达式
        if is_regex:
            try:
                re.compile(pattern)
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", f"无效的正则表达式:\n{str(e)}")
                return
        
        super().accept()
    
    def get_result(self):
        """获取结果"""
        return {
            "enabled": self.enabled_checkbox.isChecked(),
            "pattern": self.pattern_input.text(),
            "replacement": self.replacement_input.text(),
            "is_regex": self.regex_checkbox.isChecked(),
            "description": self.desc_input.text() or f"{self.pattern_input.text()} → {self.replacement_input.text()}"
        }


class ConfigFileEditor(QWidget):
    """配置文件编辑器"""
    
    def __init__(self, parent, config_manager, save_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.save_callback = save_callback
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("替换规则管理")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout()
        
        # 配置文件选择器
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("当前配置:"))
        
        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(300)
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        
        new_btn = QPushButton("新建")
        new_btn.clicked.connect(self.create_config)
        config_layout.addWidget(new_btn)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_config)
        config_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self.export_config)
        config_layout.addWidget(export_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_config)
        config_layout.addWidget(delete_btn)
        
        config_layout.addStretch()
        layout.addLayout(config_layout)
        
        # 规则树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['规则', '操作'])
        self.tree.setColumnWidth(0, 600)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        add_group_btn = QPushButton("添加规则组")
        add_group_btn.clicked.connect(self.add_group)
        button_layout.addWidget(add_group_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 加载配置列表
        self.refresh_config_list()
    
    def refresh_config_list(self):
        """刷新配置列表"""
        self.config_combo.blockSignals(True)
        self.config_combo.clear()
        
        configs = self.config_manager.list_configs()
        
        for config in configs:
            display_text = f"{config['name']} ({config['rule_count']}条规则)"
            if config['description']:
                display_text += f" - {config['description'][:30]}"
            
            self.config_combo.addItem(display_text, config['path'])
        
        self.config_combo.blockSignals(False)
        
        # 加载第一个配置
        if self.config_combo.count() > 0:
            self.on_config_changed(0)
    
    def on_config_changed(self, index):
        """配置文件切换"""
        if index < 0:
            return
        
        config_path = self.config_combo.itemData(index)
        if config_path:
            self.config_manager.load_config(config_path)
            self.refresh_tree()
            
            # 通知主应用配置已更改
            if self.save_callback:
                self.save_callback()
    
    def refresh_tree(self):
        """刷新规则树"""
        self.tree.clear()
        
        if not self.config_manager.current_config:
            return
        
        groups = self.config_manager.current_config.get("groups", [])
        
        for group_index, group in enumerate(groups):
            # 创建规则组节点
            group_item = QTreeWidgetItem(self.tree)
            group_name = group.get("name", f"规则组 {group_index + 1}")
            rules = group.get("rules", [])
            rule_count = len(rules)
            enabled_count = sum(1 for r in rules if r.get("enabled", True))
            
            collapsed = group.get("collapsed", False)
            icon = "▶" if collapsed else "▼"
            
            group_item.setText(0, f"{icon} {group_name} ({enabled_count}/{rule_count}条规则)")
            group_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "group", "index": group_index})
            group_item.setExpanded(not collapsed)
            
            # 添加规则
            for rule_index, rule in enumerate(rules):
                rule_item = QTreeWidgetItem(group_item)
                
                enabled = "☑" if rule.get("enabled", True) else "☐"
                description = rule.get("description", "")
                
                rule_item.setText(0, f"  {enabled} {description}")
                rule_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "rule",
                    "group_index": group_index,
                    "rule_index": rule_index
                })
    
    def on_item_double_clicked(self, item, column):
        """双击项目"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "group":
            # 切换折叠状态
            group_index = data["index"]
            groups = self.config_manager.current_config.get("groups", [])
            if group_index < len(groups):
                groups[group_index]["collapsed"] = not groups[group_index].get("collapsed", False)
                self.refresh_tree()
        
        elif data["type"] == "rule":
            # 编辑规则
            self.edit_rule(data["group_index"], data["rule_index"])
    
    def add_group(self):
        """添加规则组"""
        name, ok = QInputDialog.getText(self, "新建规则组", "规则组名称:")
        if ok and name:
            if not self.config_manager.current_config:
                QMessageBox.warning(self, "错误", "请先选择或创建配置文件")
                return
            
            groups = self.config_manager.current_config.setdefault("groups", [])
            groups.append({
                "name": name,
                "description": "",
                "collapsed": False,
                "rules": []
            })
            
            self.refresh_tree()
            self.save()
    
    def edit_rule(self, group_index, rule_index):
        """编辑规则"""
        groups = self.config_manager.current_config.get("groups", [])
        if group_index >= len(groups):
            return
        
        rules = groups[group_index].get("rules", [])
        if rule_index >= len(rules):
            return
        
        rule = rules[rule_index]
        dialog = RuleEditDialog(self, rule)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rules[rule_index] = dialog.get_result()
            self.refresh_tree()
            self.save()
    
    def create_config(self):
        """创建新配置"""
        name, ok = QInputDialog.getText(self, "新建配置", "配置名称:")
        if ok and name:
            description, ok2 = QInputDialog.getText(self, "新建配置", "配置描述:")
            if ok2:
                self.config_manager.create_config(name, description)
                self.refresh_config_list()
    
    def import_config(self):
        """导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                dest_path = self.config_manager.config_dir / Path(file_path).name
                shutil.copy(file_path, dest_path)
                self.refresh_config_list()
                QMessageBox.information(self, "成功", "配置已导入")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {e}")
    
    def export_config(self):
        """导出配置"""
        if not self.config_manager.current_config_path:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "", "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                shutil.copy(self.config_manager.current_config_path, file_path)
                QMessageBox.information(self, "成功", "配置已导出")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def delete_config(self):
        """删除配置"""
        if not self.config_manager.current_config_path:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除配置 '{self.config_manager.current_config['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.config_manager.delete_config(
                self.config_manager.current_config_path
            )
            
            if success:
                self.refresh_config_list()
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "错误", message)
    
    def save(self):
        """保存配置"""
        if self.config_manager.save_config():
            if self.save_callback:
                self.save_callback()
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            # 停止所有定时器
            for timer in self.findChildren(QTimer):
                timer.stop()
            
            # 保存配置
            self.save()
            
            # 接受关闭事件
            event.accept()
        except Exception as e:
            print(f"关闭配置编辑器错误: {e}")
            event.accept()
