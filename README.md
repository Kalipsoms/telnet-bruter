# 🔐 TelnetBrute (Python 3)

**TelnetBrute** is a fast, multithreaded Telnet brute-forcer written in Python 3.  
It tests common username/password combinations against a list of IPs over port 23.
---

## 💡 Features

- Pure **Python 3**, no external libraries
- **Multithreaded** for high speed
- Customizable **combo list**
- Saves valid credentials to output file
- Designed for **testing your own devices**

---

## 📦 Usage

```bash
python3 telnet_brute.py <ip_list.txt> <threads> <output.txt>
