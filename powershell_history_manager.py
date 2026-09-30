#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PowerShell 历史管理器 v1.0
功能：查看、搜索、复制、导出、彻底删除、清空原始历史文件
"""

import os
import sys
import csv
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class PowerShellHistoryManager:
    """核心逻辑：负责读取和修改硬盘上的原始历史文件"""

    def __init__(self):
        appdata = os.environ.get('APPDATA', '')
        self.history_path = Path(appdata) / r"Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"

    def read_history(self):
        """从原始文件读取历史"""
        commands = []
        if not self.history_path.exists():
            return commands, f"未找到历史文件:\n{self.history_path}"

        try:
            # 尝试 utf-8 读取，如果失败则用系统默认编码
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(self.history_path, 'r', encoding='gbk') as f:
                    lines = f.readlines()

            for line in lines:
                cmd = line.strip()
                if cmd:
                    commands.append(cmd)
            return commands, None
        except PermissionError:
            return [], "权限被拒绝！请关闭所有正在运行的 PowerShell 窗口后再试。"
        except Exception as e:
            return [], f"读取错误: {str(e)}"

    def write_history(self, commands):
        """将修改后的历史写回原始文件（彻底删除/清空的核心）"""
        try:
            # 确保目录存在
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_path, 'w', encoding='utf-8') as f:
                for cmd in commands:
                    f.write(cmd + '\n')
            return True, None
        except PermissionError:
            return False, "写入失败：文件被占用！请关闭所有正在运行的 PowerShell 窗口后重试。"
        except Exception as e:
            return False, f"写入错误: {str(e)}"


class HistoryManagerGUI:
    """GUI 界面类"""

    def __init__(self, root):
        self.root = root
        self.root.title("PowerShell 历史管理器 v1.0")
        self.root.geometry("850x600")
        self.manager = PowerShellHistoryManager()
        
        self.all_commands = []
        self.filtered_commands = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # 1. 顶部搜索与操作栏
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="🔍 搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.filter_data())

        ttk.Button(top_frame, text="🔄 刷新", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # 2. 中间列表区域 (Treeview)
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(list_frame, columns=('index', 'command'), show='headings', selectmode='extended')
        self.tree.heading('index', text='#')
        self.tree.heading('command', text='命令内容 (双击可复制)')
        self.tree.column('index', width=50, anchor=tk.CENTER, stretch=False)
        self.tree.column('command', width=700)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 双击复制
        self.tree.bind("<Double-1>", self.copy_selected)

        # 3. 底部按钮栏
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="📋 复制选中", command=self.copy_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 导出 CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        # 危险操作区（用红色或明显提示）
        ttk.Button(btn_frame, text="🗑️ 彻底删除选中", command=self.delete_selected_permanently).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="💥 清空全部历史", command=self.clear_all_permanently).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(btn_frame, text="就绪", foreground="gray")
        self.status_label.pack(side=tk.RIGHT)

    def load_data(self):
        self.all_commands, error = self.manager.read_history()
        if error:
            messagebox.showerror("加载失败", error)
            self.status_label.config(text="加载失败", foreground="red")
        else:
            self.filtered_commands = list(self.all_commands)
            self.update_tree()
            self.status_label.config(text=f"✅ 已加载 {len(self.all_commands)} 条记录", foreground="green")

    def filter_data(self):
        keyword = self.search_var.get().lower()
        if not keyword:
            self.filtered_commands = list(self.all_commands)
        else:
            self.filtered_commands = [cmd for cmd in self.all_commands if keyword in cmd.lower()]
        self.update_tree()

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, cmd in enumerate(self.filtered_commands, 1):
            # 界面上截断过长的命令，但把完整命令存在 tags 里
            display_cmd = (cmd[:90] + '...') if len(cmd) > 90 else cmd
            self.tree.insert('', tk.END, values=(i, display_cmd), tags=(cmd,))

    def copy_selected(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        
        # 获取所有选中项的完整命令
        cmds_to_copy = []
        for item in selection:
            full_cmd = self.tree.item(item)['tags'][0]
            cmds_to_copy.append(full_cmd)
            
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(cmds_to_copy))
        self.status_label.config(text=f"📋 已复制 {len(cmds_to_copy)} 条命令到剪贴板!", foreground="blue")

    def delete_selected_permanently(self):
        """彻底删除选中的命令（修改原始文件）"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先在列表中选择要删除的命令。")
            return

        count = len(selection)
        if not messagebox.askyesno("⚠️ 确认彻底删除", 
                                   f"确定要从【原始历史文件】中永久删除这 {count} 条记录吗？\n\n此操作不可恢复！"):
            return

        # 1. 获取要删除的命令
        cmds_to_delete = set()
        for item in selection:
            cmds_to_delete.add(self.tree.item(item)['tags'][0])

        # 2. 从内存总列表中移除
        self.all_commands = [cmd for cmd in self.all_commands if cmd not in cmds_to_delete]

        # 3. 写回原始文件
        success, error = self.manager.write_history(self.all_commands)
        if success:
            self.load_data() # 刷新界面
            self.status_label.config(text=f"🗑️ 已彻底删除 {count} 条记录", foreground="red")
        else:
            messagebox.showerror("删除失败", error)

    def clear_all_permanently(self):
        """清空全部历史（修改原始文件）"""
        if not self.all_commands:
            messagebox.showinfo("提示", "历史已经是空的了。")
            return

        if not messagebox.askyesno("💥 危险操作确认", 
                                   "确定要【清空所有】PowerShell 历史记录吗？\n\n这将抹除原始文件中的所有痕迹，不可恢复！"):
            return

        # 1. 清空内存
        self.all_commands = []

        # 2. 写回原始文件（写入空列表，即清空文件）
        success, error = self.manager.write_history(self.all_commands)
        if success:
            self.load_data()
            self.status_label.config(text="💥 已清空全部历史", foreground="red")
        else:
            messagebox.showerror("清空失败", error)

    def export_csv(self):
        if not self.filtered_commands:
            messagebox.showinfo("提示", "没有可导出的数据")
            return
            
        default_name = f"PS_History_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Index', 'Command'])
                    for i, cmd in enumerate(self.filtered_commands, 1):
                        writer.writerow([i, cmd])
                self.status_label.config(text=f"📤 导出成功: {os.path.basename(path)}", foreground="green")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))

def main():
    # 开启 Windows 高 DPI 支持，防止界面模糊
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = HistoryManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()