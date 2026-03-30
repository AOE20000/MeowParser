# MeowParser 主题切换指南

## 功能概述

MeowParser v2.3 新增了自动切换深色/浅色主题的功能，支持：

- 🌓 **自动模式**：跟随系统主题自动切换
- 🌙 **深色主题**：经典的 Breeze Dark 风格
- ☀️ **浅色主题**：清新的 Breeze Light 风格

---

## 使用方法

### 1. 通过托盘菜单切换

1. 右键点击系统托盘中的"喵"图标
2. 选择"主题"菜单
3. 选择你想要的主题模式：
   - 🌓 自动（跟随系统）
   - 🌙 深色
   - ☀️ 浅色

### 2. 主题模式说明

#### 自动模式（推荐）

- 自动检测系统主题设置
- 系统切换到深色模式时，应用深色主题
- 系统切换到浅色模式时，应用浅色主题
- 每 5 秒自动检查一次系统主题变化

**支持的系统：**
- Windows 10/11：读取注册表 `AppsUseLightTheme` 设置
- macOS：读取 `AppleInterfaceStyle` 设置
- Linux：读取 GTK 主题配置

#### 深色主题

- 固定使用深色主题
- 不受系统主题影响
- 适合长时间使用，减少眼睛疲劳

#### 浅色主题

- 固定使用浅色主题
- 不受系统主题影响
- 适合明亮环境使用

---

## 主题配置文件

主题偏好保存在：`.meowparser/theme_settings.json`

```json
{
  "theme": "auto"
}
```

可选值：
- `"auto"` - 自动模式
- `"dark"` - 深色主题
- `"light"` - 浅色主题

---

## 主题预览

### 深色主题

- 主背景：`#31363b` (深灰色)
- 深背景：`#1d2023` (更深的灰色)
- 前景色：`#eff0f1` (浅灰白色)
- 强调色：`#3daee9` (蓝色)

### 浅色主题

- 主背景：`#eff0f1` (浅灰色)
- 深背景：`#ffffff` (白色)
- 前景色：`#31363b` (深灰色)
- 强调色：`#3daee9` (蓝色)

---

## 技术细节

### 系统主题检测

#### Windows

```python
import winreg
registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
key = winreg.OpenKey(
    registry,
    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
)
value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
# value == 1: 浅色主题
# value == 0: 深色主题
```

#### macOS

```bash
defaults read -g AppleInterfaceStyle
# 返回 "Dark": 深色主题
# 返回错误: 浅色主题
```

#### Linux

读取 GTK 配置文件：`~/.config/gtk-3.0/settings.ini`

```ini
[Settings]
gtk-theme-name=Adwaita-dark
```

### 主题监控

在自动模式下，程序会每 5 秒检查一次系统主题：

```python
self.theme_monitor_timer = QTimer()
self.theme_monitor_timer.timeout.connect(lambda: self._check_theme_change(app))
self.theme_monitor_timer.start(5000)  # 5000ms = 5秒
```

---

## 常见问题

### Q: 自动模式不工作？

A: 请确保：
1. 系统支持主题检测（Windows 10+, macOS 10.14+, Linux with GTK）
2. 系统已正确设置深色/浅色模式
3. 重启 MeowParser 应用

### Q: 如何手动编辑主题配置？

A: 编辑 `.meowparser/theme_settings.json` 文件：

```json
{
  "theme": "dark"
}
```

然后重启应用。

### Q: 主题切换后部分窗口没有更新？

A: 关闭所有 MeowParser 窗口（窗口管理器、配置编辑器等），然后重新打开。

### Q: 可以自定义主题颜色吗？

A: 目前不支持自定义颜色，但你可以修改 `meow_parser/ui/styles.py` 文件中的 `BREEZE_DARK_STYLE` 或 `BREEZE_LIGHT_STYLE` 常量。

---

## 更新日志

### v2.3.0 (2026-03-30)

- ✨ 新增自动主题切换功能
- 🎨 新增浅色主题
- 🌓 支持跟随系统主题
- 🔄 自动监控系统主题变化
- 💾 保存用户主题偏好

---

## 反馈和建议

如果你有任何问题或建议，请：
- 提交 Issue
- 查看文档
- 参与讨论

---

**MeowParser - 让文本处理更优雅！** 🐱✨
