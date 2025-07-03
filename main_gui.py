import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pyperclip
import webbrowser

# 加密后的核心逻辑模块（需用 Cython 编译为 .pyd）
import core_logic

# 换行符显示与真实值映射
EOL_OPTIONS = {
    "LF (\\n)": "\n",
    "CRLF (\\r\\n)": "\r\n",
    "CR (\\r)": "\r"
}

def select_folder():
    path = filedialog.askdirectory()
    if path:
        folder_var.set(path)

def run_check(only_non_matching=False):
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("错误", "请选择有效的文件夹路径。")
        return

    suffixes = [s.strip().lower() for s in suffix_var.get().split(',') if s.strip()]
    target_encoding = encoding_var.get().lower()
    target_eol_display = eol_display_var.get()

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"🔍 正在检查: {folder}\n\n")

    file_count = 0
    mismatch_count = 0

    for root, _, files in os.walk(folder):
        for file in files:
            if suffixes and not any(file.lower().endswith(sfx) for sfx in suffixes):
                continue

            file_path = os.path.join(root, file)
            try:
                enc, conf = core_logic.detect_encoding(file_path)
                eol = core_logic.detect_eol(file_path, enc or 'utf-8')  # 返回显示名

                file_count += 1

                encoding_match = enc.lower() == target_encoding
                eol_match = eol == target_eol_display
                mismatch = not (encoding_match and eol_match)

                if only_non_matching and not mismatch:
                    continue

                status = "❌" if mismatch else "✅"
                result_text.insert(tk.END,
                    f"{status} {file_path}\n"
                    f"  编码: {enc}（置信度 {conf:.2f}）\n"
                    f"  换行符: {eol}\n\n"
                )

                if mismatch:
                    mismatch_count += 1

            except Exception as e:
                result_text.insert(tk.END, f"[错误] {file_path} -> {e}\n\n")

    result_text.insert(tk.END, f"📊 总文件数：{file_count} 个\n")
    result_text.insert(tk.END, f"🚫 不符合条件文件数：{mismatch_count} 个\n")

def convert_all():
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("错误", "请选择有效的文件夹路径。")
        return

    suffixes = [s.strip().lower() for s in suffix_var.get().split(',') if s.strip()]
    target_encoding = encoding_var.get()
    target_eol = EOL_OPTIONS[eol_display_var.get()]

    converted = 0
    failed = []

    for root, _, files in os.walk(folder):
        for file in files:
            if suffixes and not any(file.lower().endswith(sfx) for sfx in suffixes):
                continue

            file_path = os.path.join(root, file)
            success, err = core_logic.convert_file(file_path, target_encoding, target_eol)
            if success:
                converted += 1
            else:
                failed.append((file_path, err))

    result_text.insert(tk.END, f"\n🔧 转换完成：{converted} 个文件\n")
    if failed:
        result_text.insert(tk.END, f"❌ 转换失败 {len(failed)} 个文件:\n")
        for f, e in failed:
            result_text.insert(tk.END, f"{f} 错误: {e}\n")

def copy_results():
    content = result_text.get(1.0, tk.END)
    if content.strip():
        pyperclip.copy(content)
        messagebox.showinfo("提示", "结果已复制到剪贴板。")
    else:
        messagebox.showwarning("提示", "没有内容可以复制。")

def open_github():
    webbrowser.open("https://github.com/yizhishiliu")

if __name__ == '__main__':
    window = tk.Tk()
    window.title("编码与换行符检测与转换工具")
    window.geometry("900x720")

    folder_var = tk.StringVar()
    suffix_var = tk.StringVar()
    encoding_var = tk.StringVar(value='utf-8')
    eol_display_var = tk.StringVar(value="LF (\\n)")

    tk.Label(window, text="📁 选择文件夹:").pack(anchor='w', padx=10, pady=5)
    folder_frame = tk.Frame(window)
    folder_frame.pack(fill='x', padx=10)
    tk.Entry(folder_frame, textvariable=folder_var, width=80).pack(side='left', expand=True, fill='x')
    tk.Button(folder_frame, text="浏览", command=select_folder).pack(side='left', padx=5)

    tk.Label(window, text="📄 文件后缀（如 .py,.txt，可选）:").pack(anchor='w', padx=10, pady=5)
    tk.Entry(window, textvariable=suffix_var).pack(fill='x', padx=10)

    options_frame = tk.Frame(window)
    options_frame.pack(fill='x', padx=10, pady=10)
    tk.Label(options_frame, text="🎯 目标编码:").grid(row=0, column=0, padx=5)
    tk.OptionMenu(options_frame, encoding_var, 'utf-8', 'gbk', 'utf-16', 'big5').grid(row=0, column=1, padx=5)
    tk.Label(options_frame, text="🎯 目标换行符:").grid(row=0, column=2, padx=5)
    tk.OptionMenu(options_frame, eol_display_var, *EOL_OPTIONS.keys()).grid(row=0, column=3, padx=5)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="🔍 检测文件", command=lambda: run_check(False), width=20).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="⚠️ 仅显示不符合", command=lambda: run_check(True), width=20).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="🔧 转换文件", command=convert_all, width=20).grid(row=0, column=2, padx=10)
    tk.Button(button_frame, text="📋 复制结果", command=copy_results, width=20).grid(row=0, column=3, padx=10)
    tk.Button(button_frame, text="🧹 清空结果", command=lambda: result_text.delete(1.0, tk.END), width=20).grid(row=0, column=4, padx=10)

    result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Consolas", 10))
    result_text.pack(expand=True, fill='both', padx=10, pady=10)

    link = tk.Label(window, text="GitHub 仓库: https://github.com/yizhishiliu", fg="blue", cursor="hand2")
    link.pack(pady=5)
    link.bind("<Button-1>", lambda e: open_github())

    window.mainloop()
