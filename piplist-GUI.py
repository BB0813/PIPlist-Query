# 基础库导入
import os
import re
import json
import yaml
import time
import locale
import threading
import subprocess
from datetime import datetime

# 第三方库导入
import chardet
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from filelock import FileLock

# GUI相关导入
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# 在文件开头添加新的导入
import psutil
import venv
import pkg_resources
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Event

class PipListGUI:
    def __init__(self):
        # 设置matplotlib后端
        plt.switch_backend('Agg')
        self.VERSION = "1.0.0"
        self.monitor_running = False
        
        self.root = ttk.Window(
            title=f"piplist-GUI工具 v{self.VERSION}",
            themename="litera",
            size=(800, 600),
            position=(100, 50)
        )
        self.setup_gui()
        self.create_menu()

    def generate_dependency_graph(self):
        try:
            # 清理之前的图形
            plt.close('all')
            
            # 创建有向图
            G = nx.DiGraph()
            packages = self.get_installed_packages()
            
            # 用于存储依赖计数
            dep_count = {}
            
            # 收集依赖关系
            for pkg in packages:
                pkg_name = pkg[0]
                dep_count[pkg_name] = 0
                G.add_node(pkg_name)
                
                try:
                    result = subprocess.run(['pip', 'show', pkg_name], stdout=subprocess.PIPE)
                    output = result.stdout.decode('utf-8')
                    requires = re.search(r'Requires: (.+)', output)
                    if requires:
                        deps = [d.strip() for d in requires.group(1).split(',') if d.strip()]
                        for dep in deps:
                            G.add_edge(pkg_name, dep)
                            dep_count[dep] = dep_count.get(dep, 0) + 1
                except Exception:
                    continue

            # 创建图形
            fig = plt.figure(figsize=(20, 15))
            
            # 使用spring_layout布局，增加节点间距
            pos = nx.spring_layout(G, k=2.5, iterations=150, seed=42)
            
            # 计算节点大小（基于依赖数量）
            node_sizes = [1000 + (dep_count.get(node, 0) * 100) for node in G.nodes()]
            
            # 计算节点颜色（基于依赖数量）
            node_colors = [dep_count.get(node, 0) for node in G.nodes()]
            
            # 绘制节点
            nodes = nx.draw_networkx_nodes(G, pos,
                                         node_size=node_sizes,
                                         node_color=node_colors,
                                         cmap=plt.cm.YlOrRd,
                                         alpha=0.7)
            
            # 绘制边
            nx.draw_networkx_edges(G, pos,
                                 edge_color='lightgray',
                                 arrows=True,
                                 arrowsize=10,
                                 alpha=0.3,
                                 min_source_margin=20,
                                 min_target_margin=20)
            
            # 优化标签显示
            labels = {node: node for node in G.nodes()}
            label_pos = {k: (v[0], v[1] + 0.08) for k, v in pos.items()}  # 将标签位置略微上移
            nx.draw_networkx_labels(G, label_pos,
                                  labels=labels,
                                  font_size=8,
                                  font_family='sans-serif',
                                  bbox=dict(facecolor='white', 
                                          edgecolor='none', 
                                          alpha=0.7,
                                          pad=0.5))
            
            # 删除重复的标签绘制代码，只保留一次
            nx.draw_networkx_labels(G, label_pos,
                                  labels=labels,
                                  font_size=8,
                                  font_family='sans-serif',
                                  bbox=dict(facecolor='white', 
                                          edgecolor='none', 
                                          alpha=0.7,
                                          pad=0.5))
            
            # 保存前确保设置了正确的布局
            plt.tight_layout()
            
            # 保存图形
            file_path = os.path.join(self.save_directory, 'dependency_graph.png')
            plt.savefig(file_path,
                       dpi=300,
                       bbox_inches='tight',
                       pad_inches=0.5)
            
            # 清理资源
            plt.close(fig)
            
            self.show_message("成功", "依赖关系图已生成，节点大小和颜色深浅表示被依赖的次数")
        except Exception as e:
            self.show_message("错误", f"生成依赖图失败: {str(e)}", "error")

    def setup_gui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=BOTH, expand=YES)

        # 创建标题
        title_label = ttk.Label(
            self.main_frame,
            text="Python环境管理工具",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=10)

        # 创建选项变量和选项框
        self.option_var = ttk.StringVar(value='all')
        self.create_options_frame()

        # 创建按钮
        self.create_button_frame()

        # 创建进度条
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate',
            style='primary.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=X, padx=20, pady=10)

        # 创建状态栏
        self.status_bar = ttk.Label(
            self.root,
            text="就绪",
            relief=SUNKEN,
            padding=(10, 5)
        )
        self.status_bar.pack(side=BOTTOM, fill=X)

    def create_options_frame(self):
        options_frame = ttk.LabelFrame(
            self.main_frame,
            text="选择检测类型",
            padding="10"
        )
        options_frame.pack(fill=X, padx=20, pady=10)

        options = [
            ("所有信息 (all)", 'all'),
            ("编程语言信息 (languages)", 'languages'),
            ("Python库信息 (packages)", 'packages'),
            ("前端框架信息 (frameworks)", 'frameworks'),
            ("依赖匹配信息 (requirements)", 'requirements')
        ]

        for text, value in options:
            ttk.Radiobutton(
                options_frame,
                text=text,
                variable=self.option_var,
                value=value,
                style='primary'
            ).pack(anchor=W, pady=5)

    def create_button_frame(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        submit_button = ttk.Button(
            button_frame,
            text="查询并保存信息",
            command=self.on_select,
            style='primary.TButton',
            width=20
        )
        submit_button.pack(side=LEFT, padx=5)

    def create_menu(self):
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出JSON", command=self.export_as_json)
        file_menu.add_command(label="导出YAML", command=self.export_as_yaml)
        file_menu.add_command(label="生成依赖图", command=self.generate_dependency_graph)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 工具菜单
        tools_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="包管理", command=self.open_package_manager)
        tools_menu.add_command(label="虚拟环境管理", command=self.manage_venv)
        tools_menu.add_command(label="安全检查", command=self.security_check)
        tools_menu.add_command(label="性能监控", command=self.performance_monitor)

    def show_message(self, title, message, message_type="info"):
        if message_type == "info":
            Messagebox.show_info(message, title)
        elif message_type == "error":
            Messagebox.show_error(message, title)
        elif message_type == "warning":
            Messagebox.show_warning(message, title)

    # 数据处理方法
    def get_installed_packages(self):
        result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
        packages = result.stdout.decode('utf-8').split('\n')[2:]
        return [package.split() for package in packages if package]

    def get_requirements_packages(self, file_path='requirements.txt'):
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']

            with open(file_path, 'r', encoding=encoding) as file:
                requirements = file.readlines()

            return [re.sub(r'\s+', ' ', line.strip()).split('==') 
                   for line in requirements if line.strip()]
        except FileNotFoundError:
            return []

    def get_language_version(self, command, pattern):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8').strip()
            match = re.search(pattern, output)
            return match.group(1) if match else "版本信息未找到"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "版本信息未找到"

    def get_installed_languages(self):
        languages = []
        language_configs = [
            (['python', '--version'], r'Python (\d+\.\d+\.\d+)', 'Python'),
            (['java', '-version'], r'version "(\d+\.\d+\.\d+_\d+)"', 'Java'),
            (['node', '--version'], r'v(\d+\.\d+\.\d+)', 'Node.js'),
            # ... 其他语言配置
        ]

        for command, pattern, name in language_configs:
            version = self.get_language_version(command, pattern)
            languages.append([name, version])

        return languages

    def get_installed_front_end_frameworks(self):
        frameworks = []
        framework_configs = [
            (['npm', 'list', '-g', 'vue-cli'], r'vue-cli@(\d+\.\d+\.\d+)', 'Vue.js'),
            (['npm', 'list', '-g', 'create-react-app'], r'create-react-app@(\d+\.\d+\.\d+)', 'React.js'),
            (['npm', 'list', '-g', '@angular/cli'], r'@angular/cli@(\d+\.\d+\.\d+)', 'Angular'),
            # ... 其他框架配置
        ]

        for command, pattern, name in framework_configs:
            version = self.get_language_version(command, pattern)
            frameworks.append([name, version])

        return frameworks

    def save_to_excel(self, package_list, languages, frameworks, requirements, selected_option='all'):
        os.makedirs(self.save_directory, exist_ok=True)
    
        data_configs = {
            'languages': ('编程语言.xlsx', ['编程语言', '版本号'], languages),
            'packages': ('Python库.xlsx', ['包名', '版本号'], package_list),
            'frameworks': ('前端框架.xlsx', ['前端框架', '版本号'], frameworks),
            'requirements': ('依赖匹配.xlsx', ['包名', '要求版本', '已安装版本', '是否匹配'], self._process_requirements(package_list, requirements))
        }
    
        for key, (filename, columns, data) in data_configs.items():
            if selected_option in ['all', key]:
                file_path = os.path.join(self.save_directory, filename)
                with FileLock('lock'):
                    pd.DataFrame(data, columns=columns).to_excel(file_path, index=False)

    def export_as_json(self):
        try:
            data = {
                'packages': self.get_installed_packages(),
                'languages': self.get_installed_languages(),
                'frameworks': self.get_installed_front_end_frameworks()
            }
            file_path = os.path.join(self.save_directory, 'export.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.show_message("成功", f"数据已导出到桌面: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_message("错误", f"导出失败: {str(e)}", "error")

    def export_as_yaml(self):
        try:
            data = {
                'packages': self.get_installed_packages(),
                'languages': self.get_installed_languages(),
                'frameworks': self.get_installed_front_end_frameworks()
            }
            file_path = os.path.join(self.save_directory, 'export.yaml')
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            self.show_message("成功", f"数据已导出到桌面: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_message("错误", f"导出失败: {str(e)}", "error")

    def generate_dependency_graph(self):
        try:
            # 清理之前的图形
            plt.close('all')
            
            # 创建有向图
            G = nx.DiGraph()
            packages = self.get_installed_packages()
            
            # 用于存储依赖计数
            dep_count = {}
            
            # 收集依赖关系
            for pkg in packages:
                pkg_name = pkg[0]
                dep_count[pkg_name] = 0
                G.add_node(pkg_name)
                
                try:
                    result = subprocess.run(['pip', 'show', pkg_name], stdout=subprocess.PIPE)
                    output = result.stdout.decode('utf-8')
                    requires = re.search(r'Requires: (.+)', output)
                    if requires:
                        deps = [d.strip() for d in requires.group(1).split(',') if d.strip()]
                        for dep in deps:
                            G.add_edge(pkg_name, dep)
                            dep_count[dep] = dep_count.get(dep, 0) + 1
                except Exception:
                    continue

            # 创建图形
            fig = plt.figure(figsize=(20, 15))
            
            # 使用spring_layout布局，增加节点间距
            pos = nx.spring_layout(G, k=2.5, iterations=150, seed=42)
            
            # 计算节点大小（基于依赖数量）
            node_sizes = [1000 + (dep_count.get(node, 0) * 100) for node in G.nodes()]
            
            # 计算节点颜色（基于依赖数量）
            node_colors = [dep_count.get(node, 0) for node in G.nodes()]
            
            # 绘制节点
            nodes = nx.draw_networkx_nodes(G, pos,
                                         node_size=node_sizes,
                                         node_color=node_colors,
                                         cmap=plt.cm.YlOrRd,
                                         alpha=0.7)
            
            # 绘制边
            nx.draw_networkx_edges(G, pos,
                                 edge_color='lightgray',
                                 arrows=True,
                                 arrowsize=10,
                                 alpha=0.3,
                                 min_source_margin=20,
                                 min_target_margin=20)
            
            # 优化标签显示
            labels = {node: node for node in G.nodes()}
            label_pos = {k: (v[0], v[1] + 0.08) for k, v in pos.items()}  # 将标签位置略微上移
            nx.draw_networkx_labels(G, label_pos,
                                  labels=labels,
                                  font_size=8,
                                  font_family='sans-serif',
                                  bbox=dict(facecolor='white', 
                                          edgecolor='none', 
                                          alpha=0.7,
                                          pad=0.5))
            
            # 删除重复的标签绘制代码，只保留一次
            nx.draw_networkx_labels(G, label_pos,
                                  labels=labels,
                                  font_size=8,
                                  font_family='sans-serif',
                                  bbox=dict(facecolor='white', 
                                          edgecolor='none', 
                                          alpha=0.7,
                                          pad=0.5))
            
            # 保存前确保设置了正确的布局
            plt.tight_layout()
            
            # 保存图形
            file_path = os.path.join(self.save_directory, 'dependency_graph.png')
            plt.savefig(file_path,
                       dpi=300,
                       bbox_inches='tight',
                       pad_inches=0.5)
            
            # 清理资源
            plt.close(fig)
            
            self.show_message("成功", "依赖关系图已生成，节点大小和颜色深浅表示被依赖的次数")
        except Exception as e:
            self.show_message("错误", f"生成依赖图失败: {str(e)}", "error")

    def setup_gui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=BOTH, expand=YES)

        # 创建标题
        title_label = ttk.Label(
            self.main_frame,
            text="Python环境管理工具",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=10)

        # 创建选项变量和选项框
        self.option_var = ttk.StringVar(value='all')
        self.create_options_frame()

        # 创建按钮
        self.create_button_frame()

        # 创建进度条
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate',
            style='primary.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=X, padx=20, pady=10)

        # 创建状态栏
        self.status_bar = ttk.Label(
            self.root,
            text="就绪",
            relief=SUNKEN,
            padding=(10, 5)
        )
        self.status_bar.pack(side=BOTTOM, fill=X)

    def create_options_frame(self):
        options_frame = ttk.LabelFrame(
            self.main_frame,
            text="选择检测类型",
            padding="10"
        )
        options_frame.pack(fill=X, padx=20, pady=10)

        options = [
            ("所有信息 (all)", 'all'),
            ("编程语言信息 (languages)", 'languages'),
            ("Python库信息 (packages)", 'packages'),
            ("前端框架信息 (frameworks)", 'frameworks'),
            ("依赖匹配信息 (requirements)", 'requirements')
        ]

        for text, value in options:
            ttk.Radiobutton(
                options_frame,
                text=text,
                variable=self.option_var,
                value=value,
                style='primary'
            ).pack(anchor=W, pady=5)

    def create_button_frame(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        submit_button = ttk.Button(
            button_frame,
            text="查询并保存信息",
            command=self.on_select,
            style='primary.TButton',
            width=20
        )
        submit_button.pack(side=LEFT, padx=5)

    def create_menu(self):
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出JSON", command=self.export_as_json)
        file_menu.add_command(label="导出YAML", command=self.export_as_yaml)
        file_menu.add_command(label="生成依赖图", command=self.generate_dependency_graph)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 工具菜单
        tools_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="包管理", command=self.open_package_manager)
        tools_menu.add_command(label="虚拟环境管理", command=self.manage_venv)
        tools_menu.add_command(label="安全检查", command=self.security_check)
        tools_menu.add_command(label="性能监控", command=self.performance_monitor)

    def show_message(self, title, message, message_type="info"):
        if message_type == "info":
            Messagebox.show_info(message, title)
        elif message_type == "error":
            Messagebox.show_error(message, title)
        elif message_type == "warning":
            Messagebox.show_warning(message, title)

    # 数据处理方法
    def get_installed_packages(self):
        result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
        packages = result.stdout.decode('utf-8').split('\n')[2:]
        return [package.split() for package in packages if package]

    def get_requirements_packages(self, file_path='requirements.txt'):
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']

            with open(file_path, 'r', encoding=encoding) as file:
                requirements = file.readlines()

            return [re.sub(r'\s+', ' ', line.strip()).split('==') 
                   for line in requirements if line.strip()]
        except FileNotFoundError:
            return []

    def get_language_version(self, command, pattern):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8').strip()
            match = re.search(pattern, output)
            return match.group(1) if match else "版本信息未找到"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "版本信息未找到"

    def get_installed_languages(self):
        languages = []
        language_configs = [
            (['python', '--version'], r'Python (\d+\.\d+\.\d+)', 'Python'),
            (['java', '-version'], r'version "(\d+\.\d+\.\d+_\d+)"', 'Java'),
            (['node', '--version'], r'v(\d+\.\d+\.\d+)', 'Node.js'),
            # ... 其他语言配置
        ]

        for command, pattern, name in language_configs:
            version = self.get_language_version(command, pattern)
            languages.append([name, version])

        return languages

    def get_installed_front_end_frameworks(self):
        frameworks = []
        framework_configs = [
            (['npm', 'list', '-g', 'vue-cli'], r'vue-cli@(\d+\.\d+\.\d+)', 'Vue.js'),
            (['npm', 'list', '-g', 'create-react-app'], r'create-react-app@(\d+\.\d+\.\d+)', 'React.js'),
            (['npm', 'list', '-g', '@angular/cli'], r'@angular/cli@(\d+\.\d+\.\d+)', 'Angular'),
            # ... 其他框架配置
        ]

        for command, pattern, name in framework_configs:
            version = self.get_language_version(command, pattern)
            frameworks.append([name, version])

        return frameworks

    def save_to_excel(self, package_list, languages, frameworks, requirements, selected_option='all'):
        save_directory = os.path.join(os.getcwd(), 'results')
        os.makedirs(save_directory, exist_ok=True)
    
        data_configs = {
            'languages': ('编程语言.xlsx', ['编程语言', '版本号'], languages),
            'packages': ('Python库.xlsx', ['包名', '版本号'], package_list),
            'frameworks': ('前端框架.xlsx', ['前端框架', '版本号'], frameworks),
            'requirements': ('依赖匹配.xlsx', ['包名', '要求版本', '已安装版本', '是否匹配'], self._process_requirements(package_list, requirements))
        }
    
        for key, (filename, columns, data) in data_configs.items():
            if selected_option in ['all', key]:
                file_path = os.path.join(save_directory, filename)
                with FileLock('lock'):
                    pd.DataFrame(data, columns=columns).to_excel(file_path, index=False)

    def _process_requirements(self, package_list, requirements):
        installed_packages_dict = {package[0]: package[1] for package in package_list}
        matched_requirements = []
        for req in requirements:
            package_name = req[0]
            req_version = req[1] if len(req) > 1 else '未指定版本'
            installed_version = installed_packages_dict.get(package_name, '未安装')
            matched_requirements.append(
                [package_name, req_version, installed_version, req_version == installed_version]
            )
        return matched_requirements

    # 事件处理方法
    def on_select(self):
        try:
            self.progress_bar.start(10)
            self.status_bar.config(text="正在处理...")
            
            selected_option = self.option_var.get()
            packages = self.get_installed_packages()
            requirements = self.get_requirements_packages()
            languages = self.get_installed_languages()
            frameworks = self.get_installed_front_end_frameworks()

            self.save_to_excel(packages, languages, frameworks, requirements, selected_option)
            
            self.progress_bar.stop()
            self.status_bar.config(text="就绪")
            self.show_message("成功", "信息已成功保存到 results 目录")
        except Exception as e:
            self.progress_bar.stop()
            self.status_bar.config(text="出错")
            self.show_message("错误", str(e), "error")

    def export_as_json(self):
        try:
            data = {
                'packages': self.get_installed_packages(),
                'languages': self.get_installed_languages(),
                'frameworks': self.get_installed_front_end_frameworks()
            }
            save_directory = os.path.join(os.getcwd(), 'results')
            os.makedirs(save_directory, exist_ok=True)
            with open(os.path.join(save_directory, 'export.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.show_message("成功", "数据已导出为JSON格式")
        except Exception as e:
            self.show_message("错误", f"导出失败: {str(e)}", "error")

    def export_as_yaml(self):
        try:
            data = {
                'packages': self.get_installed_packages(),
                'languages': self.get_installed_languages(),
                'frameworks': self.get_installed_front_end_frameworks()
            }
            save_directory = os.path.join(os.getcwd(), 'results')
            os.makedirs(save_directory, exist_ok=True)
            with open(os.path.join(save_directory, 'export.yaml'), 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            self.show_message("成功", "数据已导出为YAML格式")
        except Exception as e:
            self.show_message("错误", f"导出失败: {str(e)}", "error")

    def open_package_manager(self):
        package_window = ttk.Toplevel(self.root)
        package_window.title("包管理")
        package_window.geometry("800x600")

        # 创建搜索框和按钮
        search_frame = ttk.Frame(package_window)
        search_frame.pack(fill=X, padx=10, pady=5)
        
        search_var = ttk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=LEFT, fill=X, expand=YES)

        # 创建包列表
        list_frame = ttk.Frame(package_window)
        list_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        columns = ("包名", "当前版本", "最新版本", "状态")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill=BOTH, expand=YES)

        def search_packages():
            query = search_var.get().lower()
            tree.delete(*tree.get_children())
            for dist in pkg_resources.working_set:
                if query in dist.key.lower():
                    tree.insert("", END, values=(dist.key, dist.version, "获取中...", "已安装"))

        def install_package():
            selected = tree.selection()
            if selected:
                pkg_name = tree.item(selected[0])['values'][0]
                try:
                    subprocess.run(['pip', 'install', '--upgrade', pkg_name], check=True)
                    self.show_message("成功", f"包 {pkg_name} 安装/更新成功")
                    search_packages()
                except subprocess.CalledProcessError as e:
                    self.show_message("错误", f"安装失败: {str(e)}", "error")

        def uninstall_package():
            selected = tree.selection()
            if selected:
                pkg_name = tree.item(selected[0])['values'][0]
                if Messagebox.show_question(f"确定要卸载 {pkg_name} 吗?", "确认卸载") == "是":
                    try:
                        subprocess.run(['pip', 'uninstall', '-y', pkg_name], check=True)
                        self.show_message("成功", f"包 {pkg_name} 已卸载")
                        search_packages()
                    except subprocess.CalledProcessError as e:
                        self.show_message("错误", f"卸载失败: {str(e)}", "error")

        button_frame = ttk.Frame(package_window)
        button_frame.pack(fill=X, padx=10, pady=5)
        ttk.Button(button_frame, text="搜索", command=search_packages).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="安装/更新", command=install_package).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="卸载", command=uninstall_package).pack(side=LEFT, padx=5)

        # 初始加载所有包
        search_packages()

    def manage_venv(self):
        venv_window = ttk.Toplevel(self.root)
        venv_window.title("虚拟环境管理")
        venv_window.geometry("700x500")

        # 创建虚拟环境框架
        create_frame = ttk.LabelFrame(venv_window, text="创建新环境", padding=10)
        create_frame.pack(fill=X, padx=10, pady=5)

        name_var = ttk.StringVar()
        python_var = ttk.StringVar(value="3.8")

        ttk.Label(create_frame, text="环境名称:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(create_frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(create_frame, text="Python版本:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Combobox(create_frame, textvariable=python_var, 
                    values=["3.7", "3.8", "3.9", "3.10"]).grid(row=1, column=1, padx=5, pady=5)

        # 显示现有虚拟环境列表
        list_frame = ttk.LabelFrame(venv_window, text="现有环境", padding=10)
        list_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        columns = ("环境名称", "Python版本", "路径", "状态")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill=BOTH, expand=YES)

        def create_venv():
            name = name_var.get()
            if name:
                try:
                    venv_path = os.path.join(os.getcwd(), "venvs", name)
                    venv.create(venv_path, with_pip=True)
                    self.show_message("成功", f"虚拟环境 {name} 创建成功")
                    refresh_venvs()
                except Exception as e:
                    self.show_message("错误", f"创建失败: {str(e)}", "error")

        def refresh_venvs():
            tree.delete(*tree.get_children())
            venvs_dir = os.path.join(os.getcwd(), "venvs")
            if os.path.exists(venvs_dir):
                for venv_name in os.listdir(venvs_dir):
                    venv_path = os.path.join(venvs_dir, venv_name)
                    if os.path.isdir(venv_path):
                        python_path = os.path.join(venv_path, "Scripts", "python.exe")
                        if os.path.exists(python_path):
                            try:
                                result = subprocess.run([python_path, "--version"], 
                                                     capture_output=True, text=True)
                                version = result.stdout.strip()
                                tree.insert("", END, values=(venv_name, version, venv_path, "可用"))
                            except:
                                tree.insert("", END, values=(venv_name, "未知", venv_path, "错误"))

        def activate_venv():
            selected = tree.selection()
            if selected:
                venv_path = tree.item(selected[0])['values'][2]
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                if os.path.exists(activate_script):
                    os.system(f'start cmd /K "{activate_script}"')

        def delete_venv():
            selected = tree.selection()
            if selected:
                venv_name = tree.item(selected[0])['values'][0]
                if Messagebox.show_question(f"确定要删除虚拟环境 {venv_name} 吗?", "确认删除") == "是":
                    try:
                        import shutil
                        venv_path = os.path.join(os.getcwd(), "venvs", venv_name)
                        
                        # 先尝试关闭所有可能的进程
                        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
                        if os.path.exists(python_exe):
                            try:
                                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
                            except:
                                pass
                        
                        # 设置文件权限
                        def on_error(func, path, exc_info):
                            import stat
                            if not os.access(path, os.W_OK):
                                os.chmod(path, stat.S_IWUSR)
                                func(path)
                            else:
                                raise
                        
                        # 删除虚拟环境目录
                        shutil.rmtree(venv_path, onerror=on_error)
                        self.show_message("成功", f"虚拟环境 {venv_name} 已删除")
                        refresh_venvs()
                    except Exception as e:
                        self.show_message("错误", f"删除失败: {str(e)}", "error")

        button_frame = ttk.Frame(venv_window)
        button_frame.pack(fill=X, padx=10, pady=5)
        ttk.Button(button_frame, text="创建环境", command=create_venv).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="激活环境", command=activate_venv).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="刷新列表", command=refresh_venvs).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="删除环境", command=delete_venv).pack(side=LEFT, padx=5)

        # 初始加载虚拟环境列表
        refresh_venvs()

    def security_check(self):
        security_window = ttk.Toplevel(self.root)
        security_window.title("安全检查")
        security_window.geometry("800x600")

        # 创建控制框架
        control_frame = ttk.Frame(security_window)
        control_frame.pack(fill=X, padx=10, pady=5)

        # 创建结果显示区域
        text_area = ttk.Text(security_window)
        text_area.pack(fill=BOTH, expand=YES, padx=10, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_area, orient="vertical", command=text_area.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_area.configure(yscrollcommand=scrollbar.set)

        self.security_check_running = False

        def start_check():
            self.security_check_running = True
            text_area.delete(1.0, END)
            text_area.insert(END, "开始安全检查...\n\n")
            
            try:
                packages = self.get_installed_packages()
                total = len(packages)
                
                for i, pkg in enumerate(packages, 1):
                    if not self.security_check_running:
                        break
                        
                    pkg_name = pkg[0]
                    text_area.insert(END, f"[{i}/{total}] 检查 {pkg_name}...\n")
                    text_area.see(END)
                    
                    try:
                        result = subprocess.run(
                            ['pip', 'show', pkg_name],
                            capture_output=True,
                            text=True
                        )
                        if "WARNING" in result.stderr or "ERROR" in result.stderr:
                            text_area.insert(END, f"警告: {pkg_name} 可能存在问题\n{result.stderr}\n")
                        text_area.see(END)
                    except Exception as e:
                        text_area.insert(END, f"检查 {pkg_name} 时出错: {str(e)}\n")
                        text_area.see(END)
                
                text_area.insert(END, "\n安全检查完成！\n")
                text_area.see(END)
            except Exception as e:
                self.show_message("错误", f"安全检查失败: {str(e)}", "error")
            finally:
                self.security_check_running = False

        def stop_check():
            self.security_check_running = False
            text_area.insert(END, "\n已停止安全检查！\n")
            text_area.see(END)

        def export_results():
            try:
                filename = f'security_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                filepath = os.path.join(self.save_directory, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text_area.get(1.0, END))
                
                self.show_message("成功", f"检查结果已导出到桌面: {filename}")
            except Exception as e:
                self.show_message("错误", f"导出失败: {str(e)}", "error")

        ttk.Button(control_frame, text="开始检查", 
                  command=lambda: threading.Thread(target=start_check).start()).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="停止检查", command=stop_check).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="导出结果", command=export_results).pack(side=LEFT, padx=5)

    def performance_monitor(self):
        monitor_window = ttk.Toplevel(self.root)
        monitor_window.title("性能监控")
        monitor_window.geometry("1000x800")
    
        # 创建控制框架
        control_frame = ttk.Frame(monitor_window)
        control_frame.pack(fill=X, padx=10, pady=5)
    
        # 创建图表区域
        chart_frame = ttk.Frame(monitor_window)
        chart_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)
    
        # 创建多个图表
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
    
        # 初始化数据
        self.time_points = []
        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        self.monitor_running = False
    
        def update_charts():
            if self.monitor_running:
                try:
                    # 获取当前时间
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.time_points.append(current_time)
                    
                    # 获取系统信息
                    cpu_percent = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    self.cpu_data.append(cpu_percent)
                    self.memory_data.append(memory.percent)
                    self.disk_data.append(disk.percent)
                    
                    # 保持最近30个数据点
                    if len(self.time_points) > 30:
                        self.time_points.pop(0)
                        self.cpu_data.pop(0)
                        self.memory_data.pop(0)
                        self.disk_data.pop(0)
                    
                    # 更新图表
                    ax1.clear()
                    ax2.clear()
                    ax3.clear()
                    
                    ax1.plot(range(len(self.time_points)), self.cpu_data, 'b-')
                    ax1.set_title('CPU使用率 (%)')
                    ax1.set_xticks(range(len(self.time_points)))
                    ax1.set_xticklabels(self.time_points, rotation=45)
                    
                    ax2.plot(range(len(self.time_points)), self.memory_data, 'r-')
                    ax2.set_title('内存使用率 (%)')
                    ax2.set_xticks(range(len(self.time_points)))
                    ax2.set_xticklabels(self.time_points, rotation=45)
                    
                    ax3.plot(range(len(self.time_points)), self.disk_data, 'g-')
                    ax3.set_title('磁盘使用率 (%)')
                    ax3.set_xticks(range(len(self.time_points)))
                    ax3.set_xticklabels(self.time_points, rotation=45)
                    
                    fig.tight_layout()
                    canvas.draw()
                    
                    # 每秒更新一次
                    monitor_window.after(1000, update_charts)
                except Exception as e:
                    self.show_message("错误", f"监控更新失败: {str(e)}", "error")
                    self.monitor_running = False
    
        def start_monitor():
            self.monitor_running = True
            update_charts()
    
        def stop_monitor():
            self.monitor_running = False
    
        def export_data():
            try:
                filename = f'performance_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                filepath = os.path.join(self.save_directory, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("时间,CPU使用率,内存使用率,磁盘使用率\n")
                    for t, c, m, d in zip(self.time_points, self.cpu_data, 
                                        self.memory_data, self.disk_data):
                        f.write(f"{t},{c},{m},{d}\n")
                
                self.show_message("成功", f"监控数据已导出到桌面: {filename}")
            except Exception as e:
                self.show_message("错误", f"导出失败: {str(e)}", "error")
    
        # 添加控制按钮
        ttk.Button(control_frame, text="开始监控", command=start_monitor).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="停止监控", command=stop_monitor).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="导出数据", command=export_data).pack(side=LEFT, padx=5)
    
        # 添加状态显示
        status_label = ttk.Label(monitor_window, text="监控状态: 未启动")
        status_label.pack(side=BOTTOM, fill=X, padx=10, pady=5)
    
        def update_status():
            status_label.config(text=f"监控状态: {'运行中' if self.monitor_running else '已停止'}")
            monitor_window.after(1000, update_status)
    
        update_status()
        self.show_message("成功", "性能监控已启动")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PipListGUI()
    app.run()
