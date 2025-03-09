#!python
import pandas as pd
import subprocess
from filelock import FileLock
import os
import argparse
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


def save_to_excel(package_list, languages, frameworks, requirements, file_name='已安装库.xlsx', selected_option='all'):
    lock_file_name = 'lock'

    if selected_option == 'all' or selected_option == 'languages':
        temp_file_name = '编程语言.xlsx'
        with FileLock(lock_file_name):
            df_languages = pd.DataFrame(languages, columns=['编程语言', '版本号'])
            df_languages.to_excel(temp_file_name, index=False)
        print(f"编程语言信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'packages':
        temp_file_name = 'Python库.xlsx'
        with FileLock(lock_file_name):
            df_packages = pd.DataFrame(package_list, columns=['包名', '版本号'])
            df_packages.to_excel(temp_file_name, index=False)
        print(f"Python库信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'frameworks':
        temp_file_name = '前端框架.xlsx'
        with FileLock(lock_file_name):
            df_frameworks = pd.DataFrame(frameworks, columns=['前端框架', '版本号'])
            df_frameworks.to_excel(temp_file_name, index=False)
        print(f"前端框架信息已成功保存到 {temp_file_name}")

    if selected_option == 'all' or selected_option == 'requirements':
        temp_file_name = '依赖匹配.xlsx'
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='查询并保存已安装的Python库信息、编程语言信息和前端框架信息')
    parser.add_argument('-f', '--file', type=str, default='已安装库.xlsx', help='保存文件的名称')
    args = parser.parse_args()

    print("请选择要检测的信息类型：")
    print("1. 所有信息 (all)")
    print("2. 编程语言信息 (languages)")
    print("3. Python库信息 (packages)")
    print("4. 前端框架信息 (frameworks)")
    print("5. 依赖匹配信息 (requirements)")

    selected_option = input("请输入选项编号 (1, 2, 3, 4, 或 5): ").strip()

    if selected_option == '1':
        selected_option = 'all'
    elif selected_option == '2':
        selected_option = 'languages'
    elif selected_option == '3':
        selected_option = 'packages'
    elif selected_option == '4':
        selected_option = 'frameworks'
    elif selected_option == '5':
        selected_option = 'requirements'
    else:
        print("无效的选项编号，将默认检测所有信息。")
        selected_option = 'all'

    packages = get_installed_packages()
    requirements = get_requirements_packages()
    languages = get_installed_languages()
    frameworks = get_installed_front_end_frameworks()

    save_to_excel(package_list=packages, languages=languages, frameworks=frameworks, requirements=requirements,
                  file_name=args.file, selected_option=selected_option)
# PIPlist-Query V1.1
