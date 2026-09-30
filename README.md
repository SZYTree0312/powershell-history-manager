# PowerShell 历史管理器 v1.0

一个单文件的小工具，用来**查看和管理 PowerShell 的命令历史**。

PowerShell 的历史记录存在 `ConsoleHost_history.txt` 里，按 `↑` 键翻的就是它。
系统自带的 `Clear-History` 只清当前会话的内存，**清不掉这个文件** ——
想真正删掉某条带密码、带内网地址的命令，得直接改这个文件。

这个工具就是干这个的。图形界面，不用记路径、不用手改文本。

## 功能

| 功能 | 说明 |
|---|---|
| 查看 | 列出全部历史命令，超长命令自动截断显示（完整内容仍保留） |
| 搜索 | 输入关键词实时过滤 |
| 复制 | 单击选中、双击直接复制；支持多选，一次复制多条 |
| 导出 | 导出为 CSV（带 BOM，Excel 打开不乱码） |
| 彻底删除 | 从**原始历史文件**里永久移除选中命令 |
| 清空全部 | 抹掉整个 `ConsoleHost_history.txt` |

## 它动的是哪个文件

```
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

通常是 `C:\Users\<你>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`。

读取时优先按 UTF-8，失败自动回退 GBK。写回统一用 UTF-8。

## 安装与运行

**方式一：直接用打包好的 exe**

到 [Releases](../../releases) 页面下载 `PS历史管理器1.0.exe`，双击即可。
免安装、免 Python 环境。首次运行 Windows 可能弹 SmartScreen 提示 ——
选「更多信息」→「仍要运行」。

**方式二：从源码跑**

只依赖 Python 标准库（`tkinter`），不需要 `pip install` 任何东西：

```bash
python powershell_history_manager.py
```

要求 Python 3.8+，Windows 系统自带 tkinter。

## 自己打包

```bash
pip install pyinstaller
pyinstaller "PS历史管理器1.0.spec"
```

产物在 `dist/`。仓库里另外两个 `.spec`（`PS_History_Manager.spec`、
`PowerShell历史管理器.spec`）只是换了输出名的等价配置，用哪个都行。

## 注意

- **删除和清空是不可恢复的**，改的是硬盘上的真实文件，不进回收站。界面上有二次确认。
- 操作前**先关掉所有 PowerShell 窗口**。文件被占用时会写入失败（程序会提示）。
- 建议先「导出 CSV」备份一份再动手删。
- 只读操作（查看 / 搜索 / 复制 / 导出）随便用，不会改任何东西。

## 许可

MIT
