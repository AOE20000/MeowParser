# MeowParser 权限提升功能

## 功能概述

MeowParser 现在支持自动请求管理员/root 权限。如果程序检测到没有足够的权限，会自动弹出 UAC（Windows）或请求 sudo（Linux/macOS）来提升权限。

---

## 工作原理

### 启动流程

```
启动程序
    ↓
检查是否有管理员/root权限
    ↓
    ├─ 是 → 继续启动
    └─ 否 → 请求权限提升
            ↓
            ├─ 成功 → 以新权限重启程序
            └─ 失败 → 显示错误消息并退出
```

### Windows

1. 检测到无管理员权限
2. 调用 `ShellExecuteW` 使用 `runas` 动词
3. 弹出 UAC 对话框
4. 用户点击"是" → 以管理员身份启动新进程
5. 原进程退出

### Linux/macOS

1. 检测到无 root 权限
2. 使用 `sudo` 重新执行程序
3. 提示用户输入密码
4. 密码正确 → 以 root 权限替换当前进程
5. 密码错误或取消 → 显示错误消息并退出

---

## 使用方法

### 正常启动（推荐）

**Windows:**
```bash
# 直接双击运行
MeowParser.exe

# 或命令行运行
python meow_parser.py
```

程序会自动弹出 UAC 对话框请求管理员权限。

**Linux/macOS:**
```bash
# 直接运行
python meow_parser.py

# 程序会提示输入密码
```

程序会自动使用 sudo 请求 root 权限。

### 手动以管理员身份运行

**Windows:**
```bash
# 方法1: 右键菜单
右键 MeowParser.exe → 以管理员身份运行

# 方法2: 命令行
# 以管理员身份打开 PowerShell/CMD
python meow_parser.py
```

**Linux/macOS:**
```bash
# 使用 sudo
sudo python meow_parser.py
```

---

## 技术实现

### 权限检查

```python
def is_admin():
    """检查是否有管理员/root权限"""
    if sys.platform == 'win32':
        return ctypes.windll.shell32.IsUserAnAdmin()
    else:
        return os.geteuid() == 0
```

### Windows 权限提升

```python
def request_admin_windows():
    """Windows: 请求管理员权限"""
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",  # 以管理员身份运行
        script,
        params,
        None,
        1  # SW_SHOWNORMAL
    )
    return ret > 32
```

### Unix 权限提升

```python
def request_admin_unix():
    """Unix/Linux/macOS: 请求 root 权限"""
    # 使用 sudo 重新启动
    os.execvp('sudo', ['sudo'] + args)
```

---

## 文件结构

```
meow_parser/
├── core/
│   ├── privilege.py          # 权限管理模块（新增）
│   └── __init__.py           # 导出权限函数
├── app.py                    # 移除启动时权限检查
├── __main__.py               # 添加权限检查
└── meow_parser.py            # 添加权限检查
```

---

## 权限提升对话框

### Windows UAC

```
┌─────────────────────────────────────┐
│  用户账户控制                        │
├─────────────────────────────────────┤
│  你要允许此应用对你的设备进行更改吗？ │
│                                     │
│  MeowParser                         │
│  已验证的发布者: Unknown             │
│                                     │
│  [是(Y)]  [否(N)]                   │
└─────────────────────────────────────┘
```

### Linux/macOS sudo

```
MeowParser 需要 root 权限才能运行
请输入密码以继续...
[sudo] password for user: _
```

---

## 错误处理

### 权限被拒绝

**Windows:**
- 用户点击 UAC 的"否"
- 显示错误对话框
- 程序退出

**Linux/macOS:**
- 用户取消密码输入（Ctrl+C）
- 密码错误
- 显示错误消息
- 程序退出

### 错误消息

```
┌─────────────────────────────────────┐
│  MeowParser - 权限不足               │
├─────────────────────────────────────┤
│  MeowParser 需要管理员/root 权限才能 │
│  运行。                              │
│                                     │
│  权限提升失败或被拒绝。               │
│                                     │
│  Windows: 请右键程序，选择"以管理员   │
│  身份运行"                           │
│  Linux/macOS: 请使用 sudo 运行程序   │
│                                     │
│  [确定]                              │
└─────────────────────────────────────┘
```

---

## 安全考虑

### 为什么需要管理员权限？

MeowParser 需要管理员/root 权限来：

1. **全局键盘监听**
   - 监听所有应用的键盘输入
   - 需要系统级权限

2. **输入模拟**
   - 向其他应用发送键盘事件
   - 需要提升权限

3. **窗口管理**
   - 获取其他应用的窗口信息
   - 某些系统需要管理员权限

### 安全措施

1. **最小权限原则**
   - 仅在必要时请求权限
   - 不执行危险操作

2. **透明度**
   - 明确告知用户为何需要权限
   - 开源代码，可审查

3. **用户控制**
   - 用户可以拒绝权限请求
   - 程序不会强制获取权限

---

## 常见问题

### Q: 为什么每次启动都要请求权限？

A: 这是正常行为。为了安全，操作系统不会永久授予管理员权限。每次启动都需要用户确认。

### Q: 可以跳过权限请求吗？

A: 不可以。MeowParser 的核心功能（键盘监听和输入模拟）必须要管理员权限才能工作。

### Q: 如何避免每次都弹出 UAC？

**Windows:**
1. 创建快捷方式
2. 右键快捷方式 → 属性
3. 高级 → 勾选"以管理员身份运行"
4. 确定

**Linux/macOS:**
```bash
# 创建别名
alias meowparser='sudo python /path/to/meow_parser.py'

# 或配置 sudo 免密码（不推荐）
```

### Q: 权限提升失败怎么办？

**Windows:**
1. 确保当前用户在管理员组
2. 检查 UAC 设置是否被禁用
3. 尝试右键"以管理员身份运行"

**Linux/macOS:**
1. 确保用户在 sudoers 列表中
2. 检查 sudo 配置
3. 尝试手动使用 sudo 运行

### Q: 程序会不会滥用管理员权限？

A: 不会。MeowParser 是开源软件，所有代码都可以审查。程序只使用权限来实现键盘监听和输入模拟功能，不会执行其他危险操作。

---

## 开发者说明

### 添加权限检查到新入口

如果你创建了新的程序入口，需要添加权限检查：

```python
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from meow_parser.core.privilege import ensure_admin

def main():
    # 检查权限
    if not ensure_admin():
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "权限不足",
            "需要管理员/root 权限"
        )
        sys.exit(1)
    
    # 继续启动...
```

### 测试权限提升

```bash
# 测试 Windows
python meow_parser.py

# 测试 Linux/macOS
python meow_parser.py
```

---

## 更新日志

### v2.3.0 (2026-03-30)

- ✨ 新增自动权限提升功能
- 🔒 Windows: 自动弹出 UAC 对话框
- 🔒 Linux/macOS: 自动使用 sudo 请求权限
- 🚫 移除托盘菜单中的权限状态显示
- 🚫 移除托盘菜单中的快捷键提示
- ✅ 启动时强制检查管理员权限

---

## 参考资料

- [Windows UAC](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/)
- [Linux sudo](https://www.sudo.ws/man/1.8.15/sudo.man.html)
- [Python ctypes](https://docs.python.org/3/library/ctypes.html)
- [Python os.execvp](https://docs.python.org/3/library/os.html#os.execvp)

---

## 总结

✅ 自动请求管理员/root 权限  
✅ 跨平台支持（Windows/Linux/macOS）  
✅ 用户友好的错误提示  
✅ 安全可靠的权限管理  
✅ 开源透明，可审查  

**实现状态：** 已完成  
**测试状态：** 待测试  
**安全性：** 良好
