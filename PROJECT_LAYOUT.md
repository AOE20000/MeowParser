# MeowParser 项目结构

## 根目录文件说明

### 核心文件

- `meow_parser.py` - 程序主入口
- `requirements_pyqt6.txt` - Python 依赖列表
- `LICENSE` - 开源协议
- `README.md` - 项目主文档
- `.gitignore` - Git 忽略配置

### 运行脚本

- `run.bat` - Windows 运行脚本
- `run.sh` - Linux/macOS 运行脚本

### 构建相关

- `build.py` - 跨平台打包脚本（推荐）
- `build_windows.bat` - Windows 打包脚本
- `build_linux.sh` - Linux 打包脚本
- `meow_parser.spec` - PyInstaller 配置
- `BUILD_GUIDE.md` - 详细打包指南
- `QUICK_BUILD.md` - 快速打包指南

### 依赖安装

- `install_build_deps.bat` - Windows 构建依赖安装
- `install_build_deps.sh` - Linux 构建依赖安装
- `install_breeze.bat` - BreezeStyleSheets 安装（可选）

### 测试文件

- `test_meow_rules.py` - 规则测试套件（30+ 用例）
- `test_single_text.py` - 单文本测试工具
- `TEST_GUIDE.md` - 测试指南

---

## 目录结构

```
MeowParser/
├── meow_parser/              # 核心代码包
│   ├── core/                 # 核心模块
│   │   ├── config_manager.py    # 配置管理
│   │   ├── text_processor.py    # 文本处理
│   │   ├── instance_lock.py     # 单实例锁
│   │   └── privilege.py         # 权限管理
│   ├── ui/                   # UI 模块
│   │   ├── tray_icon.py         # 系统托盘
│   │   ├── floating_window.py   # 悬浮窗
│   │   ├── window_selector.py   # 窗口选择器
│   │   ├── config_editor.py     # 配置编辑器
│   │   ├── debug_window.py      # 调试窗口
│   │   └── styles.py            # 样式管理
│   ├── platform/             # 平台特定功能
│   │   ├── windows.py           # Windows 平台
│   │   ├── linux.py             # Linux 平台
│   │   └── macos.py             # macOS 平台
│   └── app.py                # 主应用逻辑
│
├── .meowparser/              # 配置目录
│   ├── rules/                # 规则配置文件
│   │   └── default.json      # 默认规则
│   ├── window_settings.json  # 窗口设置
│   └── theme_settings.json   # 主题设置
│
├── docs/                     # 文档目录
│   ├── CHANGELOG.md          # 更新日志
│   ├── QUICKSTART.md         # 快速开始
│   ├── CUSTOM_TRIGGER_GUIDE.md  # 自定义触发器指南
│   ├── THEME_GUIDE.md        # 主题切换指南
│   ├── PRIVILEGE_ELEVATION.md   # 权限提升说明
│   ├── RULE_GROUPS_GUIDE.md  # 规则组指南
│   └── archive/              # 归档文档（开发过程记录）
│
├── tests/                    # 测试目录
│   ├── test_theme.py         # 主题测试
│   ├── test_menu_theme.py    # 菜单主题测试
│   └── test_privilege.py     # 权限测试
│
├── build/                    # 构建临时文件（自动生成）
├── dist/                     # 打包输出目录（自动生成）
└── __pycache__/              # Python 缓存（自动生成）
```

---

## 文件用途分类

### 必需文件（运行）

```
meow_parser/          # 核心代码
meow_parser.py        # 入口
.meowparser/          # 配置
requirements_pyqt6.txt # 依赖
run.bat / run.sh      # 运行脚本
```

### 必需文件（开发）

```
上述所有文件 +
test_meow_rules.py    # 测试
test_single_text.py   # 测试
BUILD_GUIDE.md        # 构建指南
```

### 可选文件

```
install_*.bat/sh      # 依赖安装脚本
build_*.bat/sh        # 平台特定构建脚本
QUICK_BUILD.md        # 快速构建指南
```

---

## 清理命令

### 清理构建文件

```bash
# Windows
rmdir /s /q build dist __pycache__
del /q *.pyc

# Linux/macOS
rm -rf build dist __pycache__
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete
```

### 清理配置文件

```bash
# Windows
rmdir /s /q .meowparser

# Linux/macOS
rm -rf .meowparser
```

---

## 最小部署

如果只需要运行程序，最小文件集：

```
meow_parser/          # 核心代码（必需）
meow_parser.py        # 入口（必需）
requirements_pyqt6.txt # 依赖（必需）
run.bat / run.sh      # 运行脚本（推荐）
README.md             # 说明文档（推荐）
LICENSE               # 许可证（推荐）
```

---

## 文档位置

### 用户文档

- `README.md` - 项目主文档
- `docs/QUICKSTART.md` - 快速开始
- `docs/CUSTOM_TRIGGER_GUIDE.md` - 自定义触发器
- `docs/THEME_GUIDE.md` - 主题切换
- `docs/PRIVILEGE_ELEVATION.md` - 权限说明
- `docs/RULE_GROUPS_GUIDE.md` - 规则组指南

### 开发文档

- `BUILD_GUIDE.md` - 详细构建指南
- `QUICK_BUILD.md` - 快速构建
- `TEST_GUIDE.md` - 测试指南
- `PROJECT_LAYOUT.md` - 项目结构（本文档）
- `docs/CHANGELOG.md` - 更新日志

### 归档文档

- `docs/archive/` - 开发过程文档、版本更新记录、详细技术说明等

---

## 更新日志

### v2.3.0 (2026-03-30)

- 整理项目结构
- 移动非必要文档到 `docs/archive/`
- 移动测试文件到 `tests/`
- 简化根目录文件
- 创建项目结构说明文档

---

**保持项目整洁，便于维护！** 📁✨
