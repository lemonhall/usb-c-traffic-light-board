import pcbnew


BOARD_PATH = r"E:\development\usb-c-traffic-light-board\kicad\usb_c_traffic_light_board.kicad_pcb"
FP_ROOT = r"E:\KiCad\10.0\share\kicad\footprints"
ROUTE_DRAFT_TRACES = False
BOARD_ORIGIN_X = 141.5
BOARD_ORIGIN_Y = 76.5


def nm(mm_value):
    return int(mm_value * 1_000_000)


def size_vec(x, y):
    return pcbnew.VECTOR2I(nm(x), nm(y))


def v(x, y):
    return pcbnew.VECTOR2I(nm(BOARD_ORIGIN_X + x), nm(BOARD_ORIGIN_Y + y))


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def pad_by_number(fp, number):
    for pad in fp.Pads():
        if pad.GetNumber() == str(number):
            return pad
    raise ValueError(f"{fp.GetReference()} has no pad {number}")


def set_pad_net(fp, pad_number, net):
    pad_by_number(fp, pad_number).SetNet(net)


def load_fp(lib_name, footprint_name, ref, value, x, y, rot=0):
    fp = pcbnew.FootprintLoad(FP_ROOT + "\\" + lib_name + ".pretty", footprint_name)
    if fp is None:
        raise RuntimeError(f"Cannot load footprint {lib_name}:{footprint_name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(v(x, y))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    return fp


def put_on_back(fp):
    # KiCad 10.0.3 pcbnew.FOOTPRINT.Flip() crashes for this USB-C footprint in
    # headless Python. Set the placement layer here; mirror/orientation can be
    # finalized in KiCad after the exact rear connector is selected.
    fp.SetLayer(pcbnew.B_Cu)
    return fp


def add_line(board, x1, y1, x2, y2, layer, width=0.12):
    item = pcbnew.PCB_SHAPE(board)
    item.SetShape(pcbnew.SHAPE_T_SEGMENT)
    item.SetStart(v(x1, y1))
    item.SetEnd(v(x2, y2))
    item.SetLayer(layer)
    item.SetWidth(nm(width))
    board.Add(item)


def add_rect(board, x1, y1, x2, y2, layer, width=0.12):
    add_line(board, x1, y1, x2, y1, layer, width)
    add_line(board, x2, y1, x2, y2, layer, width)
    add_line(board, x2, y2, x1, y2, layer, width)
    add_line(board, x1, y2, x1, y1, layer, width)


def add_text(board, text, x, y, size=0.8):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(v(x, y))
    item.SetLayer(pcbnew.F_SilkS)
    item.SetTextSize(size_vec(size, size))
    item.SetTextThickness(nm(size * 0.12))
    board.Add(item)


def add_track(board, net, start, end, width=0.25, layer=pcbnew.F_Cu):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(nm(width))
    track.SetLayer(layer)
    track.SetNet(net)
    board.Add(track)


def connect(board, net, pad_a, pad_b, width=0.25):
    add_track(board, net, pad_a.GetPosition(), pad_b.GetPosition(), width)


def main():
    board = pcbnew.BOARD()

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

    add_rect(board, 0, 0, 14, 57, pcbnew.Edge_Cuts, 0.1)
    add_text(board, "A2", 1.2, 1.8, 0.8)

    # Match the original traffic-light board: green at top, amber/yellow in middle,
    # red at bottom, all centered on the narrow 14 mm board.
    d1 = load_fp("LED_SMD", "LED_1206_3216Metric", "D1", "\u7eff\u706f", 7.0, 7.0, 90)
    d2 = load_fp("LED_SMD", "LED_1206_3216Metric", "D2", "\u6a59\u706f", 7.0, 29.0, 90)
    d3 = load_fp("LED_SMD", "LED_1206_3216Metric", "D3", "\u7ea2\u706f", 7.0, 50.0, 90)

    r3 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R3", "1k", 11.0, 7.0, 90)
    r2 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R2", "1k", 11.0, 29.0, 90)
    r1 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R1", "1k", 11.0, 50.0, 90)

    u1 = load_fp("Package_SO", "SOIC-16_3.9x9.9mm_P1.27mm", "U1", "CH552G", 7.0, 39.0, 0)

    r4 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R4", "22R", 2.4, 34.5, 90)
    r5 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R5", "22R", 3.9, 34.5, 90)
    r6 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R6", "5.1k", 10.2, 34.5, 90)
    r7 = load_fp("Resistor_SMD", "R_0603_1608Metric", "R7", "5.1k", 11.8, 34.5, 90)
    c3 = load_fp("Capacitor_SMD", "C_0603_1608Metric", "C3", "100nF", 2.5, 42.5, 90)
    c2 = load_fp("Capacitor_SMD", "C_0603_1608Metric", "C2", "100nF", 11.5, 42.5, 90)
    c1 = load_fp("Capacitor_SMD", "C_0805_2012Metric", "C1", "10uF", 11.5, 46.0, 90)
    # Back-side vertical USB-C receptacle at the original rear switch opening area.
    j1 = put_on_back(load_fp("Connector_USB", "USB_C_Receptacle_G-Switch_GT-USB-7051x", "J1", "\u80cc\u9762\u7acb\u5f0fUSB-C", 7.0, 21.0, 0))

    for fp in [d1, d2, d3, r1, r2, r3, u1, r4, r5, r6, r7, c1, c2, c3, j1]:
        board.Add(fp)

    # LED footprints use pad 1 as cathode and pad 2 as anode in KiCad's LED_SMD library.
    set_pad_net(d3, 1, nets["GND"])
    set_pad_net(d3, 2, nets["LED_R_A"])
    set_pad_net(d2, 1, nets["GND"])
    set_pad_net(d2, 2, nets["LED_Y_A"])
    set_pad_net(d1, 1, nets["GND"])
    set_pad_net(d1, 2, nets["LED_G_A"])

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

    for pad_name in ["A4", "A9", "B4", "B9"]:
        set_pad_net(j1, pad_name, nets["5V"])
    for pad_name in ["A1", "A12", "B1", "B12", "SH"]:
        for pad in j1.Pads():
            if pad.GetNumber() == pad_name:
                pad.SetNet(nets["GND"])
    for pad_name in ["A6", "B6"]:
        set_pad_net(j1, pad_name, nets["USB_D+_CONN"])
    for pad_name in ["A7", "B7"]:
        set_pad_net(j1, pad_name, nets["USB_D-_CONN"])
    set_pad_net(j1, "A5", nets["CC1"])
    set_pad_net(j1, "B5", nets["CC2"])

    if ROUTE_DRAFT_TRACES:
        connect(board, nets["LED_R"], pad_by_number(u1, 2), pad_by_number(r1, 1))
        connect(board, nets["LED_Y"], pad_by_number(u1, 3), pad_by_number(r2, 1))
        connect(board, nets["LED_G"], pad_by_number(u1, 4), pad_by_number(r3, 1))
        connect(board, nets["LED_R_A"], pad_by_number(r1, 2), pad_by_number(d3, 2))
        connect(board, nets["LED_Y_A"], pad_by_number(r2, 2), pad_by_number(d2, 2))
        connect(board, nets["LED_G_A"], pad_by_number(r3, 2), pad_by_number(d1, 2))
        connect(board, nets["USB_D+"], pad_by_number(u1, 12), pad_by_number(r4, 2), 0.2)
        connect(board, nets["USB_D-"], pad_by_number(u1, 13), pad_by_number(r5, 2), 0.2)
        connect(board, nets["USB_D+_CONN"], pad_by_number(r4, 1), pad_by_number(j1, "A6"), 0.2)
        connect(board, nets["USB_D-_CONN"], pad_by_number(r5, 1), pad_by_number(j1, "A7"), 0.2)
        connect(board, nets["CC1"], pad_by_number(j1, "A5"), pad_by_number(r6, 1), 0.2)
        connect(board, nets["CC2"], pad_by_number(j1, "B5"), pad_by_number(r7, 1), 0.2)
        connect(board, nets["5V"], pad_by_number(j1, "A4"), pad_by_number(c1, 1), 0.35)
        connect(board, nets["5V"], pad_by_number(c1, 1), pad_by_number(c2, 1), 0.35)
        connect(board, nets["5V"], pad_by_number(c2, 1), pad_by_number(u1, 15), 0.35)
        connect(board, nets["V33"], pad_by_number(u1, 16), pad_by_number(c3, 1), 0.2)

    add_text(board, "TP", 1.0, 55.0, 0.8)

    pcbnew.SaveBoard(BOARD_PATH, board)


if __name__ == "__main__":
    main()
