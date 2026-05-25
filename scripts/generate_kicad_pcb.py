import math

import pcbnew


BOARD_PATH = r"E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb"
FP_ROOT = r"E:\KiCad\10.0\share\kicad\footprints"
BOARD_ORIGIN_X = 141.5
BOARD_ORIGIN_Y = 76.5


def nm(mm_value):
    return int(mm_value * 1_000_000)


def v(x, y):
    return pcbnew.VECTOR2I(nm(BOARD_ORIGIN_X + x), nm(BOARD_ORIGIN_Y + y))


def size_vec(x, y):
    return pcbnew.VECTOR2I(nm(x), nm(y))


def back_smd_layers():
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.B_Cu)
    layers.AddLayer(pcbnew.B_Mask)
    layers.AddLayer(pcbnew.B_Paste)
    return layers


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def pad_by_number(fp, number):
    for pad in fp.Pads():
        if pad.GetNumber() == str(number):
            return pad
    raise ValueError(f"{fp.GetReference()} has no pad {number}")


def pads_by_number(fp, number):
    return [pad for pad in fp.Pads() if pad.GetNumber() == str(number)]


def set_pad_net(fp, pad_number, net):
    for pad in pads_by_number(fp, pad_number):
        pad.SetNet(net)


def quiet_footprint_graphics(fp):
    for item in fp.GraphicalItems():
        if item.GetLayer() in [pcbnew.F_SilkS, pcbnew.B_SilkS, pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
            item.SetLayer(pcbnew.F_Fab)
        if isinstance(item, pcbnew.PCB_TEXT):
            item.SetVisible(False)
            item.SetLayer(pcbnew.F_Fab)


def put_smd_on_back(fp):
    fp.SetLayer(pcbnew.B_Cu)
    for pad in fp.Pads():
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            pad.SetLayerSet(back_smd_layers())
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.F_Fab:
            item.SetLayer(pcbnew.B_Fab)
    return fp


def load_fp(lib_name, footprint_name, ref, value, x, y, rot=0, back=False):
    fp = pcbnew.FootprintLoad(FP_ROOT + "\\" + lib_name + ".pretty", footprint_name)
    if fp is None:
        raise RuntimeError(f"Cannot load footprint {lib_name}:{footprint_name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(v(x, y))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    quiet_footprint_graphics(fp)
    if back:
        put_smd_on_back(fp)
        quiet_footprint_graphics(fp)
    return fp


def add_line(board, x1, y1, x2, y2, layer, width=0.12):
    item = pcbnew.PCB_SHAPE(board)
    item.SetShape(pcbnew.SHAPE_T_SEGMENT)
    item.SetStart(v(x1, y1))
    item.SetEnd(v(x2, y2))
    item.SetLayer(layer)
    item.SetWidth(nm(width))
    board.Add(item)


def add_arc(board, x1, y1, xm, ym, x2, y2, layer, width=0.12):
    item = pcbnew.PCB_SHAPE(board)
    item.SetShape(pcbnew.SHAPE_T_ARC)
    item.SetArcGeometry(v(x1, y1), v(xm, ym), v(x2, y2))
    item.SetLayer(layer)
    item.SetWidth(nm(width))
    board.Add(item)


def add_rect(board, x1, y1, x2, y2, layer, width=0.12):
    add_line(board, x1, y1, x2, y1, layer, width)
    add_line(board, x2, y1, x2, y2, layer, width)
    add_line(board, x2, y2, x1, y2, layer, width)
    add_line(board, x1, y2, x1, y1, layer, width)


def add_polyline(board, points, layer, width=0.1):
    for start, end in zip(points, points[1:]):
        add_line(board, start[0], start[1], end[0], end[1], layer, width)


def circular_notch_points(side, center_y, half_chord=1.0, depth=0.75, segments=8):
    radius = (half_chord * half_chord + depth * depth) / (2.0 * depth)
    offset = radius - depth
    if side == "right":
        center_x = 14.0 + offset
        start_angle = math.atan2(-half_chord, -offset)
        end_angle = math.atan2(half_chord, -offset) - 2.0 * math.pi
    else:
        center_x = -offset
        start_angle = math.atan2(half_chord, offset)
        end_angle = math.atan2(-half_chord, offset)

    points = []
    for index in range(segments + 1):
        ratio = index / segments
        angle = start_angle + (end_angle - start_angle) * ratio
        points.append((center_x + radius * math.cos(angle), center_y + radius * math.sin(angle)))
    return points


def add_mechanical_outline(board):
    # 照原板照片做的第一版近似轮廓：端部梯形窄边 10mm，高度暂按 4.5mm。
    # 左右两侧保留塑料柱避让槽。
    # 避让槽按用户实测描述成对放置：从板底往上约 11/25/33/47 mm，
    # 换算到本坐标系为 y=46/32/24/10 mm。
    layer = pcbnew.Edge_Cuts
    width = 0.1
    notch_centers = [10.0, 24.0, 32.0, 46.0]
    notch_half_chord = 1.5
    notch_depth = 0.35

    add_polyline(board, [(2.0, 0.0), (12.0, 0.0), (14.0, 4.5)], layer, width)

    y = 4.5
    for center_y in notch_centers:
        add_line(board, 14.0, y, 14.0, center_y - notch_half_chord, layer, width)
        add_polyline(board, circular_notch_points("right", center_y, notch_half_chord, notch_depth), layer, width)
        y = center_y + notch_half_chord
    add_polyline(board, [(14.0, y), (14.0, 52.5), (12.0, 57.0), (2.0, 57.0), (0.0, 52.5)], layer, width)

    y = 52.5
    for center_y in reversed(notch_centers):
        add_line(board, 0.0, y, 0.0, center_y + notch_half_chord, layer, width)
        add_polyline(board, circular_notch_points("left", center_y, notch_half_chord, notch_depth), layer, width)
        y = center_y - notch_half_chord
    add_polyline(board, [(0.0, y), (0.0, 4.5), (2.0, 0.0)], layer, width)


def add_text(board, text, x, y, size=0.8, layer=pcbnew.F_SilkS):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(v(x, y))
    item.SetLayer(layer)
    item.SetTextSize(size_vec(size, size))
    item.SetTextThickness(nm(0.1))
    board.Add(item)


def add_track(board, net, start, end, width=0.22, layer=pcbnew.F_Cu):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(nm(width))
    track.SetLayer(layer)
    track.SetNet(net)
    board.Add(track)


def route_points(board, net, points, width=0.22, layer=pcbnew.F_Cu):
    for start, end in zip(points, points[1:]):
        add_track(board, net, start, end, width, layer)


def route_xy(board, net, coords, width=0.22, layer=pcbnew.F_Cu):
    route_points(board, net, [v(x, y) for x, y in coords], width, layer)


def route_pad_to_pad(board, net, pad_a, pad_b, coords=None, width=0.22, layer=pcbnew.F_Cu):
    middle = [v(x, y) for x, y in (coords or [])]
    route_points(board, net, [pad_a.GetPosition()] + middle + [pad_b.GetPosition()], width, layer)


def add_via(board, net, x, y, width=0.62, drill=0.32):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(v(x, y))
    via.SetWidth(nm(width))
    via.SetDrill(nm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)
    return via


def front_pad_to_back(board, net, pad, x, y, width=0.22):
    add_via(board, net, x, y)
    route_points(board, net, [pad.GetPosition(), v(x, y)], width, pcbnew.F_Cu)


def back_pad_to_xy(board, net, pad, coords, width=0.22):
    route_points(board, net, [pad.GetPosition()] + [v(x, y) for x, y in coords], width, pcbnew.B_Cu)


def setup_design_rules(board):
    settings = board.GetDesignSettings()
    settings.m_MinClearance = nm(0.10)
    settings.m_TrackMinWidth = nm(0.15)
    settings.m_MinThroughDrill = nm(0.25)
    settings.m_HoleClearance = nm(0.15)
    settings.m_SilkClearance = nm(0.10)
    settings.m_SolderMaskMinWidth = nm(0.05)
    netclass = board.GetAllNetClasses()["Default"]
    netclass.SetClearance(nm(0.10))
    netclass.SetTrackWidth(nm(0.22))
    netclass.SetViaDiameter(nm(0.62))
    netclass.SetViaDrill(nm(0.32))


def main():
    board = pcbnew.BOARD()
    setup_design_rules(board)

    nets = {
        name: add_net(board, name)
        for name in [
            "5V",
            "GND",
            "USB_D+_CONN",
            "USB_D-_CONN",
            "USB_D+",
            "USB_D-",
            "CC1",
            "CC2",
            "LED_R",
            "LED_Y",
            "LED_G",
            "LED_R_A",
            "LED_Y_A",
            "LED_G_A",
            "V33",
            "RST",
        ]
    }

    add_mechanical_outline(board)
    add_text(board, "A3", 2.0, 2.6, 0.8)

    d1 = load_fp("LED_SMD", "LED_1206_3216Metric", "D1", "\u7eff\u706f", 7.0, 7.0, 90)
    d2 = load_fp("LED_SMD", "LED_1206_3216Metric", "D2", "\u6a59\u706f", 7.0, 29.0, 90)
    d3 = load_fp("LED_SMD", "LED_1206_3216Metric", "D3", "\u7ea2\u706f", 7.0, 50.0, 90)
    r3 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R3", "1k", 4.0, 7.0, 90)
    r2 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R2", "1k", 4.0, 29.0, 90)
    r1 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R1", "1k", 4.0, 50.0, 90)
    u1 = load_fp("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm", "U1", "CH552G", 7.0, 41.5, 0)
    add_text(board, "CH552G", 8.0, 33.0, 0.8)

    r4 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R4", "22R", 6.8, 27.5, 0, True)
    r5 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R5", "22R", 9.5, 27.5, 0, True)
    r6 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R6", "5.1k", 4.0, 25.0, 0, True)
    r7 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R7", "5.1k", 11.0, 25.0, 0, True)
    c3 = load_fp("Capacitor_SMD", "C_0603_1608Metric", "C3", "100nF", 11.8, 34.0, 90)
    c2 = load_fp("Capacitor_SMD", "C_0603_1608Metric", "C2", "100nF", 11.8, 39.5, 90)
    c1 = load_fp("Capacitor_SMD", "C_0805_2012Metric", "C1", "10uF", 11.8, 44.5, 90)
    j1 = load_fp("Connector_USB", "USB_C_Receptacle_G-Switch_GT-USB-7025", "J1", "\u80cc\u9762USB-C", 7.0, 23.0, 0, True)
    tp_rst = load_fp("TestPoint", "TestPoint_Pad_D1.0mm", "TP1", "RST", 3.0, 47.5, 0)
    h1 = load_fp("MountingHole", "MountingHole_2mm", "H1", "\u4e0a\u87ba\u4e1d\u5b54", 10.8, 3.0, 0)
    h2 = load_fp("MountingHole", "MountingHole_2mm", "H2", "\u4e0b\u87ba\u4e1d\u5b54", 3.4, 34.0, 0)

    for fp in [d1, d2, d3, r1, r2, r3, u1, r4, r5, r6, r7, c1, c2, c3, j1, tp_rst, h1, h2]:
        board.Add(fp)

    set_pad_net(d1, 1, nets["GND"])
    set_pad_net(d1, 2, nets["LED_G_A"])
    set_pad_net(d2, 1, nets["GND"])
    set_pad_net(d2, 2, nets["LED_Y_A"])
    set_pad_net(d3, 1, nets["GND"])
    set_pad_net(d3, 2, nets["LED_R_A"])
    set_pad_net(r1, 1, nets["LED_R"])
    set_pad_net(r1, 2, nets["LED_R_A"])
    set_pad_net(r2, 1, nets["LED_Y"])
    set_pad_net(r2, 2, nets["LED_Y_A"])
    set_pad_net(r3, 1, nets["LED_G"])
    set_pad_net(r3, 2, nets["LED_G_A"])

    set_pad_net(u1, 2, nets["LED_R"])
    set_pad_net(u1, 3, nets["LED_Y"])
    set_pad_net(u1, 4, nets["LED_G"])
    set_pad_net(u1, 6, nets["RST"])
    set_pad_net(u1, 12, nets["USB_D+"])
    set_pad_net(u1, 13, nets["USB_D-"])
    set_pad_net(u1, 14, nets["GND"])
    set_pad_net(u1, 15, nets["5V"])
    set_pad_net(u1, 16, nets["V33"])

    set_pad_net(r4, 1, nets["USB_D+_CONN"])
    set_pad_net(r4, 2, nets["USB_D+"])
    set_pad_net(r5, 1, nets["USB_D-_CONN"])
    set_pad_net(r5, 2, nets["USB_D-"])
    set_pad_net(r6, 1, nets["CC1"])
    set_pad_net(r6, 2, nets["GND"])
    set_pad_net(r7, 1, nets["CC2"])
    set_pad_net(r7, 2, nets["GND"])
    set_pad_net(c1, 1, nets["5V"])
    set_pad_net(c1, 2, nets["GND"])
    set_pad_net(c2, 1, nets["5V"])
    set_pad_net(c2, 2, nets["GND"])
    set_pad_net(c3, 1, nets["V33"])
    set_pad_net(c3, 2, nets["GND"])
    set_pad_net(tp_rst, 1, nets["RST"])

    # USB-C 只挂接本板使用的 USB2.0、供电和 CC 焊盘；其余高速/冗余焊盘不挂网。
    set_pad_net(j1, "A1", nets["GND"])
    set_pad_net(j1, "A4", nets["5V"])
    set_pad_net(j1, "A5", nets["CC1"])
    set_pad_net(j1, "B5", nets["CC2"])
    set_pad_net(j1, "A6", nets["USB_D+_CONN"])
    set_pad_net(j1, "A7", nets["USB_D-_CONN"])

    # 正面 LED 与限流电阻短连。
    route_pad_to_pad(board, nets["LED_G_A"], pad_by_number(r3, 2), pad_by_number(d1, 2), [(4.0, 5.6)], 0.22)
    route_pad_to_pad(board, nets["LED_Y_A"], pad_by_number(r2, 2), pad_by_number(d2, 2), [(4.0, 27.6)], 0.22)
    route_pad_to_pad(board, nets["LED_R_A"], pad_by_number(r1, 2), pad_by_number(d3, 2), [(4.0, 48.6)], 0.22)

    # 三路 GPIO 用背面独立线槽，避免正面长线交叉。
    for net_name, u_pad, r_pad, ux, uy, rx, ry, lane_x in [
        ("LED_G", pad_by_number(u1, 4), pad_by_number(r3, 1), 3.2, 40.865, 3.2, 7.825, 1.0),
        ("LED_Y", pad_by_number(u1, 3), pad_by_number(r2, 1), 2.8, 39.595, 2.8, 29.825, 2.0),
        ("LED_R", pad_by_number(u1, 2), pad_by_number(r1, 1), 3.9, 38.325, 3.9, 50.825, 3.9),
    ]:
        net = nets[net_name]
        front_pad_to_back(board, net, u_pad, ux, uy)
        front_pad_to_back(board, net, r_pad, rx, ry)
        route_xy(board, net, [(ux, uy), (lane_x, uy), (lane_x, ry), (rx, ry)], 0.22, pcbnew.B_Cu)

    # USB 背面布线：端口 -> 串联电阻 -> 过孔 -> U1。
    back_pad_to_xy(board, nets["USB_D+_CONN"], pad_by_number(j1, "A6"), [(6.4, 22.4), (5.975, 22.4), (5.975, 27.5)], 0.20)
    back_pad_to_xy(board, nets["USB_D-_CONN"], pad_by_number(j1, "A7"), [(6.8, 22.0), (8.675, 22.0), (8.675, 27.5)], 0.20)
    front_pad_to_back(board, nets["USB_D+"], pad_by_number(u1, 12), 10.1, 42.135, 0.20)
    front_pad_to_back(board, nets["USB_D-"], pad_by_number(u1, 13), 10.7, 40.865, 0.20)
    route_xy(board, nets["USB_D+"], [(7.625, 27.5), (7.625, 29.0), (9.8, 29.0), (9.8, 42.135), (10.1, 42.135)], 0.20, pcbnew.B_Cu)
    route_xy(board, nets["USB_D-"], [(10.325, 27.5), (10.7, 27.5), (10.7, 40.865)], 0.20, pcbnew.B_Cu)

    # CC 下拉。
    back_pad_to_xy(board, nets["CC1"], pad_by_number(j1, "A5"), [(5.6, 21.0), (3.175, 21.0), (3.175, 25.0)], 0.20)
    back_pad_to_xy(board, nets["CC2"], pad_by_number(j1, "B5"), [(8.4, 21.0), (10.175, 21.0), (10.175, 25.0)], 0.20)
    route_xy(board, nets["GND"], [(4.825, 25.0), (4.825, 51.4), (12.8, 51.4)], 0.24, pcbnew.B_Cu)
    route_xy(board, nets["GND"], [(11.825, 25.0), (11.825, 51.4), (12.8, 51.4)], 0.24, pcbnew.B_Cu)

    # 电源母线：USB 端从背面进来，过孔后走正面右侧。
    add_via(board, nets["5V"], 8.0, 14.8)
    route_xy(board, nets["5V"], [(8.0, 14.8), (13.0, 14.8), (13.0, 45.5)], 0.30, pcbnew.F_Cu)
    back_pad_to_xy(board, nets["5V"], pad_by_number(j1, "A4"), [(4.8, 14.8), (8.0, 14.8)], 0.28)
    route_points(board, nets["5V"], [pad_by_number(u1, 15).GetPosition(), v(10.6, 37.6), v(13.0, 37.6), v(13.0, 38.325)], 0.28, pcbnew.F_Cu)
    for pad, py in [(pad_by_number(c2, 1), 40.275), (pad_by_number(c1, 1), 45.5)]:
        route_points(board, nets["5V"], [pad.GetPosition(), v(13.0, py)], 0.26, pcbnew.F_Cu)
    route_pad_to_pad(board, nets["V33"], pad_by_number(u1, 16), pad_by_number(c3, 1), [(11.8, 37.055)], 0.20)

    # 地线母线。
    route_xy(board, nets["GND"], [(12.8, 8.4), (12.8, 51.4)], 0.35, pcbnew.B_Cu)
    add_via(board, nets["GND"], 1.6, 19.55)
    add_via(board, nets["GND"], 12.8, 51.4)
    back_pad_to_xy(board, nets["GND"], pad_by_number(j1, "A1"), [(4.0, 18.5), (1.6, 18.5), (1.6, 19.55)], 0.26)
    route_xy(board, nets["GND"], [(1.6, 19.55), (1.6, 52.0), (12.8, 52.0), (12.8, 51.4)], 0.26, pcbnew.F_Cu)

    for pad, px, py in [
        (pad_by_number(d1, 1), 12.2, 8.4),
        (pad_by_number(d2, 1), 12.2, 30.4),
        (pad_by_number(d3, 1), 12.2, 51.4),
        (pad_by_number(c3, 2), 12.3, 33.225),
        (pad_by_number(c2, 2), 12.3, 38.725),
        (pad_by_number(c1, 2), 12.3, 43.5),
    ]:
        front_pad_to_back(board, nets["GND"], pad, px, py, 0.24)
        route_xy(board, nets["GND"], [(px, py), (12.8, py)], 0.28, pcbnew.B_Cu)
    route_pad_to_pad(board, nets["GND"], pad_by_number(u1, 14), pad_by_number(c2, 2), [(10.4, 39.2), (11.2, 38.725)], 0.20)

    # 复位测试点。
    route_pad_to_pad(board, nets["RST"], pad_by_number(u1, 6), pad_by_number(tp_rst, 1), [(2.7, 43.405), (2.7, 47.5)], 0.20)

    pcbnew.SaveBoard(BOARD_PATH, board)


if __name__ == "__main__":
    main()
