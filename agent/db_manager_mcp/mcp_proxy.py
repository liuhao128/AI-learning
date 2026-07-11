#!/usr/bin/env python3
"""
MCP 中间代理

仅记录：
1. Cline -> MCP Server
2. MCP Server -> Cline
"""

import argparse
import os
import subprocess
import sys
import threading
from datetime import datetime


# 日志文件路径
LOG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "mcp_io.log"
)


# =========================
# 参数解析
# =========================

parser = argparse.ArgumentParser(
    description="拦截并记录 Cline 与 MCP Server 之间的输入输出",
    usage="%(prog)s <command> [args...]"
)

parser.add_argument(
    "command",
    nargs=argparse.REMAINDER,
    help="MCP Server 启动命令及其参数"
)

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

if not args.command:
    parser.print_help(sys.stderr)
    sys.exit(1)

target_command = args.command


# =========================
# 输入输出转发
# =========================

def forward_and_log_stdin(proxy_stdin, target_stdin, log_file):
    """
    读取 Cline 的标准输入，记录日志，然后转发给 MCP Server。
    """
    try:
        while True:
            line_bytes = proxy_stdin.readline()

            if not line_bytes:
                break

            try:
                line_str = line_bytes.decode("utf-8").strip()
                timestamp = datetime.now().isoformat()

                log_file.write(
                    f"[{timestamp}] "
                    f"Cline -> MCP Server: {line_str}\n"
                )
                log_file.flush()

            except UnicodeDecodeError:
                timestamp = datetime.now().isoformat()

                log_file.write(
                    f"[{timestamp}] "
                    f"Cline -> MCP Server: "
                    f"[Binary data, {len(line_bytes)} bytes]\n"
                )
                log_file.flush()

            target_stdin.write(line_bytes)
            target_stdin.flush()

    except Exception as e:
        try:
            log_file.write(
                f"[{datetime.now().isoformat()}] "
                f"STDIN Forwarding Error: {e}\n"
            )
            log_file.flush()
        except Exception:
            pass

    finally:
        try:
            target_stdin.close()

            log_file.write(
                f"[{datetime.now().isoformat()}] "
                f"--- STDIN stream closed ---\n"
            )
            log_file.flush()

        except Exception:
            pass


def forward_and_log_stdout(
    target_stdout,
    proxy_stdout,
    log_file
):
    """
    读取 MCP Server 的标准输出，记录日志，然后转发给 Cline。
    """
    try:
        while True:
            line_bytes = target_stdout.readline()

            if not line_bytes:
                break

            try:
                line_str = line_bytes.decode("utf-8").strip()
                timestamp = datetime.now().isoformat()

                log_file.write(
                    f"[{timestamp}] "
                    f"MCP Server -> Cline: {line_str}\n"
                )
                log_file.flush()

            except UnicodeDecodeError:
                timestamp = datetime.now().isoformat()

                log_file.write(
                    f"[{timestamp}] "
                    f"MCP Server -> Cline: "
                    f"[Binary data, {len(line_bytes)} bytes]\n"
                )
                log_file.flush()

            proxy_stdout.write(line_bytes)
            proxy_stdout.flush()

    except Exception as e:
        try:
            log_file.write(
                f"[{datetime.now().isoformat()}] "
                f"STDOUT Forwarding Error: {e}\n"
            )
            log_file.flush()
        except Exception:
            pass

    finally:
        try:
            log_file.flush()
        except Exception:
            pass


# =========================
# 主程序
# =========================

process = None
log_f = None
exit_code = 1

try:
    log_f = open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    )

    log_f.write(f"\n{'=' * 80}\n")
    log_f.write(
        f"[{datetime.now().isoformat()}] MCP代理启动\n"
    )
    log_f.write(
        f"[{datetime.now().isoformat()}] "
        f"命令: {' '.join(target_command)}\n"
    )
    log_f.write(f"{'=' * 80}\n\n")
    log_f.flush()

    # 启动真正的 MCP Server
    process = subprocess.Popen(
        target_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,

        # 丢弃 MCP Server 的所有 stderr 信息
        stderr=subprocess.DEVNULL,

        # 无缓冲二进制 I/O
        bufsize=0
    )

    stdin_thread = threading.Thread(
        target=forward_and_log_stdin,
        args=(
            sys.stdin.buffer,
            process.stdin,
            log_f
        ),
        daemon=True
    )

    stdout_thread = threading.Thread(
        target=forward_and_log_stdout,
        args=(
            process.stdout,
            sys.stdout.buffer,
            log_f
        ),
        daemon=True
    )

    stdin_thread.start()
    stdout_thread.start()

    process.wait()
    exit_code = process.returncode

    stdin_thread.join(timeout=1.0)
    stdout_thread.join(timeout=1.0)

except Exception as e:
    print(
        f"MCP代理错误: {e}",
        file=sys.stderr
    )

    if log_f and not log_f.closed:
        try:
            log_f.write(
                f"[{datetime.now().isoformat()}] "
                f"主程序错误: {e}\n"
            )
            log_f.flush()
        except Exception:
            pass

    exit_code = 1

finally:
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=1.0)
        except Exception:
            pass

        if process.poll() is None:
            try:
                process.kill()
            except Exception:
                pass

    if log_f and not log_f.closed:
        try:
            log_f.write(
                f"\n[{datetime.now().isoformat()}] "
                f"MCP代理停止，退出码: {exit_code}\n"
            )
            log_f.write(f"{'=' * 80}\n\n")
            log_f.close()
        except Exception:
            pass

    sys.exit(exit_code)