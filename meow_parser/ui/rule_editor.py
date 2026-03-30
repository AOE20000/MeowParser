#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旧版规则编辑器模块（用于兼容）
"""

import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt


class ReplacementRuleEditor(QWidget):
    """替换规则编辑器（非模态窗口）"""
    
    def __init__(self, parent, replacement_rules, save_callback):
        super().__init__(parent)
        self.replacement_rules = replacement_rules
        self.save_callback = save_callback
        self.current_group = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("替换规则管理")
        self.setGeometry(100, 100, 900, 600)
        
        # 设置窗口标志（独立窗口）
        self.setWindowFlags(Qt.WindowType.Window)
        
        main_layout = QHBoxLayout()
        
        # 左侧：规则组列表
        left_panel = QVBoxLayout()
        
        group_label = QLabel("规则组（双击切换启用/禁用）：")
        left_panel.addWidget(group_label)
        
        self.group_list = QTreeWidget()
        self.group_list.setHeaderLabels(['规则组', '状态'])
        self.group_list.setColumnWidth(0, 150)
        self.group_list.setColumnWidth(1, 50)
        self.group_list.itemClicked.connect(self.on_group_selected)
        self.group_list.itemDoubleClicked.connect(self.toggle_group)
        left_panel.addWidget(self.group_list)
        
        # 规则组按钮
        group_btn_layout = QHBoxLayout()
        add_group_btn = QPushButton("新建组")
        add_group_btn.clicked.connect(self.add_group)
        group_btn_layout.addWidget(add_group_btn)
        
        rename_group_btn = QPushButton("重命名")
        rename_group_btn.clicked.connect(self.rename_group)
        group_btn_layout.addWidget(rename_group_btn)
        
        delete_group_btn = QPushButton("删除组")
        delete_group_btn.clicked.connect(self.delete_group)
        group_btn_layout.addWidget(delete_group_btn)
        
        left_panel.addLayout(group_btn_layout)
        
        # 导入导出按钮
        import_export_layout = QHBoxLayout()
        import_btn = QPushButton("导入规则组")
        import_btn.clicked.connect(self.import_group)
        import_export_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出规则组")
        export_btn.clicked.connect(self.export_group)
        import_export_layout.addWidget(export_btn)
        
        left_panel.addLayout(import_export_layout)
        
        # 右侧：规则列表
        right_panel = QVBoxLayout()
        
        # 当前规则组标签
        self.current_group_label = QLabel("请选择规则组")
        self.current_group_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        right_panel.addWidget(self.current_group_label)
        
        # 规则列表
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['优先级', '匹配文本', '替换为', '类型'])
        self.tree.setColumnWidth(0, 60)
        self.tree.setColumnWidth(1, 180)
        self.tree.setColumnWidth(2, 180)
        self.tree.setColumnWidth(3, 80)
        right_panel.addWidget(self.tree)
        
        # 规则按钮
        rule_btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加规则")
        add_btn.clicked.connect(self.add_rule)
        rule_btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("编辑规则")
        edit_btn.clicked.connect(self.edit_rule)
        rule_btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除规则")
        delete_btn.clicked.connect(self.delete_rule)
        rule_btn_layout.addWidget(delete_btn)
        
        up_btn = QPushButton("上移")
        up_btn.clicked.connect(self.move_up)
        rule_btn_layout.addWidget(up_btn)
        
        down_btn = QPushButton("下移")
        down_btn.clicked.connect(self.move_down)
        rule_btn_layout.addWidget(down_btn)
        
        right_panel.addLayout(rule_btn_layout)
        
        # 说明文本
        info_text = ("说明：规则按顺序依次应用，每个规则会替换文本中所有匹配的位置。\n"
                    "文本示例：\"我\" → \"喵\"，则\"我的\"会变成\"喵的\"。\n"
                    "正则示例：\"\\d+\" → \"数字\"，则\"123\"会变成\"数字\"。")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; padding: 10px;")
        right_panel.addWidget(info_label)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        close_layout.addWidget(close_btn)
        right_panel.addLayout(close_layout)
        
        # 组合布局
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(250)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        self.setLayout(main_layout)
        
        # 刷新规则组列表
        self.refresh_groups()
    
    def closeEvent(self, event):
        """关闭事件 - 保存设置"""
        try:
            # 停止所有定时器
            for timer in self.findChildren(QTimer):
                timer.stop()
            
            # 保存设置
            if self.save_callback:
                self.save_callback()
            
            # 接受关闭事件
            event.accept()
        except Exception as e:
            print(f"关闭规则编辑器错误: {e}")
            event.accept()
    
    def refresh_groups(self):
        """刷新规则组列表"""
        self.group_list.clear()
        
        # 确保有 groups 结构
        if "groups" not in self.replacement_rules:
            # 自动迁移旧格式
            old_rules = self.replacement_rules.get("rules", [])
            
            # 清空原字典并更新，而不是重新赋值
            self.replacement_rules.clear()
            self.replacement_rules["groups"] = {
                "默认规则组": {
                    "enabled": True,
                    "rules": old_rules
                },
                "喵语转换": {
                    "enabled": True,
                    "rules": [
                        {
                            "pattern": "([^喵])([。，！？；、）（：])",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^。，！？；、）（：\\n])$",
                            "replacement": "\\1喵",
                            "is_regex": True
                        }
                    ]
                }
            }
            # 保存迁移后的配置
            if self.save_callback:
                self.save_callback()
        
        groups = self.replacement_rules.get("groups", {})
        for group_name, group_data in groups.items():
            item = QTreeWidgetItem(self.group_list)
            item.setText(0, group_name)
            item.setText(1, "✓" if group_data.get("enabled", True) else "✗")
            item.setData(0, Qt.ItemDataRole.UserRole, group_name)
        
        # 选择第一个组
        if self.group_list.topLevelItemCount() > 0:
            self.group_list.setCurrentItem(self.group_list.topLevelItem(0))
            self.on_group_selected(self.group_list.topLevelItem(0), 0)
    
    def on_group_selected(self, item, column):
        """选择规则组"""
        if not item:
            return
        
        group_name = item.data(0, Qt.ItemDataRole.UserRole)
        self.current_group = group_name
        self.current_group_label.setText(f"规则组：{group_name}")
        self.refresh_rules()
    
    def toggle_group(self, item, column):
        """切换规则组启用状态"""
        if not item:
            return
        
        group_name = item.data(0, Qt.ItemDataRole.UserRole)
        groups = self.replacement_rules.get("groups", {})
        
        if group_name in groups:
            current_state = groups[group_name].get("enabled", True)
            groups[group_name]["enabled"] = not current_state
            item.setText(1, "✓" if not current_state else "✗")
            self.save_callback()
    
    def refresh_rules(self):
        """刷新规则列表"""
        self.tree.clear()
        
        if not self.current_group:
            return
        
        groups = self.replacement_rules.get("groups", {})
        if self.current_group not in groups:
            return
        
        rules = groups[self.current_group].get("rules", [])
        for index, rule in enumerate(rules, 1):
            rule_type = "正则" if rule.get("is_regex", False) else "文本"
            item = QTreeWidgetItem(self.tree)
            item.setText(0, str(index))
            item.setText(1, rule.get("pattern", ""))
            item.setText(2, rule.get("replacement", ""))
            item.setText(3, rule_type)
    
    def add_group(self):
        """添加规则组"""
        group_name, ok = QInputDialog.getText(self, "新建规则组", "规则组名称：")
        if ok and group_name:
            groups = self.replacement_rules.setdefault("groups", {})
            if group_name in groups:
                QMessageBox.warning(self, "错误", "规则组已存在")
                return
            
            groups[group_name] = {
                "enabled": True,
                "rules": []
            }
            self.refresh_groups()
            self.save_callback()
    
    def rename_group(self):
        """重命名规则组"""
        current_item = self.group_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        new_name, ok = QInputDialog.getText(self, "重命名规则组", "新名称：", text=old_name)
        
        if ok and new_name and new_name != old_name:
            groups = self.replacement_rules.get("groups", {})
            if new_name in groups:
                QMessageBox.warning(self, "错误", "规则组已存在")
                return
            
            groups[new_name] = groups.pop(old_name)
            if self.current_group == old_name:
                self.current_group = new_name
            
            self.refresh_groups()
            
            # 重新选中重命名后的组
            for i in range(self.group_list.topLevelItemCount()):
                item = self.group_list.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == new_name:
                    self.group_list.setCurrentItem(item)
                    self.on_group_selected(item, 0)
                    break
            
            self.save_callback()
    
    def delete_group(self):
        """删除规则组"""
        current_item = self.group_list.currentItem()
        if not current_item:
            return
        
        group_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除规则组 '{group_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            groups = self.replacement_rules.get("groups", {})
            if group_name in groups:
                del groups[group_name]
                
                # 先清空当前组和右侧面板
                self.current_group = None
                self.current_group_label.setText("请选择规则组")
                self.tree.clear()
                
                # 再刷新列表
                self.refresh_groups()
                self.save_callback()
    
    def add_rule(self):
        """添加规则"""
        if not self.current_group:
            QMessageBox.warning(self, "错误", "请先选择规则组")
            return
        
        dialog = RuleDialog(self, "添加规则")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pattern, replacement, is_regex = dialog.get_result()
            
            if not pattern:
                QMessageBox.warning(self, "错误", "匹配文本不能为空")
                return
            
            if not replacement:
                reply = QMessageBox.question(
                    self,
                    "确认",
                    "替换文本为空，这将删除匹配的内容。是否继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            groups = self.replacement_rules.get("groups", {})
            groups[self.current_group].setdefault("rules", []).append({
                "pattern": pattern,
                "replacement": replacement,
                "is_regex": is_regex
            })
            self.refresh_rules()
            self.save_callback()
    
    def edit_rule(self):
        """编辑规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        groups = self.replacement_rules.get("groups", {})
        rule = groups[self.current_group]["rules"][index]
        
        dialog = RuleDialog(
            self, 
            "编辑规则",
            rule.get("pattern", ""),
            rule.get("replacement", ""),
            rule.get("is_regex", False)
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pattern, replacement, is_regex = dialog.get_result()
            
            if not pattern:
                QMessageBox.warning(self, "错误", "匹配文本不能为空")
                return
            
            if not replacement:
                reply = QMessageBox.question(
                    self,
                    "确认",
                    "替换文本为空，这将删除匹配的内容。是否继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            groups[self.current_group]["rules"][index] = {
                "pattern": pattern,
                "replacement": replacement,
                "is_regex": is_regex
            }
            self.refresh_rules()
            self.save_callback()
    
    def delete_rule(self):
        """删除规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条规则吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            index = self.tree.indexOfTopLevelItem(current_item)
            groups = self.replacement_rules.get("groups", {})
            del groups[self.current_group]["rules"][index]
            self.refresh_rules()
            self.save_callback()
    
    def move_up(self):
        """上移规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        if index > 0:
            groups = self.replacement_rules.get("groups", {})
            rules = groups[self.current_group]["rules"]
            rules[index], rules[index-1] = rules[index-1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.setCurrentItem(self.tree.topLevelItem(index-1))
    
    def move_down(self):
        """下移规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        groups = self.replacement_rules.get("groups", {})
        rules = groups[self.current_group]["rules"]
        if index < len(rules) - 1:
            rules[index], rules[index+1] = rules[index+1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.setCurrentItem(self.tree.topLevelItem(index+1))
    
    def import_group(self):
        """导入规则组"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入规则组",
            "",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 检查是否是单个规则组
            if "enabled" in imported_data and "rules" in imported_data:
                # 单个规则组格式
                group_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # 检查是否已存在
                groups = self.replacement_rules.get("groups", {})
                if group_name in groups:
                    new_group_name, ok = QInputDialog.getText(
                        self,
                        "规则组已存在",
                        f"规则组 '{group_name}' 已存在，请输入新名称：",
                        text=f"{group_name}_导入"
                    )
                    if not ok or not new_group_name:
                        return
                    group_name = new_group_name
                
                groups[group_name] = imported_data
                QMessageBox.information(self, "成功", f"已导入规则组：{group_name}")
            
            elif "groups" in imported_data:
                # 多个规则组格式
                groups = self.replacement_rules.get("groups", {})
                imported_count = 0
                
                for group_name, group_data in imported_data["groups"].items():
                    original_name = group_name
                    if group_name in groups:
                        # 重命名冲突的规则组
                        counter = 1
                        while group_name in groups:
                            group_name = f"{original_name}_{counter}"
                            counter += 1
                    
                    groups[group_name] = group_data
                    imported_count += 1
                
                QMessageBox.information(self, "成功", f"已导入 {imported_count} 个规则组")
            
            else:
                QMessageBox.warning(self, "错误", "无效的规则组文件格式")
                return
            
            self.refresh_groups()
            self.save_callback()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败：{str(e)}")
    
    def export_group(self):
        """导出规则组"""
        current_item = self.group_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要导出的规则组")
            return
        
        group_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        groups = self.replacement_rules.get("groups", {})
        
        if group_name not in groups:
            return
        
        # 默认文件名
        default_filename = f"{group_name}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出规则组",
            default_filename,
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 导出单个规则组
            export_data = groups[group_name]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"规则组已导出到：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")


class RuleDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent, title, pattern="", replacement="", is_regex=False):
        super().__init__(parent)
        self.result = None
        self.init_ui(title, pattern, replacement, is_regex)
        
    def init_ui(self, title, pattern, replacement, is_regex):
        """初始化UI"""
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 匹配文本
        pattern_label = QLabel("匹配文本：")
        layout.addWidget(pattern_label)
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setText(pattern)
        layout.addWidget(self.pattern_input)
        
        # 替换为
        replacement_label = QLabel("替换为：")
        layout.addWidget(replacement_label)
        
        self.replacement_input = QLineEdit()
        self.replacement_input.setText(replacement)
        layout.addWidget(self.replacement_input)
        
        # 正则表达式选项
        self.regex_checkbox = QCheckBox("使用正则表达式")
        self.regex_checkbox.setChecked(is_regex)
        layout.addWidget(self.regex_checkbox)
        
        # 提示
        hint_label = QLabel("提示：正则表达式示例 - \\d+ 匹配数字，[a-z]+ 匹配小写字母")
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(hint_label)
        
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
        
        # 设置焦点
        self.pattern_input.setFocus()
    
    def accept(self):
        """重写 accept 方法，添加验证"""
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
                QMessageBox.warning(
                    self,
                    "正则表达式错误",
                    f"无效的正则表达式：\n{str(e)}"
                )
                return
        
        super().accept()
    
    def get_result(self):
        """获取结果"""
        return (
            self.pattern_input.text(),
            self.replacement_input.text(),
            self.regex_checkbox.isChecked()
        )
