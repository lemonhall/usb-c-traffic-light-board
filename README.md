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
- 第一版板框先按矩形处理。
- 三颗灯从上到下暂定为：绿、黄、红。
- USB-C 暂定放在红灯一端；如果外壳开口方向不同，后续再反向调整。
- 孔位、缺口、圆角、灯中心坐标等，等你给精确尺寸后再修。

## 电气方案

- 主控：沁恒 `CH552G`，小封装、带原生 USB。
- USB-C：
  - `VBUS` 提供 `5V`。
  - `D+ / D-` 接到主控 USB 引脚。
  - `CC1 / CC2` 各接一个 `5.1k` 下拉电阻到地，只做受电设备。
- 三颗灯：
  - 每颗灯单独串限流电阻。
  - 每颗灯由一个主控 GPIO 控制。
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
