# UI 样式设计说明

## 概述

MeowParser v2.2.1 采用了受 BreezeStyleSheets 启发的现代化深色主题设计，提供统一、美观的用户界面体验。

---

## 设计理念

### 1. 现代化深色主题

**主色调：**
- 背景色：`#31363b` (深灰色)
- 前景色：`#eff0f1` (浅灰白色)
- 强调色：`#3daee9` (蓝色)

**设计原则：**
- 低对比度，减少眼睛疲劳
- 清晰的视觉层次
- 一致的交互反馈
- 优雅的动画过渡

### 2. 统一的视觉语言

所有 UI 组件遵循相同的设计规范：
- 圆角：4px（按钮、输入框）
- 边框：1px solid（默认状态）
- 悬停效果：蓝色高亮
- 禁用状态：灰色半透明

---

## 组件样式

### 按钮 (QPushButton)

**默认状态：**
```css
background-color: #31363b
color: #eff0f1
border: 1px solid #76797c
border-radius: 4px
padding: 6px 16px
```

**悬停状态：**
```css
background-color: #3daee9
border-color: #3daee9
color: #ffffff
```

**按下状态：**
```css
background-color: #2a79a3
```

**禁用状态：**
```css
background-color: #454545
color: #76797c
```

### 输入框 (QLineEdit)

**默认状态：**
```css
background-color: #1d2023
color: #eff0f1
border: 1px solid #76797c
border-radius: 4px
padding: 4px 8px
```

**焦点状态：**
```css
border: 1px solid #3daee9
```

**选中文本：**
```css
selection-background-color: #3daee9
selection-color: #ffffff
```

### 菜单 (QMenu)

**菜单背景：**
```css
background-color: #31363b
color: #eff0f1
border: 1px solid #76797c
padding: 4px
```

**菜单项：**
```css
padding: 8px 32px 8px 32px
border-radius: 3px
```

**菜单项悬停：**
```css
background-color: #3daee9
color: #ffffff
```

**分隔线：**
```css
height: 1px
background-color: #76797c
margin: 6px 10px
```

### 树形控件 (QTreeWidget)

**背景：**
```css
background-color: #1d2023
color: #eff0f1
border: 1px solid #76797c
```

**项目悬停：**
```css
background-color: rgba(61, 173, 232, 0.1)
```

**项目选中：**
```css
background-color: #3daee9
color: #ffffff
```

**表头：**
```css
background-color: #31363b
border-right: 1px solid #76797c
border-bottom: 1px solid #76797c
padding: 6px 8px
```

### 复选框 (QCheckBox)

**指示器：**
```css
width: 18px
height: 18px
border: 1px solid #76797c
border-radius: 3px
background-color: #1d2023
```

**选中状态：**
```css
background-color: #3daee9
border-color: #3daee9
```

### 滚动条 (QScrollBar)

**垂直滚动条：**
```css
background-color: #1d2023
width: 14px
border-radius: 7px
```

**滚动条手柄：**
```css
background-color: #76797c
border-radius: 7px
min-height: 30px
```

**手柄悬停：**
```css
background-color: #3daee9
```

---

## 特殊组件

### 悬浮输入窗口

**窗口样式：**
```css
background-color: #1e1e1e
border: 3px solid #3daee9
border-radius: 6px
```

**输入框：**
```css
background-color: #252526
color: #cccccc
border: 2px solid #3e3e42
border-radius: 4px
padding: 8px 12px
font-size: 11pt
```

### 托盘菜单

托盘菜单使用与主菜单相同的样式，但通过 `StyleManager.get_menu_style()` 单独应用，确保在系统托盘中也能正确显示。

---

## 颜色系统

### 主色板

| 颜色名称 | 十六进制 | 用途 |
|---------|---------|------|
| 主背景 | `#31363b` | 窗口、对话框背景 |
| 深背景 | `#1d2023` | 输入框、列表背景 |
| 前景色 | `#eff0f1` | 文本颜色 |
| 中间色 | `#76797c` | 边框、分隔线 |
| 强调色 | `#3daee9` | 悬停、选中、焦点 |
| 深强调 | `#2a79a3` | 按下状态 |
| 禁用色 | `#454545` | 禁用背景 |
| 禁用文本 | `#76797c` | 禁用文本 |

### 语义颜色

| 用途 | 颜色 | 说明 |
|-----|------|------|
| 成功 | `#27ae60` | 成功提示 |
| 警告 | `#f39c12` | 警告提示 |
| 错误 | `#e74c3c` | 错误提示 |
| 信息 | `#3daee9` | 信息提示 |
| 正则标识 | `#FFA500` | 橙色，标识正则规则 |

---

## 使用方法

### 应用全局样式

在应用启动时自动应用：

```python
from PyQt6.QtWidgets import QApplication
from meow_parser.ui.styles import StyleManager

app = QApplication(sys.argv)
StyleManager.apply_breeze_dark(app)
```

### 应用菜单样式

对于系统托盘菜单等特殊菜单：

```python
from meow_parser.ui.styles import StyleManager

menu = QMenu()
menu.setStyleSheet(StyleManager.get_menu_style())
```

### 自定义样式

如果需要自定义样式，可以修改 `meow_parser/ui/styles.py` 中的 `BREEZE_DARK_STYLE` 常量。

---

## 响应式设计

### 字体大小

- 默认字体：9pt
- 悬浮窗输入框：11pt
- 标题：12pt（加粗）

### 组件尺寸

- 按钮最小高度：20px
- 输入框高度：28px（默认）
- 悬浮窗输入框高度：50px
- 滚动条宽度：14px

### 间距

- 按钮内边距：6px 16px
- 输入框内边距：4px 8px
- 菜单项内边距：8px 32px
- 对话框边距：10px

---

## 可访问性

### 对比度

所有文本与背景的对比度符合 WCAG AA 标准：
- 正常文本：至少 4.5:1
- 大文本：至少 3:1

### 焦点指示

所有可交互元素在获得焦点时都有明显的视觉反馈：
- 输入框：蓝色边框
- 按钮：蓝色背景
- 菜单项：蓝色背景

### 状态指示

- 启用/禁用：通过颜色和图标双重指示
- 选中状态：通过背景色和复选标记
- 悬停状态：通过背景色变化

---

## 主题扩展

### 添加浅色主题

可以在 `styles.py` 中添加浅色主题：

```python
BREEZE_LIGHT_STYLE = """
/* 浅色主题样式 */
QWidget {
    background-color: #eff0f1;
    color: #31363b;
}
/* ... 其他样式 */
"""
```

### 自定义颜色

修改颜色变量即可快速定制主题：

```python
# 主色调
PRIMARY_BG = "#31363b"
PRIMARY_FG = "#eff0f1"
ACCENT_COLOR = "#3daee9"
```

---

## 已知限制

### Qt 样式表限制

1. **图标颜色**：无法通过样式表动态改变 SVG 图标颜色
2. **复杂动画**：样式表不支持复杂的过渡动画
3. **伪状态**：某些伪状态组合可能不生效

### 解决方案

- 使用 QCommonStyle 子类化处理图标
- 使用 QPropertyAnimation 实现动画
- 通过代码动态设置状态样式

---

## 性能优化

### 样式表缓存

样式表在应用启动时加载一次，避免重复解析。

### 选择器优化

- 使用类选择器而非通用选择器
- 避免过深的选择器嵌套
- 使用对象名称进行精确选择

### 最佳实践

```python
# 好的做法
widget.setObjectName("MyWidget")
# CSS: #MyWidget { ... }

# 避免
# CSS: QWidget QWidget QWidget { ... }
```

---

## 参考资源

- [BreezeStyleSheets](https://github.com/Alexhuszagh/BreezeStyleSheets)
- [Qt Style Sheets Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)
- [Material Design Color System](https://material.io/design/color)

---

**更新日期：** 2026-03-30  
**版本：** v2.2.1
