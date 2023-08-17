import socket
import threading
import concurrent.futures
import argparse
import os
import time

def scan_port(target_ip, port, protocol='tcp', timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def scan_ports_threadpool(target_ip, ports, thread_count=10, protocol='tcp'):
    open_ports = []

    def scan_port_thread(port):
        if scan_port(target_ip, port, protocol=protocol, timeout=0.5):
            open_ports.append(port)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(scan_port_thread, ports)

    return open_ports

def banner_grabbing(target_ip, port, protocol='tcp', timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.connect((target_ip, port))
        banner = sock.recv(1024).decode("utf-8").strip()
        sock.close()
        return banner
    except Exception as e:
        return None

def save_results(filename, target_ip, open_ports):
    with open(filename, 'w') as file:
        file.write(f"Open ports for {target_ip}:\n")
        for port in open_ports:
            file.write(f"Port {port}\n")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Port Scanner")
    parser.add_argument("target_ip", type=str, help="Target IP address")
    parser.add_argument("--start-port", type=int, default=1, help="Start of port range")
    parser.add_argument("--end-port", type=int, default=1024, help="End of port range")
    parser.add_argument("--thread-count", type=int, default=10, help="Number of threads for scanning")
    parser.add_argument("--protocol", type=str, default='tcp', choices=['tcp', 'udp'], help="Protocol to scan (TCP or UDP)")
    parser.add_argument("--output-file", type=str, default=None, help="Output file for results")
    args = parser.parse_args()

    target_ip = args.target_ip
    port_range = range(args.start_port, args.end_port + 1)

    open_ports = scan_ports_threadpool(target_ip, port_range, thread_count=args.thread_count, protocol=args.protocol)

    print(f"Scanning ports {args.start_port} to {args.end_port} on {target_ip} using {args.protocol.upper()}...")
    for port in open_ports:
        banner = banner_grabbing(target_ip, port, protocol=args.protocol)
        if banner:
            print(f"Port {port} is open: {banner}")
        else:
            print(f"Port {port} is open")

    if args.output_file:
        save_results(args.output_file, target_ip, open_ports)
        print(f"Results saved to {args.output_file}")

if __name__ == "__main__":
    main()
