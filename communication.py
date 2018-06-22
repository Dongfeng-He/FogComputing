import socket


def find_idle_port():
    for port in range(10000, 65535):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.bind(("", port))
            s.settimeout(None)
            s.close()
            idle_port = port
            break
        except Exception:
            pass

    return idle_port
