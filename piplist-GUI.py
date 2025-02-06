import tkinter as tk
from tkinter import messagebox
import pandas as pd
import subprocess
from filelock import FileLock
import os
import re
import chardet

def get_installed_packages():
    result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
    packages = result.stdout.decode('utf-8').split('\n')
    packages = packages[2:]
    packages = [package for package in packages if package]
    package_list = [package.split() for package in packages]
    return package_list

def get_requirements_packages(file_path='requirements.txt'):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result['encoding']

        with open(file_path, 'r', encoding=encoding) as file:
            requirements = file.readlines()

        requirements = [re.sub(r'\s+', ' ', line.strip()).split('==') for line in requirements if line.strip()]
        return requirements
    except FileNotFoundError:
        print("requirements.txt 文件未找到。")
        return []
    except chardet.UniversalDetectorError:
        print(f"无法检测 {file_path} 文件的编码。请手动指定编码。")
        return []

def get_language_version(command, pattern):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip()
        match = re.search(pattern, output)
        if match:
            return match.group(1)
        else:
            return "版本信息未找到"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "版本信息未找到"

def get_installed_languages():
    languages = []

    python_version = get_language_version(['python', '--version'], r'Python (\d+\.\d+\.\d+)')
    languages.append(['Python', python_version])

    java_version = get_language_version(['java', '-version'], r'version "(\d+\.\d+\.\d+_\d+)"')
    languages.append(['Java', java_version])

    node_version = get_language_version(['node', '--version'], r'v(\d+\.\d+\.\d+)')
    languages.append(['Node.js', node_version])

    c_version = get_language_version(['gcc', '--version'], r'gcc version (\d+\.\d+\.\d+)')
    languages.append(['C语言编译器 (gcc)', c_version])

    go_version = get_language_version(['go', 'version'], r'go version go(\d+\.\d+\.\d+)')
    languages.append(['Go语言', go_version])

    ruby_version = get_language_version(['ruby', '-v'], r'ruby (\d+\.\d+\.\d+)')
    languages.append(['Ruby', ruby_version])

    php_version = get_language_version(['php', '-v'], r'PHP (\d+\.\d+\.\d+)')
    languages.append(['PHP', php_version])

    perl_version = get_language_version(['perl', '-v'], r'v(\d+\.\d+\.\d+)')
    languages.append(['Perl', perl_version])

    swift_version = get_language_version(['swift', '--version'], r'Swift version (\d+\.\d+\.\d+)')
    languages.append(['Swift', swift_version])

    rust_version = get_language_version(['rustc', '--version'], r'rustc (\d+\.\d+\.\d+)')
    languages.append(['Rust', rust_version])

    csharp_version = get_language_version(['dotnet', '--version'], r'(\d\.\d+\.\d+)')
    languages.append(['C#', csharp_version])

    python3_version = get_language_version(['python3', '--version'], r'Python (\d+\.\d+\.\d+)')
    languages.append(['Python 3', python3_version])

    typescript_version = get_language_version(['npm', 'list', '-g', 'typescript'], r'typescript@(\d+\.\d+\.\d+)')
    languages.append(['TypeScript', typescript_version])

    r_version = get_language_version(['Rscript', '--version'], r'R version (\d+\.\d+\.\d+)')
    languages.append(['R', r_version])

    kotlin_version = get_language_version(['kotlinc', '-version'], r'Kotlin version (\d+\.\d+\.\d+)')
    languages.append(['Kotlin', kotlin_version])

    return languages

def get_installed_front_end_frameworks():
    frameworks = []

    vue_version = get_language_version(['npm', 'list', '-g', 'vue-cli'], r'vue-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Vue.js', vue_version])

    react_version = get_language_version(['npm', 'list', '-g', 'create-react-app'], r'create-react-app@(\d+\.\d+\.\d+)')
    frameworks.append(['React.js', react_version])

    angular_version = get_language_version(['npm', 'list', '-g', '@angular/cli'], r'@angular/cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Angular', angular_version])

    ember_version = get_language_version(['npm', 'list', '-g', 'ember-cli'], r'ember-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Ember.js', ember_version])

    svelte_version = get_language_version(['npm', 'list', '-g', 'svelte-cli'], r'svelte-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Svelte', svelte_version])

    nextjs_version = get_language_version(['npm', 'list', '-g', 'next'], r'next@(\d+\.\d+\.\d+)')
    frameworks.append(['Next.js', nextjs_version])

    nuxtjs_version = get_language_version(['npm', 'list', '-g', 'nuxt'], r'nuxt@(\d+\.\d+\.\d+)')
    frameworks.append(['Nuxt.js', nuxtjs_version])

    gatsby_version = get_language_version(['npm', 'list', '-g', 'gatsby-cli'], r'gatsby-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Gatsby', gatsby_version])

    vuepress_version = get_language_version(['npm', 'list', '-g', 'vuepress'], r'vuepress@(\d+\.\d+\.\d+)')
    frameworks.append(['VuePress', vuepress_version])

    return frameworks

def save_to_excel(package_list, languages, frameworks, requirements, selected_option='all'):
    lock_file_name = 'lock'
    save_directory = os.path.join(os.getcwd(), 'results')
    os.makedirs(save_directory, exist_ok=True)

    if selected_option == 'all' or selected_option == 'languages':
        temp_file_name = os.path.join(save_directory, '编程语言.xlsx')
        with FileLock(lock_file_name):
            df_languages = pd.DataFrame(languages, columns=['编程语言', '版本号'])
            df_languages.to_excel(temp_file_name, index=False)
        print(f"编程语言信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'packages':
        temp_file_name = os.path.join(save_directory, 'Python库.xlsx')
        with FileLock(lock_file_name):
            df_packages = pd.DataFrame(package_list, columns=['包名', '版本号'])
            df_packages.to_excel(temp_file_name, index=False)
        print(f"Python库信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'frameworks':
        temp_file_name = os.path.join(save_directory, '前端框架.xlsx')
        with FileLock(lock_file_name):
            df_frameworks = pd.DataFrame(frameworks, columns=['前端框架', '版本号'])
            df_frameworks.to_excel(temp_file_name, index=False)
        print(f"前端框架信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'requirements':
        temp_file_name = os.path.join(save_directory, '依赖匹配.xlsx')
        with FileLock(lock_file_name):
            installed_packages_dict = {package[0]: package[1] for package in package_list}
            matched_requirements = []
            for req in requirements:
                package_name = req[0]
                req_version = req[1] if len(req) > 1 else '未指定版本'
                installed_version = installed_packages_dict.get(package_name, '未安装')
                matched_requirements.append(
                    [package_name, req_version, installed_version, req_version == installed_version])
            df_matched_requirements = pd.DataFrame(matched_requirements,
                                                   columns=['包名', '要求版本', '已安装版本', '是否匹配'])
            df_matched_requirements.to_excel(temp_file_name, index=False)
        print(f"依赖匹配信息已成功保存到 {temp_file_name}")

def on_select():
    selected_option = option_var.get()
    packages = get_installed_packages()
    requirements = get_requirements_packages()
    languages = get_installed_languages()
    frameworks = get_installed_front_end_frameworks()

    save_to_excel(package_list=packages, languages=languages, frameworks=frameworks, requirements=requirements,
                  selected_option=selected_option)
    messagebox.showinfo("成功", "信息已成功保存到 results 目录")

# 创建主窗口
root = tk.Tk()
root.title("piplist-GUI工具")
root.geometry("400x400")

# 创建选项变量
option_var = tk.StringVar()
option_var.set('all')  # 默认选项

# 创建选项框
options_frame = tk.Frame(root)
options_frame.pack(pady=10)

# 添加选项
tk.Radiobutton(options_frame, text="所有信息 (all)", variable=option_var, value='all').pack(anchor=tk.W)
tk.Radiobutton(options_frame, text="编程语言信息 (languages)", variable=option_var, value='languages').pack(anchor=tk.W)
tk.Radiobutton(options_frame, text="Python库信息 (packages)", variable=option_var, value='packages').pack(anchor=tk.W)
tk.Radiobutton(options_frame, text="前端框架信息 (frameworks)", variable=option_var, value='frameworks').pack(anchor=tk.W)
tk.Radiobutton(options_frame, text="依赖匹配信息 (requirements)", variable=option_var, value='requirements').pack(anchor=tk.W)

# 创建按钮
submit_button = tk.Button(root, text="查询并保存信息", command=on_select)
submit_button.pack(pady=20)

# 运行主循环
root.mainloop()
