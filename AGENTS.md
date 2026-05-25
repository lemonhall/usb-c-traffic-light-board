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

## 本项目当前布线生成方法

当前 PCB 不是靠手写 `.kicad_pcb` 文本拼出来的，而是通过 KiCad 自带 Python 接口 `pcbnew` 生成。入口脚本是：

```text
scripts/generate_kicad_pcb.py
```

重新生成 PCB 时使用：

```powershell
& 'E:\KiCad\10.0\bin\python.exe' E:\development\usb-c-traffic-light-board\scripts\generate_kicad_pcb.py
```

这个脚本做了这些事：

- 新建 `pcbnew.BOARD()`，设置最小间距、最小线宽、过孔直径和钻孔。
- 用 `FootprintLoad()` 从 KiCad 10 自带封装库加载 LED、电阻、电容、CH552G、USB-C、测试点和螺丝孔。
- 明确创建 `5V`、`GND`、`USB_D+`、`USB_D-`、`CC1`、`CC2`、三路 LED 控制等网络。
- 用 `set_pad_net()` 把每个焊盘挂到对应网络，避免 KiCad 只显示飞线但没有真实铜线。
- 用 `PCB_TRACK` 生成实际铜线，用 `PCB_VIA` 生成过孔；正面和背面都参与布线。
- 用 `Edge.Cuts` 多段线生成当前非矩形外轮廓、端部梯形和 8 个侧边避让槽。

当初解决“满屏蓝线”的方式是：

1. 先把所有元件焊盘明确分配到网络。
2. 给每个网络补真实铜线，而不是只依赖 KiCad 的飞线提示。
3. LED 阳极到限流电阻走短线，三路 GPIO 改成背面独立线槽，避免正面交叉。
4. USB-C 的 D+/D- 从背面端口进入串联电阻，再通过过孔接到 CH552G。
5. 5V 从 USB-C 背面进来，过孔到正面右侧母线，再分给 MCU 和电容。
6. GND 做正反面母线，并给 LED、MCU、电容、CC 下拉电阻补过孔连接。
7. 每次调整元件、外形或走线路径后都重新跑 `kicad-cli pcb drc`，按报告继续改，直到 0 违规、0 未连接。

布线后必须运行：

```powershell
& 'E:\KiCad\10.0\bin\kicad-cli.exe' pcb drc 'E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb' -o 'E:\development\usb-c-traffic-light-board\kicad\_check_pcb_drc.rpt'
```

合格输出必须包含：

```text
发现 0 条违规项
发现 0 个未连接的项目
```

如果 DRC 里仍有 `unconnected`，或者 KiCad 里仍能看到蓝色飞线，就不能说 PCB 已完成。

## 每次和用户对话后的收口步骤

每轮完成用户交代的 PCB、文档、脚本或验证任务后，按这个顺序收口：

1. 先确认最新用户请求，避免还在处理上一轮旧问题。
2. 如果改了 KiCad 生成逻辑，先运行 `scripts/generate_kicad_pcb.py` 重新生成 PCB。
3. 如果改了 `.kicad_pcb`，必须导出 PCB SVG，并运行 PCB DRC。
4. 如果改了 `.kicad_sch`，必须导出原理图 SVG。
5. 如果改了中文文档，必须跑乱码扫描。
6. 跑 `git status --short` 和 `git diff --check`，确认没有意外文件和明显空白错误。
7. 用户明确要求“落袋为安”“commit”“push”时，提交并推送到当前分支。
8. 提交后用 `git log -1 --oneline` 和 `git status --short` 核对结果。
9. 任务完成后，用 `apn-pushtool` 发简短通知。
10. 最后用中文简要告诉用户：改了什么、验证结果、commit hash、是否已 push。

推荐提交前检查命令：

```powershell
git status --short
git diff --check
& 'E:\KiCad\10.0\bin\kicad-cli.exe' pcb drc 'E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb' -o 'E:\development\usb-c-traffic-light-board\kicad\_check_pcb_drc.rpt'
```

推荐通知命令：

```powershell
apn-pushtool send --title "红绿灯板" --body "任务已完成"
```

## 编码检查

本项目文档以简体中文为主。写入中文后，必须扫描乱码：

```powershell
rg --text -n "\x{951b}|\x{20ac}|\x{4fd9}|\x{fffd}|\?\?\?" E:\development\usb-c-traffic-light-board
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
