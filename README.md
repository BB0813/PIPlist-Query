# piplist-query

## 简介
`piplist-query` 是一个用于检测和保存本地已安装的Python库、编程语言和前端框架信息的工具。用户可以通过交互式选择来决定要检测的信息类型，并将结果保存到Excel文件中。

## 功能
- **检测已安装的Python库**：使用`pip list`命令获取已安装的Python库列表。
- **检测已安装的编程语言**：包括Python、Java、Node.js、C语言编译器（gcc）、Go语言、Ruby、PHP、Perl、Swift、Rust和C#。
- **检测已安装的前端框架**：包括Vue.js、React.js、Angular、Ember.js、Svelte、Next.js、Nuxt.js、Gatsby和VuePress。
- **交互式选择**：用户可以通过输入选项编号来选择要检测的信息类型。
- **保存到Excel文件**：将检测到的信息分别保存到Excel文件的不同工作表中。

## 安装依赖
在运行脚本之前，请确保你已经安装了以下依赖库：
- `pandas`
- `filelock`

你可以使用以下命令安装这些库：
```bash
pip install pandas filelock
```

## 使用方法
1. 下载脚本：将脚本文件piplist.py保存到你的本地目录。
2. 运行脚本：在命令行中运行脚本，并根据提示选择要检测的信息类型。
```bash
python piplist.py -f 已安装库信息.xlsx
```
3. 选择检测类型：
- 输入 1 选择所有信息。
- 输入 2 选择编程语言信息。
- 输入 3 选择Python库信息。
- 输入 4 选择前端框架信息。

**选择后，脚本将检测并保存所有信息到已安装库信息.xlsx文件中**

## 工作表说明
- 编程语言：包含已安装的编程语言及其版本信息。
- Python库：包含已安装的Python库及其版本信息。
- 前端框架：包含已安装的前端框架及其版本信息。

## 注意事项
1. **命令行工具：确保你已经安装了相应的命令行工具（如gcc、go、npm、ruby、php、perl、swift、rust、dotnet等），以便脚本能够正确检测其版本信息。**

2. **版本检测命令：某些编程语言或框架的版本检测命令可能有所不同，请根据实际情况调整命令和正则表达式。**

3. **权限问题：在某些操作系统中，检测全局安装的npm包可能需要管理员权限。你可以通过以下命令以管理员权限运行脚本：**
```bash
Windows: 右键点击命令提示符或PowerShell，选择“以管理员身份运行”。
macOS/Linux: 使用sudo命令。
sudo python piplist.py
```

# 个人信息

**开发者：BinbimTech**
**联系邮箱: 18677523963@163.com**

# 版权与许可
**版权: © BinbimTech**