# Python环境管理工具

## 项目简介
Python环境管理工具是一个基于 Python 的图形界面应用程序，用于管理和监控 Python 开发环境。它提供了包管理、虚拟环境管理、安全检查和性能监控等功能，帮助开发者更好地管理其 Python 开发环境。

## 使用方式
### 方式一：直接运行可执行文件（推荐）
1. 下载 `piplist.exe`
2. 双击运行即可，无需安装 Python 环境和依赖包
3. 所有生成的文件将保存在程序所在的"results"文件夹中

### 方式二：从源码运行
1. 确保安装 Python 3.6+
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 运行程序：
```bash
python piplist-GUI.py
```

## 主要功能
### 1. 包管理
- 检测已安装的 Python 包及其版本
- 导出包信息为 JSON/YAML 格式
- 生成包依赖关系图
- 检查包版本与 requirements.txt 的匹配情况

### 2. 虚拟环境管理
- 创建新的虚拟环境
- 查看现有虚拟环境列表
- 激活指定的虚拟环境
- 删除不需要的虚拟环境

### 3. 安全检查
- 检查已安装包的安全警告
- 导出安全检查报告
- 实时显示检查进度

### 4. 性能监控
- 实时监控 CPU 使用率
- 内存使用情况跟踪
- 磁盘使用状态监控
- 导出监控数据为 CSV 格式

## 使用说明
### 包管理
1. 在主界面选择要检测的信息类型：
   - 所有信息
   - 编程语言信息
   - Python库信息
   - 前端框架信息
   - 依赖匹配信息
2. 点击"查询并保存信息"按钮执行检测
3. 结果将自动保存到桌面的"Python环境管理工具"文件夹中

### 虚拟环境管理
1. 点击"工具" -> "虚拟环境管理"
2. 在弹出窗口中可以：
   - 输入名称创建新环境
   - 选择环境后点击激活
   - 选择环境后点击删除
   - 点击刷新更新环境列表

### 安全检查
1. 点击"工具" -> "安全检查"
2. 点击"开始检查"启动检查流程
3. 可随时点击"停止检查"中断操作
4. 使用"导出结果"保存检查报告

### 性能监控
1. 点击"工具" -> "性能监控"
2. 查看实时系统资源使用图表
3. 可随时开始/停止监控
4. 支持将监控数据导出为 CSV 文件

## 输出文件说明
所有生成的文件都将保存在桌面的"Python环境管理工具"文件夹中：
- `Python库.xlsx`: 已安装的 Python 包信息
- `编程语言.xlsx`: 系统中的编程语言版本信息
- `前端框架.xlsx`: 已安装的前端框架信息
- `依赖匹配.xlsx`: requirements.txt 的依赖匹配结果
- `dependency_graph.png`: Python 包依赖关系图
- `security_check_*.txt`: 安全检查报告
- `performance_monitor_*.csv`: 性能监控数据
- `export.json/yaml`: 导出的环境信息

## 发布版本
- 最新版本：v1.0.0
- 发布日期：2024年
- 支持系统：Windows 10/11
- 运行要求：无需 Python 环境，双击即可运行

## 注意事项
1. 首次运行时可能需要管理员权限
2. 虚拟环境的创建和删除可能需要一定时间
3. 性能监控数据会定期自动更新
4. 建议定期进行安全检查
5. 导出大量数据时可能需要等待几秒钟

## 常见问题
1. **程序无法启动**
   - 尝试以管理员身份运行
   - 检查杀毒软件是否拦截

2. **虚拟环境创建失败**
   - 确保目标路径具有写入权限
   - 检查磁盘空间是否充足

3. **监控数据不更新**
   - 点击停止后重新开始监控
   - 检查系统资源使用情况

4. **导出文件失败**
   - 确保目标文件夹具有写入权限
   - 关闭可能占用文件的程序

## 版权信息
© 2024 BinbimTech. 保留所有权利。

## 联系方式
- 个人主页：暂无
- 邮箱：hbq30@outlook.com
- QQ：1721822150
- GitHub：https://github.com/BB0813

## 许可证
本项目采用 Apache-2.0 license 许可证。
```