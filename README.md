# 🚄 鲸介12306智能抢票助手

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

**基于 Selenium 的自动化抢票工具，让春运抢票更轻松！**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用说明](#-使用说明) • [常见问题](#-常见问题)

</div>

---

## 📖 项目简介

鲸介12306智能抢票助手是一款基于 Selenium WebDriver 的自动化抢票工具，支持图形界面（GUI）和命令行两种使用模式。通过智能化的抢票策略，帮助用户在12306官网快速抢到心仪的车票。

### ✨ 功能特性

- 🖥️ **双模式支持**：提供友好的 GUI 界面和灵活的命令行模式
- 🎯 **双策略抢票**：
  - 时间范围策略：在指定时间段内抢最早的车次
  - 指定车次策略：精准抢购指定车次号
- 🔐 **预登录功能**：提前完成登录，抢票时无需等待
- ⚡ **高速刷新**：智能刷新间隔，提高抢票成功率
- 💾 **配置保存**：支持保存常用配置，一键加载
- 📱 **扫码登录**：使用12306 APP扫码，安全便捷
- 🎫 **多票型支持**：成人票、学生票自由选择
- 🪑 **智能选座**：支持座位偏好设置

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Microsoft Edge 浏览器
- Windows 操作系统

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/你的用户名/12306-ticket-tool.git
cd 12306-ticket-tool
```

2. **创建虚拟环境（推荐）**
```bash
conda create -n py12306 python=3.8
conda activate py12306
```

3. **安装依赖**
```bash
pip install selenium
```

4. **安装 Edge WebDriver**
   - 自动安装：运行脚本时会自动下载匹配的驱动
   - 手动安装：访问 [Edge WebDriver 下载页](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

---

## 📚 使用说明

### 方式一：GUI 图形界面（推荐）

1. **启动 GUI**
```bash
cd v2.0
python gui_app.py
```

2. **操作流程**
   - ① 填写出发站、到达站、日期等基本信息
   - ② 选择抢票策略（时间范围 or 指定车次）
   - ③ 点击 **🔐 预登录12306** 按钮
   - ④ 使用手机12306 APP扫码登录
   - ⑤ 登录成功后，点击 **🚀 开始抢票**

![GUI界面示例](docs/gui-screenshot.png)

### 方式二：命令行模式

1. **运行脚本**
```bash
cd Auto12306
python 12306_booking_script.py
```

2. **配置参数**
   - 首次运行会提示输入参数
   - 或编辑 `config.json` 文件预设参数

### 配置文件示例

```json
{
  "from_station": "广州南",
  "to_station": "深圳北",
  "travel_date": "2026-02-05",
  "ticket_type": "adult",
  "depart_time_range": {
    "start": "07:00",
    "end": "09:00"
  },
  "seat_category": "二等座",
  "seat_position_preference": "window",
  "booking_start_time": "2026-02-03 21:30:00",
  "target_train_number": "G1234"
}
```

**参数说明：**
- `from_station`：出发站（完整站名）
- `to_station`：到达站（完整站名）
- `travel_date`：出发日期（YYYY-MM-DD）
- `ticket_type`：票型（`adult` 成人票 / `student` 学生票）
- `depart_time_range`：出发时间范围
- `seat_category`：席别（二等座/一等座/商务座等）
- `seat_position_preference`：选座偏好（`first` 第一个 / `window` 靠窗 / `aisle` 过道）
- `booking_start_time`：开售时间（可留空立即开始）
- `target_train_number`：指定车次号（留空则按时间范围抢票）

---

## 🎯 抢票策略详解

### 策略一：时间范围抢票

适用场景：对车次无特殊要求，只要在某个时间段内出发即可

**工作原理：**
1. 扫描查询结果中所有车次
2. 筛选出发时间在指定范围内的车次
3. 按出发时间从早到晚排序
4. 优先抢购最早的可预订车次

**配置示例：**
```json
{
  "depart_time_range": {
    "start": "07:00",
    "end": "09:00"
  },
  "target_train_number": ""
}
```

### 策略二：指定车次抢票

适用场景：明确知道要抢的车次号

**工作原理：**
1. 精确定位目标车次号（如 G1234）
2. 高频刷新查询结果
3. 一旦出现立即点击预订

**配置示例：**
```json
{
  "target_train_number": "G1234"
}
```

---

## ⚙️ 高级功能

### 预登录功能

**为什么需要预登录？**
- ✅ 避免抢票时因登录问题浪费时间
- ✅ 提前确认登录状态，确保万无一失
- ✅ 登录和抢票分离，流程更稳定

**使用方法：**
1. 在 GUI 中点击"预登录12306"按钮
2. 等待浏览器打开并扫码登录
3. 登录成功后状态显示"✓ 已登录"
4. 此时可以随时开始抢票

### 开售时间设置

支持精确到秒的开售时间等待：

```json
{
  "booking_start_time": "2026-02-03 21:30:00"
}
```

脚本会在开售前10秒进入高频轮询状态，确保在开售瞬间开始抢票。

---

## 🛠️ 项目结构

```
12306-ticket-tool/
├── Auto12306/                    # 命令行版本
│   ├── 12306_booking_script.py  # 主脚本
│   ├── config.json              # 配置文件
│   └── 抢票脚本6.0.ipynb         # Jupyter Notebook版本
├── v2.0/                         # GUI版本
│   ├── gui_app.py               # GUI主程序
│   ├── booking_core.py          # 核心抢票逻辑
│   └── config.json              # 配置文件
├── README.md                     # 项目说明文档
└── LICENSE                       # 开源协议
```

---

## ❓ 常见问题

### Q1: 运行时提示"No module named 'selenium'"

**解决方法：**
```bash
pip install selenium
```

### Q2: 浏览器打开后无法自动操作

**可能原因：**
- Edge WebDriver 版本与浏览器版本不匹配
- 需要更新 Edge 浏览器到最新版本

**解决方法：**
```bash
# 检查 Edge 版本
edge://version

# 下载对应版本的 WebDriver
# https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

### Q3: 点击登录按钮失败

**解决方法：**
- 使用 GUI 的"预登录"功能，手动完成登录
- 12306 网站结构可能有变化，等待脚本更新

### Q4: 选座失败但订单已提交

**说明：**
- 这是正常现象，部分车次/席别不支持选座
- 12306 会自动分配座位
- 不影响订单提交和支付

### Q5: 抢票成功率如何提高？

**建议：**
1. 使用"指定车次"策略，刷新频率更高
2. 设置准确的开售时间，提前进入等待状态
3. 网络环境要稳定，建议使用有线网络
4. 提前完成预登录，确保登录状态正常

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## ⚠️ 免责声明

- 本项目仅供学习交流使用，请勿用于商业用途
- 使用本工具产生的任何后果由使用者自行承担
- 请遵守12306官网的使用规则和相关法律法规
- 建议合理使用，避免对12306服务器造成过大压力

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议

---

## 👨‍💻 作者

**鲸介 (Whale_DIY)**

- GitHub: [@你的GitHub用户名](https://github.com/你的用户名)
- Email: 你的邮箱@example.com

---

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️ 支持一下！

---

## 📝 更新日志

### v2.0 (2026-02-04)
- ✨ 新增 GUI 图形界面
- ✨ 新增预登录功能
- ✨ 优化登录流程，支持多种定位方式
- 🐛 修复选座失败的问题
- 📝 完善文档和注释

### v1.0 (2025-10-05)
- 🎉 首次发布
- ✨ 支持时间范围和指定车次两种策略
- ✨ 支持配置文件保存
- ✨ 支持扫码登录

---

<div align="center">

**如果觉得有用，请给个 ⭐️ Star 吧！**

Made with ❤️ by 鲸介

</div>
