# AGENTS.md

本项目是一个 KiCad 10 红绿灯控制板项目。后续 agent 修改这里的 KiCad 文件时，必须按下面流程验证，不能只靠文本检查。

## 本机 KiCad 路径

柠檬叔这台机器上的 KiCad 10 安装在：

```powershell
E:\KiCad\10.0
```

命令行工具路径：

```powershell
E:\KiCad\10.0\bin\kicad-cli.exe
```

Python 接口路径：

```powershell
E:\KiCad\10.0\bin\python.exe
```

## 第一原则：必须让 KiCad 自己加载

不要把以下检查当成“KiCad 文件有效”的证明：

- 括号数量相等。
- JSON 能解析。
- 文件能被普通文本编辑器打开。
- 自己手写的 S-expression 看起来像 KiCad 格式。

这些只能说明文本大致没断，不能说明 KiCad GUI 能打开。

修改 `.kicad_sch` 后，必须运行：

```powershell
& 'E:\KiCad\10.0\bin\kicad-cli.exe' sch export svg E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_sch -o E:\development\usb-c-traffic-light-board\kicad\_check_sch_svg
```

期望输出包含：

```text
完成。
```

修改 `.kicad_pcb` 后，必须运行：

```powershell
& 'E:\KiCad\10.0\bin\kicad-cli.exe' pcb export svg --layers F.SilkS,Edge.Cuts --mode-single E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb -o E:\development\usb-c-traffic-light-board\kicad\_check_pcb_svg\usb_c_traffic_light_board.svg
```

期望输出包含：

```text
完成。
```

## 红圈排查

KiCad 工程管理器里看到红圈时，按这个顺序查：

1. 确认 KiCad 是否已经打开了旧状态：

```powershell
Get-Process | Where-Object { $_.ProcessName -match 'kicad|eeschema|pcbnew' } | Select-Object ProcessName,Id,MainWindowTitle,Path
```

如果已有 `kicad.exe` 正在打开本工程，先让用户关闭 KiCad，再重新打开工程。

2. 检查锁文件：

```powershell
Get-ChildItem -Force E:\development\usb-c-traffic-light-board\kicad | Where-Object { $_.Name -like '~*.lck' }
```

如果 KiCad 已经关闭但锁文件还在，才可以删除这个锁文件。

3. 分别验证单文件：

```powershell
& 'E:\KiCad\10.0\bin\kicad-cli.exe' sch export svg E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_sch -o E:\development\usb-c-traffic-light-board\kicad\_check_sch_svg
```

```powershell
& 'E:\KiCad\10.0\bin\kicad-cli.exe' pcb export svg --layers F.SilkS,Edge.Cuts --mode-single E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb -o E:\development\usb-c-traffic-light-board\kicad\_check_pcb_svg\usb_c_traffic_light_board.svg
```

4. 如果单文件都能导出，但工程入口还是红圈，检查 `.kicad_pro` 的 `sheets` 段是否包含根 sheet UUID。

## KiCad 10 文件格式注意事项

- `.kicad_sch` 的图形多段线要带 `fill` 段。
- `.kicad_sch` 需要 `lib_symbols` 和 `sheet_instances`。
- `.kicad_pcb` 不要随手手写 footprint/property，格式细节很容易导致 KiCad 拒绝加载。
- 如果要生成 PCB 文件，优先用 KiCad 自带 Python 接口 `pcbnew` 生成，再用 `kicad-cli pcb export svg` 验证。
- `.kicad_pro` 不要写成极简 JSON；KiCad 10 工程管理器依赖较完整的工程元数据。

## PCB 布线要求

蓝色连线是 KiCad 的 ratsnest，也就是未布线网络提示，不是铜线。

不能把带大量 ratsnest 的 PCB 当成完成品交付。最终可下单版本必须满足：

- 三颗灯位置沿 `14mm x 57mm` 长条方向排列：上绿、中橙、下红。
- USB-C 是背面立式/垂直接口，位置复用原拨动开关穿出后壳的区域；不要把 USB-C 放在板子底端和红灯抢位置。
- 所有必须连接的网络都要有真实铜线、过孔或铺铜连接。
- KiCad 中不应再显示未布线飞线。
- `kicad-cli pcb drc` 报告中不能有短路、间距、板边、未连接等 error。

KiCad 10 本体主要提供交互式布线器，不是完整的一键自动布线器。若需要全自动布线，应接入外部 Freerouting 流程；当前机器 PATH 里未发现 `freerouting` 命令。没有 Freerouting 时，必须手工/脚本辅助布线并反复跑 DRC。

## 编码检查

本项目文档以简体中文为主。写入中文后，必须扫描乱码：

```powershell
rg --text -n "锛|€|俙|����|�|\?\?\?" E:\development\usb-c-traffic-light-board --glob "!AGENTS.md"
```

期望没有匹配。

## 当前可用验证产物

原理图导出结果：

```text
E:\development\usb-c-traffic-light-board\kicad\_check_sch_svg\usb_c_traffic_light_board.svg
```

PCB 导出结果：

```text
E:\development\usb-c-traffic-light-board\kicad\_check_pcb_svg\usb_c_traffic_light_board.svg
```
