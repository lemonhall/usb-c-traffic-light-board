# USB-C 红绿灯控制板实施计划

> 给后续执行者：按任务逐项完成并勾选。每一步都应该留下可检查的文件结果。

**目标：** 建立一套第一版 USB-C 红绿灯控制板项目资料，面向 `57mm x 14mm` 完全替换板。

**架构：** 电路板使用 CH552G 原生 USB 单片机，USB-C 负责供电和数据，三颗 LED 由三个 GPIO 控制。KiCad 先建立工程骨架和板框，详细封装和精确机械位置等拿到卡尺数据后再锁定。

**技术栈：** KiCad、Markdown 硬件文档、Python 电脑端串口脚本。

---

### 任务 1：项目结构和需求

**文件：**
- 创建：`README.md`
- 创建：`docs/hardware/requirements.md`
- 创建：`references/original-board-photo.md`

- [x] **步骤 1：创建项目目录**

运行：

```powershell
New-Item -ItemType Directory -Force -Path E:\development\usb-c-traffic-light-board
```

期望结果：项目目录存在。

- [x] **步骤 2：写入需求文档**

写入 README、硬件需求和原板照片观察记录，明确 `57mm x 14mm` 外形、USB-C 供电控制、原板三灯信息。

### 任务 2：电气草案

**文件：**
- 创建：`docs/hardware/bom.md`
- 创建：`docs/hardware/pinout.md`
- 创建：`docs/hardware/serial-protocol.md`

- [x] **步骤 1：定义第一版物料清单**

列出 USB-C 母座、CH552G、三颗 LED、电阻、电容和测试焊盘。

- [x] **步骤 2：定义 USB 和 GPIO 网络**

记录 `VBUS`、`GND`、`D+`、`D-`、`CC1`、`CC2` 和三路 LED 控制信号。

- [x] **步骤 3：定义串口文本协议**

记录 `R`、`Y`、`G`、`A`、`S` 和 `?` 命令，以及对应返回。

### 任务 3：KiCad 骨架

**文件：**
- 创建：`kicad/usb_c_traffic_light_board.kicad_pro`
- 创建：`kicad/usb_c_traffic_light_board.kicad_sch`
- 创建：`kicad/usb_c_traffic_light_board.kicad_pcb`

- [x] **步骤 1：创建 KiCad 项目文件**

创建 KiCad 项目容器。

- [x] **步骤 2：创建原理图说明页**

创建带项目标题和设计说明的原理图草稿。

- [x] **步骤 3：创建板框**

创建 `57mm x 14mm` 的 `Edge.Cuts` 矩形板框，并加入放置提示。

### 任务 4：电脑端控制辅助

**文件：**
- 创建：`pc-control/traffic_light.py`
- 创建：`firmware/README.md`

- [x] **步骤 1：创建串口控制脚本**

实现一个最小 Python 脚本：向指定串口发送一条 ASCII 命令，并打印一行返回。

- [x] **步骤 2：记录固件行为**

记录上电状态、命令解析流程和可选工具链。

### 任务 5：验证

**文件：**
- 检查所有创建的文件。

- [x] **步骤 1：列出生成文件**

运行：

```powershell
Get-ChildItem -Recurse E:\development\usb-c-traffic-light-board
```

期望结果：计划中的文件都存在。

- [x] **步骤 2：检查中文乱码**

按仓库编码规则运行乱码特征扫描。

期望结果：没有匹配。
