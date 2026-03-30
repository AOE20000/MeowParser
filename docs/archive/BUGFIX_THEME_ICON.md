# 主题切换功能 Bug 修复

## 问题描述

在切换主题时出现 `TypeError` 错误：

```
TypeError: arguments did not match any overloaded call:
showMessage(self, title: Optional[str], msg: Optional[str], 
    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information, 
    msecs: int = 10000): argument 3 has unexpected type 'int'
```

## 问题原因

`show_message()` 方法的第三个参数应该是 `QSystemTrayIcon.MessageIcon` 枚举类型，但代码中使用了整数（1, 2）。

## 修复内容

### 1. 添加导入

在 `meow_parser/app.py` 中添加 `QSystemTrayIcon` 导入：

```python
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
```

### 2. 修复所有 show_message 调用

将所有使用整数的地方改为使用正确的枚举类型：

**修复前：**
```python
self.tray_manager.show_message("主题已切换", message, 1)
self.tray_manager.show_message("切换失败", f"错误: {str(e)}", 2)
```

**修复后：**
```python
self.tray_manager.show_message(
    "主题已切换", 
    message, 
    QSystemTrayIcon.MessageIcon.Information
)
self.tray_manager.show_message(
    "切换失败", 
    f"错误: {str(e)}", 
    QSystemTrayIcon.MessageIcon.Critical
)
```

### 3. 修复的位置

修复了以下所有 `show_message` 调用：

1. `toggle()` 方法 - 权限不足提示
2. `start_input_listener()` 方法 - 启动失败提示
3. `toggle_current_window()` 方法 - 无法切换提示（2处）
4. `toggle_current_window()` 方法 - 窗口状态切换提示（2处）
5. `change_theme()` 方法 - 主题切换提示（2处）

## 图标类型说明

`QSystemTrayIcon.MessageIcon` 枚举值：

- `Information` - 信息图标（蓝色 i）
- `Warning` - 警告图标（黄色 !）
- `Critical` - 错误图标（红色 X）
- `NoIcon` - 无图标

## 测试验证

```bash
# 编译检查
python -m py_compile meow_parser/app.py

# 运行程序
python meow_parser.py

# 测试主题切换
# 右键托盘图标 → 主题 → 选择任意主题
```

## 修复状态

✅ 已修复所有 `show_message` 调用
✅ 通过语法检查
✅ 功能正常工作

---

**修复日期：** 2026-03-30  
**修复版本：** v2.3.0
