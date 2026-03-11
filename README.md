https://drive.google.com/file/d/1rR7oNRwo3YqAUAPURHvCs0V9ZU42KUWe/view?usp=sharing

NOTE : Please open this link to get proper understanding of this web based application. 

# Xchat - Browser-Based Web Chat Application

**Xchat** is a browser-based web chat application built on the **WebSocket** protocol. It facilitates real-time communication, supporting private messaging, broadcast group chats, and point-to-point file transfers, even across different domains.

---

## 🚀 Features
* **Online User List:** Real-time visibility of active users.
* **Private Messaging:** Secure one-to-one communication between users.
* **Broadcast Messaging:** Group messages sent to all online users.
* **Point-to-Point File Transfer:** Direct one-to-one file sharing.
* **Cross-Domain Support:** Full functionality across different server domains.

---

## 🛠️ Tech Stack
* **Server-Side:** Python
* **Client-Side:** HTML, JavaScript (Standard Web APIs)

---

## 📋 Prerequisites
### Infrastructure
* All users must be connected to the same local network (Local Wi-Fi or Hotspot).

### Server Requirements
1.  **Python 3.8+**
    * **Linux:** `sudo apt update && sudo apt install python3.8 python3.8-venv`
    * **macOS:** `brew install python@3.8`
    * **Windows:** Download the installer from [python.org](https://www.python.org/) (ensure "Add Python to PATH" is checked).
2.  **Required Libraries:**
    ```bash
    pip install art cryptography websockets
    ```

### Client Requirements
* Any modern web browser (Google Chrome, Mozilla Firefox, etc.). No external dependencies required.

---

## ⚙️ Configuration

### 1. Server Configuration (`config.py`)
Modify the `DOMAIN`, `server_mapping`, and `registered_users` in `config.py`:

```python
# Define your server domain
DOMAIN = "s2"

# Map domain names to WebSocket URIs
server_mapping = {
    "s1": "ws://10.13.83.155:5555",
    "s2": "ws://[YOUR_LOCAL_IP]:5555",
    "s4": "ws://10.13.101.145:5555"
}

# User database (JID: Hashed Password)
# Generate hashes using hash.py
registered_users = {
    "tushar@s2": "7d082e414f09c5ca390197afe48109943e2597c782e58e4262b14303477c1b6b"
}
