"""USB-C 红绿灯控制板的电脑端辅助脚本。

用法：
    python traffic_light.py COM7 "S 1 0 0"
    python traffic_light.py COM7 "?"

依赖：
    pip install pyserial
"""

from __future__ import annotations

import argparse
import serial


def send_command(port: str, command: str, baud: int = 115200, timeout: float = 1.0) -> str:
    with serial.Serial(port, baudrate=baud, timeout=timeout) as ser:
        ser.write((command.strip() + "\n").encode("ascii"))
        ser.flush()
        return ser.readline().decode("ascii", errors="replace").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="串口号，例如 COM7")
    parser.add_argument("command", help='控制命令，例如 "S 1 0 0"')
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()

    print(send_command(args.port, args.command, args.baud))


if __name__ == "__main__":
    main()
