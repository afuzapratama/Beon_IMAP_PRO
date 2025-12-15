# 📧 IMAP Login Checker

Tool untuk testing kredensial login IMAP dengan support SOCKS5 proxy (termasuk SSH Tunnel).

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repo
git clone git@github.com:afuzapratama/Beon_IMAP_PRO.git
cd Beon_IMAP_PRO

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install PySocks  # Untuk proxy support yang lebih baik
```

### 2. Siapkan File Input

Buat file dengan format `email:password` per baris:

```
user1@gmail.com:password123
user2@yahoo.com:mypassword
user3@softbank.jp:secret123
```

---

## 🔒 Setup Proxy (SSH Tunnel)

**PENTING:** Banyak IMAP server akan block IP kamu kalau terlalu banyak request. Gunakan SSH Tunnel sebagai SOCKS5 proxy.

### Cara Setup SSH Tunnel

**Terminal 1** - Jalankan SSH Tunnel (biarkan running):

```bash
ssh -D 1080 -N -C username@ip-server-kamu
```

**Penjelasan flags:**
- `-D 1080` = Buat SOCKS5 proxy di port 1080
- `-N` = Tidak execute command, hanya tunnel
- `-C` = Compress traffic (lebih cepat)

**Contoh:**
```bash
ssh -D 1080 -N -C root@151.241.109.140
```

Kalau sukses, terminal akan **diam/hang** (tidak ada output) - itu normal!

---

## 📖 Cara Penggunaan

### Mode 1: Interactive (Recommended untuk pemula)

```bash
source venv/bin/activate
python imap_checker.py
```

Menu interaktif akan muncul:

```
╔══════════════════════════════════════════════════════════╗
║             📧 IMAP LOGIN CHECKER v2.0 📧                ║
╚══════════════════════════════════════════════════════════╝

  [1] 📄 Set Input File
  [2] 💾 Set Output Files  
  [3] 🔒 Configure Proxy (SOCKS5)
  [4] ⚙️  Settings
  [5] 🧪 Test Single Login
  [6] 🚀 START CHECKING
  [7] 📋 Show Supported Domains
  [0] 🚪 Exit
```

### Mode 2: CLI (Command Line)

**Basic usage:**
```bash
python imap_checker.py --cli -i input.txt -P "localhost:1080" -T 30 -v
```

**Full options:**
```bash
python imap_checker.py --cli \
  -i data.txt \              # Input file (required)
  -o success.txt \           # Output success (optional, auto jika tidak diset)
  -f failed.txt \            # Output failed (optional, auto jika tidak diset)
  -O hasil \                 # Output directory (default: hasil)
  -P "localhost:1080" \      # Proxy host:port
  -U proxyuser \             # Proxy username (optional)
  -W proxypass \             # Proxy password (optional)
  -T 30 \                    # Timeout dalam detik
  -t 1 \                     # Sleep antar request (detik)
  -s \                       # Show success only
  -v                         # Verbose mode
```

---

## 📁 Output Structure

Hasil akan otomatis disimpan dengan struktur rapi:

```
hasil/
└── 2025-12-15/
    ├── success/
    │   └── success_20251215_143022.txt
    └── failed/
        └── failed_20251215_143022.txt
```

---

## 💡 Contoh Penggunaan

### Test 1 Email (tanpa proxy)

```bash
python imap_checker.py --cli -i test.txt -T 10 -v
```

### Test dengan SSH Tunnel

**Terminal 1:**
```bash
ssh -D 1080 -N -C root@your-server-ip
```

**Terminal 2:**
```bash
python imap_checker.py --cli -i emails.txt -P "localhost:1080" -T 30 -v
```

### Test dengan External SOCKS5 Proxy

```bash
python imap_checker.py --cli -i emails.txt \
  -P "proxy.example.com:1080" \
  -U myusername \
  -W mypassword \
  -T 30
```

---

## 📋 Supported Email Domains

Script mendukung 46+ domain email. Lihat `domains.ini` untuk daftar lengkap.

**Contoh domain yang didukung:**
- Gmail (gmail.com)
- Yahoo (yahoo.com, yahoo.co.jp, ymail.com)
- Outlook/Hotmail (outlook.com, hotmail.com, live.com)
- iCloud (icloud.com, me.com)
- Softbank (i.softbank.jp)
- Dan banyak lagi...

### Menambah Domain Baru

Edit `domains.ini`:

```ini
[newdomain.com]
imap = imap.newdomain.com
port = 993
ssl = True
```

---

## ⚠️ Troubleshooting

### "IMAP4 server terminating connection"
- **Penyebab:** IP kamu di-block oleh server
- **Solusi:** Gunakan SSH Tunnel atau VPN

### "SSL record layer failure"  
- **Penyebab:** Proxy tidak support SSL tunneling
- **Solusi:** Gunakan SSH Tunnel (pasti work)

### "Connection not allowed by ruleset"
- **Penyebab:** Proxy block koneksi ke mail server
- **Solusi:** Gunakan proxy lain atau SSH Tunnel

### Proxy tidak terdetect
- Pastikan SSH Tunnel sudah jalan (terminal diam = sukses)
- Cek port: `netstat -tlnp | grep 1080`

---

## 🔧 Requirements

- Python 3.8+
- Dependencies: `requirements.txt`
  - SocksiPy_branch
  - PySocks  
  - termcolor
  - validators

---

## 📜 License

MIT License

---

## 👤 Author

- **afuzapratama**
- GitHub: [@afuzapratama](https://github.com/afuzapratama)
