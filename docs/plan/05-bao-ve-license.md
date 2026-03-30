## 5. Bảo Vệ License & Chống Copy

### 5.1 Vấn Đề Cần Giải Quyết

```
User mua $89 → Download .exe → Copy file gửi bạn bè → Bạn bè dùng free?
User mua $89 → Lấy license key → Post lên forum → 1000 người dùng chung?
User mua $89 → Crack app → Upload lên torrent → Ai cũng tải free?
```

> **Thực tế:** Không tool nào chống crack 100%. Nhưng có thể chặn 85-95% piracy thông thường.

### 5.2 Kiến Trúc Bảo Vệ 5 Lớp

```
┌─────────────────────────────────────────────────────────────┐
│  LỚP 1: NUITKA COMPILE                                      │
│  Python → C → Native binary (.exe/.app)                      │
│  Source code KHÔNG THỂ decompile ngược lại                   │
├─────────────────────────────────────────────────────────────┤
│  LỚP 2: PYARMOR OBFUSCATION                                 │
│  Encrypt bytecode + obfuscate logic                          │
│  Biến code thành dạng không đọc được                         │
├─────────────────────────────────────────────────────────────┤
│  LỚP 3: HARDWARE FINGERPRINT (Machine Binding)              │
│  1 license key = tối đa 3 máy tính                           │
│  Copy .exe sang máy khác → KHÔNG CHẠY ĐƯỢC                  │
├─────────────────────────────────────────────────────────────┤
│  LỚP 4: ONLINE LICENSE VALIDATION (Keygen.sh)               │
│  Mở app → gọi API verify key + máy                           │
│  Key bị share → phát hiện + khóa từ xa                       │
├─────────────────────────────────────────────────────────────┤
│  LỚP 5: FEATURE GATING                                      │
│  Cloud sync, auto-update, marketplace → CẦN ACCOUNT         │
│  Crack được app nhưng không có cloud features                │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Chi Tiết Từng Lớp Bảo Vệ

#### Lớp 1: Nuitka Compile (Chống Decompile)

| Vấn đề | PyInstaller (không dùng) | Nuitka (dùng cái này) |
|---------|-------------------------|----------------------|
| Đóng gói | Bundle .pyc files → dễ extract | Compile Python → C → native binary |
| Decompile | `pyinstxtractor` + `uncompyle6` = lấy lại source | **Không thể** decompile ngược native code |
| Performance | Chậm (interpret bytecode) | Nhanh hơn 2-4x (native code) |
| Kích thước | Lớn (bundle cả Python runtime) | Nhỏ hơn |

```bash
# Build với Nuitka
nuitka --standalone --onefile --enable-plugin=tk-inter \
       --company-name="MoneyPrinterTurbo" \
       --product-name="MoneyPrinterTurbo" \
       --output-dir=dist \
       main.py
```

#### Lớp 2: PyArmor Obfuscation (Chống Đọc Logic)

```bash
# Obfuscate trước khi compile
pyarmor gen --enable-jit --enable-bcc --mix-str \
            --bind-device "HDD:SERIAL" "MAC:ADDRESS" \
            --period 30 \
            main.py

# Kết quả: code Python biến thành dạng không đọc được
# Ngay cả nếu extract được, cũng chỉ thấy gibberish
```

| Feature | Mô Tả |
|---------|--------|
| `--enable-jit` | Convert Python functions → compiled C at runtime |
| `--enable-bcc` | Compile bytecode → native code |
| `--mix-str` | Encrypt tất cả strings trong code |
| `--bind-device` | Bind vào hardware cụ thể |
| `--period 30` | License hết hạn sau 30 ngày (cho trial) |

> Chi phí PyArmor: ~$56 (personal) hoặc ~$268 (business license)

#### Lớp 3: Hardware Fingerprint (Chống Copy .exe)

**Cách hoạt động:**

```
Máy của User A:
┌────────────────────────────┐
│ MAC Address: 70:f1:a1:23.. │
│ HDD Serial: PBN2081SF3..   │
│ CPU Info: Intel i7-13700K  │
│ OS Machine ID: a8f2e...    │
├────────────────────────────┤
│ SHA-256 Hash = "abc123..."  │ ← Hardware Fingerprint
└────────────────────────────┘

Lần đầu mở app:
  App tạo fingerprint "abc123..." → Gửi lên server cùng license key
  Server lưu: Key MPT-XXXX = máy "abc123..."
  Server trả về: ✅ Activated

User copy .exe sang máy B:
  Máy B có fingerprint khác: "xyz789..."
  App gửi: Key MPT-XXXX + fingerprint "xyz789..."
  Server check: Key này đã bind máy "abc123...", không match!
  Server trả về: ❌ Rejected → App không chạy
```

**Thuật toán fingerprint (dùng nhiều yếu tố, cho phép 1-2 thay đổi):**

```python
import hashlib, uuid, platform

def get_machine_fingerprint():
    """Tạo fingerprint từ 4-5 yếu tố hardware"""
    components = []

    # 1. MAC Address (network card)
    components.append(hex(uuid.getnode()))

    # 2. Machine name + architecture
    components.append(platform.node())
    components.append(platform.machine())

    # 3. OS-level machine ID
    #    Windows: HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid
    #    Linux: /etc/machine-id
    components.append(get_os_machine_id())

    # 4. Disk serial number
    components.append(get_disk_serial())

    raw = "|".join(components)
    return hashlib.sha256(raw.encode()).hexdigest()
```

**Fuzzy matching:** Nếu user thay ổ cứng hoặc đổi card mạng, vẫn match được nếu 3/5 yếu tố giống → không lock user vô lý.

**Giới hạn thiết bị:**

| App tham khảo | Số máy/license |
|---------------|---------------|
| Microsoft 365 | 5 |
| JetBrains | Unlimited máy, 1 user đồng thời |
| Sublime Text | Unlimited máy, 1 user |
| Typora | 3 |
| **MPT (đề xuất)** | **3 máy** (desktop + laptop + dự phòng) |

User muốn đổi máy? → Tự deactivate máy cũ trong web portal → Activate máy mới.

#### Lớp 4: Online License Validation (Keygen.sh)

**Flow chi tiết:**

```
┌─ LẦN ĐẦU MỞ APP ─────────────────────────────────────────┐
│                                                             │
│  1. User nhập license key: MPT-XXXX-XXXX-XXXX              │
│  2. App tạo hardware fingerprint                            │
│  3. App gọi: POST keygen.sh/api/v1/machines                │
│     Body: { key: "MPT-XXXX", fingerprint: "abc123" }       │
│  4. Server check:                                           │
│     ├─ Key hợp lệ? ✅                                      │
│     ├─ Còn slot máy? (< 3 máy) ✅                          │
│     ├─ Key chưa bị revoke? ✅                               │
│     └─ → Trả về signed license token                        │
│  5. App lưu token vào local (encrypted file)                │
│  6. App chạy bình thường ✅                                 │
└─────────────────────────────────────────────────────────────┘

┌─ CÁC LẦN MỞ APP SAU ─────────────────────────────────────┐
│                                                             │
│  Có internet:                                               │
│  → Verify token online → Cập nhật cache → Chạy OK          │
│                                                             │
│  Không có internet:                                         │
│  → Check cached token (signed, có expiry)                   │
│  → Nếu cache < 30 ngày → Chạy OK (offline grace)          │
│  → Nếu cache > 30 ngày → Yêu cầu kết nối internet 1 lần  │
└─────────────────────────────────────────────────────────────┘
```

**Heartbeat monitoring (chống dùng đồng thời):**

```
App chạy → Ping server mỗi 30 phút: "Máy abc123 vẫn active"
Server: Nếu máy không ping > 48 giờ → Tự động deactivate
→ Giải phóng slot cho máy khác
→ User format máy cũ? Slot tự free sau 48h, không cần support
```

**Phát hiện key bị share:**

| Dấu hiệu | Hành động |
|-----------|-----------|
| Cùng key activate từ 5+ quốc gia khác nhau | Flag + gửi email cảnh báo cho buyer |
| 10+ máy cố activate trong 1 tuần | Tạm khóa key + yêu cầu verify email |
| Key xuất hiện trên forum/torrent | Revoke key + gửi key mới cho buyer gốc |
| Velocity bất thường | Rate limit activations |

#### Lớp 5: Feature Gating (Chống Crack Triệt Để)

Ngay cả nếu ai đó crack được app, một số features **vẫn cần server**:

```
┌─────────────────────────────────────────────────────────┐
│  FEATURES CHẠY LOCAL (crack được)                        │
│  ├── Video generation pipeline                           │
│  ├── Effects & transitions                               │
│  └── Basic rendering                                     │
│                                                          │
│  FEATURES CẦN SERVER/ACCOUNT (crack không được)          │
│  ├── Auto-update (cần verify license mới download)       │
│  ├── Template marketplace (cần account để browse/buy)    │
│  ├── Plugin marketplace (cần account)                    │
│  ├── Cloud rendering ($9.99/mo)                          │
│  ├── Auto-publishing (OAuth tokens lưu trên server)      │
│  ├── Analytics dashboard (data trên server)              │
│  ├── Voice cloning models (download cần auth)            │
│  └── Priority support                                    │
│                                                          │
│  → User crack chỉ được 40-50% features                  │
│  → Features hay nhất đều cần account hợp lệ             │
└─────────────────────────────────────────────────────────┘
```

### 5.4 Tech Stack Bảo Vệ License

| Component | Công Cụ | Chi Phí | Vai Trò |
|-----------|---------|---------|---------|
| **Source protection** | Nuitka | Free (open-source) | Compile Python → native binary |
| **Obfuscation** | PyArmor | $56-$268 | Encrypt + obfuscate + hardware bind |
| **License management** | Keygen.sh | Free (≤25 licenses) → $49-$249/mo | Activation, machine binding, heartbeat |
| **Payment** | Paddle hoặc Stripe | 5% + $0.50/txn | Thu tiền, handle tax toàn cầu |
| **Anti-tamper** | Nuitka + PyArmor combo | Đã tính ở trên | Detect binary modification |

**Tại sao Keygen.sh thay vì LemonSqueezy?**
- LemonSqueezy bị Stripe mua (07/2024), roadmap không rõ ràng
- Keygen.sh chuyên về licensing, có machine fingerprint, heartbeat, floating license
- Keygen.sh có Python SDK, SOC 2 Type II compliant
- Kết hợp: **Keygen.sh** (licensing) + **Paddle/Stripe** (payment)

### 5.5 Các App Thực Tế Đang Làm Gì?

| App | Cách bảo vệ | Kết quả |
|-----|-------------|---------|
| **Sublime Text** | Offline crypto key, no machine binding | Bị crack phổ biến, nhưng vẫn profitable nhờ corporate buyers |
| **JetBrains** | Online subscription + account + offline 30 days | Rất ít crack, recurring revenue tốt |
| **Sketch** | Key + device limit + server-side block | Hiệu quả, bị crack ít |
| **Typora** | Key + online activation + 3 devices | Tốt cho indie app |
| **Figma** | Account-based, cloud rendering | Không crack được (cần server) |

### 5.6 Thực Tế Về Piracy

| Thống kê | Số liệu |
|----------|---------|
| % piracy trung bình (indie apps) | ~50% installations |
| % pirates sẽ mua nếu không crack được | Chỉ 5-25% |
| % piracy chặn được với online activation + binding | 85-95% casual piracy |
| Determined crackers (hacker giỏi) | **Không thể chặn 100%** |

**Triết lý đúng:**

> "Không cố chặn 100% piracy. Cố làm cho việc mua EASY và việc crack ANNOYING."
>
> - $89 vẫn rẻ hơn tốn công crack → Hầu hết người chọn mua
> - Business users PHẢI mua (rủi ro pháp lý)
> - Pirates = free marketing → một số sẽ convert thành buyers sau
> - Focus vào features cần server → crack cũng không có full experience

### 5.7 User Experience (Không Làm Phiền User Thật)

| Nguyên tắc | Chi tiết |
|-------------|----------|
| **Silent activation** | Nhập key 1 lần, sau đó auto-verify ngầm |
| **Offline grace 30 ngày** | Không bao giờ khóa app vì mất wifi |
| **Self-service deactivation** | User tự quản lý devices trên web portal |
| **3 máy/key** | Desktop + laptop + dự phòng, đủ thoải mái |
| **Soft failure** | Hết grace → cảnh báo + 7 ngày gia hạn, KHÔNG xóa data |
| **Fast support** | Format máy? → Reset activations trong 1 click |
| **Không accusatory** | Không hiện "Bạn đang dùng bản lậu!", chỉ hiện "Vui lòng verify license" |

---

