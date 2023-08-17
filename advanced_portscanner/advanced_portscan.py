import socket
import threading
import argparse

def scan_port(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def scan_ports_multithread(target_ip, ports):
    open_ports = []

    def scan_port_thread(port):
        if scan_port(target_ip, port):
            open_ports.append(port)

    threads = []
    for port in ports:
        thread = threading.Thread(target=scan_port_thread, args=(port,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return open_ports

def banner_grabbing(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((target_ip, port))
        banner = sock.recv(1024).decode("utf-8").strip()
        sock.close()
        return banner
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser(description="Enhanced Port Scanner")
    parser.add_argument("target_ip", type=str, help="Target IP address")
    parser.add_argument("--start-port", type=int, default=1, help="Start of port range")
    parser.add_argument("--end-port", type=int, default=1024, help="End of port range")
    args = parser.parse_args()

    target_ip = args.target_ip
    port_range = range(args.start_port, args.end_port + 1)

    open_ports = scan_ports_multithread(target_ip, port_range)

    print(f"Scanning ports {args.start_port} to {args.end_port} on {target_ip}...")
    for port in open_ports:
        banner = banner_grabbing(target_ip, port)
        if banner:
            print(f"Port {port} is open: {banner}")
        else:
            print(f"Port {port} is open")

if __name__ == "__main__":
    main()
