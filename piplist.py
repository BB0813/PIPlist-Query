import pandas as pd
import subprocess
from filelock import FileLock
import os
import argparse
import re

def get_installed_packages():
    # 使用pip list命令获取已安装的包列表
    result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
    # 解码输出并分割成行
    packages = result.stdout.decode('utf-8').split('\n')
    # 移除第一行（列标题）
    packages = packages[2:]
    # 过滤掉空行
    packages = [package for package in packages if package]
    # 将每一行分割成包名和版本号
    package_list = [package.split() for package in packages]
    return package_list

def get_language_version(command, pattern):
    try:
        # 运行命令获取版本信息
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 解码输出
        output = result.stdout.decode('utf-8').strip()
        # 使用正则表达式提取版本号
        match = re.search(pattern, output)
        if match:
            return match.group(1)
        else:
            return "版本信息未找到"
    except Exception as e:
        return str(e)

def get_installed_languages():
    languages = []
    
    # 检测Python版本
    python_version = get_language_version(['python', '--version'], r'Python (\d+\.\d+\.\d+)')
    languages.append(['Python', python_version])
    
    # 检测Java版本
    java_version = get_language_version(['java', '-version'], r'version "(\d+\.\d+\.\d+_\d+)"')
    languages.append(['Java', java_version])
    
    # 检测Node.js版本
    node_version = get_language_version(['node', '--version'], r'v(\d+\.\d+\.\d+)')
    languages.append(['Node.js', node_version])
    
    # 检测C语言编译器（假设使用gcc）
    c_version = get_language_version(['gcc', '--version'], r'gcc version (\d+\.\d+\.\d+)')
    languages.append(['C语言编译器 (gcc)', c_version])
    
    # 检测Go语言版本
    go_version = get_language_version(['go', 'version'], r'go version go(\d+\.\d+\.\d+)')
    languages.append(['Go语言', go_version])
    
    # 检测Ruby版本
    ruby_version = get_language_version(['ruby', '-v'], r'ruby (\d+\.\d+\.\d+)')
    languages.append(['Ruby', ruby_version])
    
    # 检测PHP版本
    php_version = get_language_version(['php', '-v'], r'PHP (\d+\.\d+\.\d+)')
    languages.append(['PHP', php_version])
    
    # 检测Perl版本
    perl_version = get_language_version(['perl', '-v'], r'v(\d+\.\d+\.\d+)')
    languages.append(['Perl', perl_version])
    
    # 检测Swift版本
    swift_version = get_language_version(['swift', '--version'], r'Swift version (\d+\.\d+\.\d+)')
    languages.append(['Swift', swift_version])
    
    # 检测Rust版本
    rust_version = get_language_version(['rustc', '--version'], r'rustc (\d+\.\d+\.\d+)')
    languages.append(['Rust', rust_version])
    
    # 检测C#版本（假设使用dotnet）
    csharp_version = get_language_version(['dotnet', '--version'], r'(\d+\.\d+\.\d+)')
    languages.append(['C#', csharp_version])
    
    # 检测其他编程语言（根据需要添加）
    # 例如，检测Python 3版本
    python3_version = get_language_version(['python3', '--version'], r'Python (\d+\.\d+\.\d+)')
    languages.append(['Python 3', python3_version])
    
    # 例如，检测TypeScript版本（假设使用npm）
    typescript_version = get_language_version(['npm', 'list', '-g', 'typescript'], r'typescript@(\d+\.\d+\.\d+)')
    languages.append(['TypeScript', typescript_version])
    
    # 例如，检测R版本
    r_version = get_language_version(['Rscript', '--version'], r'R version (\d+\.\d+\.\d+)')
    languages.append(['R', r_version])
    
    # 例如，检测Kotlin版本（假设使用kotlinc）
    kotlin_version = get_language_version(['kotlinc', '-version'], r'Kotlin version (\d+\.\d+\.\d+)')
    languages.append(['Kotlin', kotlin_version])
    
    return languages

def get_installed_front_end_frameworks():
    frameworks = []
    
    # 检测Vue版本（假设使用npm）
    vue_version = get_language_version(['npm', 'list', '-g', 'vue-cli'], r'vue-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Vue.js', vue_version])
    
    # 检测React版本（假设使用npm）
    react_version = get_language_version(['npm', 'list', '-g', 'create-react-app'], r'create-react-app@(\d+\.\d+\.\d+)')
    frameworks.append(['React.js', react_version])
    
    # 检测Angular版本（假设使用npm）
    angular_version = get_language_version(['npm', 'list', '-g', '@angular/cli'], r'@angular/cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Angular', angular_version])
    
    # 检测Ember.js版本（假设使用npm）
    ember_version = get_language_version(['npm', 'list', '-g', 'ember-cli'], r'ember-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Ember.js', ember_version])
    
    # 检测Svelte版本（假设使用npm）
    svelte_version = get_language_version(['npm', 'list', '-g', 'svelte-cli'], r'svelte-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Svelte', svelte_version])
    
    # 检测Next.js版本（假设使用npm）
    nextjs_version = get_language_version(['npm', 'list', '-g', 'next'], r'next@(\d+\.\d+\.\d+)')
    frameworks.append(['Next.js', nextjs_version])
    
    # 检测其他前端框架（根据需要添加）
    # 例如，检测Nuxt.js版本（假设使用npm）
    nuxtjs_version = get_language_version(['npm', 'list', '-g', 'nuxt'], r'nuxt@(\d+\.\d+\.\d+)')
    frameworks.append(['Nuxt.js', nuxtjs_version])
    
    # 例如，检测Gatsby版本（假设使用npm）
    gatsby_version = get_language_version(['npm', 'list', '-g', 'gatsby-cli'], r'gatsby-cli@(\d+\.\d+\.\d+)')
    frameworks.append(['Gatsby', gatsby_version])
    
    # 例如，检测VuePress版本（假设使用npm）
    vuepress_version = get_language_version(['npm', 'list', '-g', 'vuepress'], r'vuepress@(\d+\.\d+\.\d+)')
    frameworks.append(['VuePress', vuepress_version])
    
    return frameworks

def save_to_excel(package_list, languages, frameworks, file_name='已安装库.xlsx', selected_option='all'):
    temp_file_name = file_name + '.tmp.xlsx'
    lock_file_name = file_name + '.lock'
    
    with FileLock(lock_file_name):
        # 创建Excel writer对象
        with pd.ExcelWriter(temp_file_name, engine='openpyxl') as writer:
            if selected_option == 'all' or selected_option == 'languages':
                # 将编程语言信息保存到“编程语言”工作表
                df_languages = pd.DataFrame(languages, columns=['编程语言', '版本号'])
                df_languages.to_excel(writer, sheet_name='编程语言', index=False)
            if selected_option == 'all' or selected_option == 'packages':
                # 将Python库信息保存到“Python库”工作表
                df_packages = pd.DataFrame(package_list, columns=['包名', '版本号'])
                df_packages.to_excel(writer, sheet_name='Python库', index=False)
            if selected_option == 'all' or selected_option == 'frameworks':
                # 将前端框架信息保存到“前端框架”工作表
                df_frameworks = pd.DataFrame(frameworks, columns=['前端框架', '版本号'])
                df_frameworks.to_excel(writer, sheet_name='前端框架', index=False)
        
        # 如果原始文件存在，先删除它
        if os.path.exists(file_name):
            os.remove(file_name)
        # 将临时文件重命名为目标文件名
        os.rename(temp_file_name, file_name)
    
    print(f"已安装的Python库信息、编程语言信息和前端框架信息已成功保存到 {file_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='查询并保存已安装的Python库信息、编程语言信息和前端框架信息')
    parser.add_argument('-f', '--file', type=str, default='已安装库.xlsx', help='保存文件的名称')
    args = parser.parse_args()
    
    # 交互式选择要检测的信息类型
    print("请选择要检测的信息类型：")
    print("1. 所有信息 (all)")
    print("2. 编程语言信息 (languages)")
    print("3. Python库信息 (packages)")
    print("4. 前端框架信息 (frameworks)")
    
    selected_option = input("请输入选项编号 (1, 2, 3, 或 4): ").strip()
    
    if selected_option == '1':
        selected_option = 'all'
    elif selected_option == '2':
        selected_option = 'languages'
    elif selected_option == '3':
        selected_option = 'packages'
    elif selected_option == '4':
        selected_option = 'frameworks'
    else:
        print("无效的选项编号，将默认检测所有信息。")
        selected_option = 'all'
    
    packages = get_installed_packages()
    languages = get_installed_languages()
    frameworks = get_installed_front_end_frameworks()
    
    save_to_excel(package_list=packages, languages=languages, frameworks=frameworks, file_name=args.file, selected_option=selected_option)
# PIPlist-Query V1.0