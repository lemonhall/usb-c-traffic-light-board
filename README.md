# USB-C 红绿灯控制板

这是一个用于替换原红绿灯小板的项目。目标是做一块新的 `57mm x 14mm` 电路板，通过 USB-C 供电，并让电脑通过 USB 串口控制红、黄、绿三颗灯。

## 目标

- 完全替换原来的小电路板。
- 使用 USB-C 供电。
- 通过 USB-C 连接电脑，由电脑控制三颗灯。
- 电脑端识别为虚拟串口，方便脚本控制。
- 尽量避免飞线，最终装配时只使用这一块新板。

## 当前机械假设

- 板长：`57mm`
- 板宽：`14mm`
- 当前板框已经按原板照片改成上下梯形端部和左右半圆避让槽。
- 三颗灯从上到下为：绿、黄、红；灯中心按从板底往上约 `50mm`、`28mm`、`7mm` 复核。
- 上螺丝孔直径 `2mm`，孔边离上端梯形窄边约 `1mm`。
- 下螺丝孔直径 `2mm`，孔中心离板顶约 `33mm`，位于板子左侧、靠近从下往上第二组避让槽。
- USB-C 目标位置对应原拨动开关穿出后壳的位置；原开关伸出背面约 `10mm`，开口宽度约 `10mm`。
- 注意：当前 KiCad 里 `USB_C_Receptacle_G-Switch_GT-USB-7025` 是 `right-angle` 占位封装，不是最终可下单的立式背出 USB-C；最终必须按实物型号替换封装和 3D 机械模型。

## 下一步顺序

1. 机械复核：量原板孔位、缺口、圆角、灯中心坐标、USB-C 后壳开口位置，把板框从当前矩形改成更贴原壳的形状。
2. USB-C 完整性复核：按最终采购的连接器封装，复核 `VBUS`、`GND`、`CC1`、`CC2`、`D+`、`D-`，确认正反插都能稳定供电和通信。
3. 生成生产文件：用 KiCad CLI 导出 Gerber 和钻孔文件，再用 Gerber 预览检查铜层、板框、孔、阻焊和丝印。
4. 小批打样前审查：逐项核对 BOM、封装方向、LED 极性、USB-C 型号、CH552G 供电和下载方式。

当前建议先做第 1 步和第 2 步。它们决定这块板能不能真的塞回外壳，以及插上电脑后能不能稳定识别。

## 电气方案

- 主控：沁恒 `CH552G`，小封装、带原生 USB。
- USB-C：
  - 电脑 USB-C 默认 `VBUS` 提供 `5V`。
  - 本板只作为普通受电设备，不做 USB PD 高压协商。
  - `D+ / D-` 接到主控 USB 引脚。
  - `CC1 / CC2` 各接一个 `5.1k` 下拉电阻到地，只做受电设备。
- 三颗灯：
  - 每颗灯单独串限流电阻。
  - 每颗灯由一个主控 GPIO 控制。
  - 固件可用 PWM 分别控制三颗灯亮度，也可以控制任意组合同时亮、闪烁或呼吸。
  - 第一版按低亮度指示灯设计，目标电流约 `2-5mA`。
- 调试：
  - 预留 `5V`、`GND`、`D+`、`D-`、复位、三路灯控制测试焊盘。

## 串口协议草案

电脑通过虚拟串口发送一行文本命令：

```text
R 1
R 0
Y 1
Y 0
G 1
G 0
A 0
A 1
S 1 0 1
?
```

返回示例：

```text
OK
ERR 1
S R=1 Y=0 G=1
```

## 文件说明

- `docs/hardware/requirements.md`：需求和边界。
- `docs/hardware/bom.md`：第一版物料清单。
- `docs/hardware/pinout.md`：引脚和网络分配。
- `docs/hardware/mechanical-measurement-guide.md`：原板外轮廓和孔位测量指南。
- `docs/hardware/serial-protocol.md`：电脑控制协议。
- `docs/hardware/schematic.md`：完整原理图连接说明。
- `docs/hardware/schematic.svg`：可直接打开查看的完整原理图。
- `docs/hardware/pcb-layout.svg`：第一版 PCB 顶层布局草案。
- `references/original-board-photo.md`：原板照片观察记录。
- `kicad/`：KiCad 工程骨架和第一版板框。
- `firmware/README.md`：固件设计说明。
- `pc-control/traffic_light.py`：电脑端串口控制小脚本。

## 已查资料

- CH552G 是带 USB 的 8 位单片机：https://www.alldatasheet.com/datasheet-pdf/pdf/1147065/WCH/CH552G.html
- LCSC 页面显示 CH552G 常见封装为 SOP-16：https://www.lcsc.com/product-detail/Microcontrollers-MCU-MPU-SOC_WCH-Jiangsu-Qin-Heng-CH552G_C111292.html
- CH552G 资料中包含 USB Type-C CC 控制相关内容：https://www.alldatasheet.net/html-pdf/1147065/WCH/CH552G/2781/41/CH552G.html
