## 6. Business Infrastructure (Server, Website, Team License)

### 6.1 Trả Lời Câu Hỏi Chính: Có Cần Server Không?

**KHÔNG cần server riêng.** Toàn bộ hệ thống chạy trên managed services, không cần mua/thuê/maintain server nào.

```
┌─────────────────────────────────────────────────────────────┐
│  BẠN KHÔNG CẦN:                                             │
│  ✗ VPS / Dedicated server                                    │
│  ✗ Database server (MySQL, PostgreSQL...)                    │
│  ✗ DevOps / System admin                                     │
│  ✗ SSL certificates (tự quản lý)                            │
│                                                              │
│  BẠN CHỈ CẦN:                                               │
│  ✓ Paddle/LemonSqueezy account (thu tiền + tax)             │
│  ✓ Keygen.sh account (quản lý license, free tier)           │
│  ✓ Landing page (Carrd $9/năm hoặc static site free)       │
│  ✓ 1 serverless function (Vercel free) để nối payment→key  │
│  ✓ Domain name (~$12/năm)                                    │
│                                                              │
│  TỔNG CHI PHÍ CỐ ĐỊNH: ~$2/tháng                           │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Kiến Trúc Tổng Quan Hệ Thống

```
  USER JOURNEY:
  ═════════════

  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────────┐
  │ 1. Xem   │    │ 2. Mua    │    │ 3. Nhận  │    │ 4. Dùng      │
  │ Landing  │───→│ Checkout  │───→│ License  │───→│ Desktop App  │
  │ Page     │    │ Paddle    │    │ Key      │    │              │
  └──────────┘    └───────────┘    └──────────┘    └──────────────┘
       │               │                │                │
       ▼               ▼                ▼                ▼

  INFRASTRUCTURE:
  ═══════════════

  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────────┐
  │ Carrd.co │    │ Paddle    │    │ Vercel   │    │ Keygen.sh    │
  │ hoặc     │    │           │    │ Function │    │ (Cloud)      │
  │ Vercel   │    │ Thu tiền  │    │          │    │              │
  │          │    │ Handle tax│───→│ Webhook: │───→│ Tạo license  │
  │ Landing  │    │ Invoice   │    │ Payment  │    │ Bind máy     │
  │ page     │    │ Refund    │    │ success  │    │ Verify key   │
  │          │    │           │    │ → Create │    │ Deactivate   │
  │ $9/năm   │    │ 5%+$0.50  │    │   key    │    │ Heartbeat    │
  │          │    │ /giao dịch│    │          │    │              │
  └──────────┘    └───────────┘    │ FREE     │    │ FREE (≤100   │
                       │           └──────────┘    │  users)      │
                       ▼                           └──────────────┘
                  ┌───────────┐                          │
                  │ Customer  │                          │
                  │ Portal    │         ┌────────────────┘
                  │ (Paddle   │         │
                  │  hosted)  │         ▼
                  │           │    ┌──────────────┐
                  │ Invoice   │    │ Desktop App  │
                  │ Thanh toán│    │              │
                  │ Subscription   │ Gọi Keygen   │
                  └───────────┘    │ API verify   │
                                   │ license +    │
                                   │ fingerprint  │
                                   └──────────────┘
```

### 6.3 Chi Tiết Từng Service

#### A. Payment: Paddle (Recommend) hoặc LemonSqueezy

| | Paddle | LemonSqueezy |
|--|--------|-------------|
| **Vai trò** | Thu tiền, xử lý tax toàn cầu, invoice, refund | Tương tự |
| **Phí** | 5% + $0.50/giao dịch | 5% + $0.50/giao dịch |
| **Tax/VAT** | Tự xử lý hộ (Merchant of Record) | Tương tự (MoR) |
| **Customer portal** | Có sẵn (hosted by Paddle) | Cơ bản |
| **License key** | Không có built-in | Có built-in (cơ bản) |
| **Webhook** | Có (payment.completed event) | Có |
| **KYC process** | 1-6 tuần verify | Nhanh hơn |
| **Stability** | Ổn định, lâu đời | Bị Stripe mua (07/2024), roadmap chưa rõ |

> **Recommend: Paddle** cho stability. Hoặc **LemonSqueezy** nếu muốn start nhanh (KYC nhanh hơn + có sẵn license key cơ bản).

**Bạn không cần lo:**
- Tax/VAT: Paddle/LS tự tính và nộp cho mỗi quốc gia
- Invoice: Tự động gửi cho customer
- Refund: Customer tự request, bạn approve/deny
- Currency: Tự chuyển đổi, trả bạn bằng USD

#### B. License Management: Keygen.sh

| Hạng mục | Chi tiết |
|----------|----------|
| **Vai trò** | Quản lý license keys, machine binding, activation limits, heartbeat |
| **Free tier** | 100 active licensed users (đủ cho giai đoạn đầu) |
| **Paid tier** | Scale theo số users, fair pricing |
| **Self-hosted** | Có thể (open-source, Docker) khi muốn tiết kiệm |
| **Python SDK** | Không có SDK chính thức, dùng REST API (rất đơn giản) |
| **Offline support** | Có - signed license files (Ed25519 + AES-256-GCM) |

**Keygen quản lý gì:**
```
┌─ Keygen Dashboard ──────────────────────────────────┐
│                                                      │
│  Licenses:                                           │
│  ├── MPT-XXXX-1111 (Pro, 3 máy max)                │
│  │   ├── Machine: abc123 (Desktop Win11) ✅ Active  │
│  │   ├── Machine: def456 (Laptop Mac) ✅ Active     │
│  │   └── [1 slot còn trống]                         │
│  │                                                   │
│  ├── MPT-XXXX-2222 (Pro, 3 máy max)                │
│  │   ├── Machine: ghi789 ✅ Active                  │
│  │   └── [2 slots còn trống]                        │
│  │                                                   │
│  └── MPT-TEAM-3333 (Team 5 seats)                   │
│      ├── User: admin@company.com (2 machines)        │
│      ├── User: dev1@company.com (1 machine)          │
│      ├── User: dev2@company.com (1 machine)          │
│      └── [2 seats còn trống]                         │
│                                                      │
│  Analytics:                                          │
│  ├── Total active licenses: 47                       │
│  ├── Total machines: 89                              │
│  ├── Activations today: 5                            │
│  └── Failed validations: 2 (suspicious)              │
└──────────────────────────────────────────────────────┘
```

#### C. Landing Page + Website

**Phase 1 (Launch): Carrd.co - $9/năm**

```
┌─ moneyprinterturbo.com ─────────────────────────────┐
│                                                      │
│  [HERO]                                              │
│  "Tạo Video Tự Động Bằng AI. Từ $7.99/tháng."      │
│  [Screenshot/Demo GIF]                               │
│  [  MUA NGAY  ]  [  TẢI FREE  ]                    │
│                                                      │
│  [FEATURES] - 3-4 features chính với hình            │
│  [DEMO VIDEO] - 60s video showing the tool           │
│  [PRICING] - Free / Monthly / Yearly / Lifetime      │
│  [TESTIMONIALS] - GitHub stars + user quotes         │
│  [FAQ]                                               │
│  [FOOTER] - Links, support, social                   │
└──────────────────────────────────────────────────────┘
```

**Phase 2 (Growth): Custom site - Next.js + Vercel (FREE)**

```
moneyprinterturbo.com/           → Landing page
moneyprinterturbo.com/pricing    → Pricing + checkout
moneyprinterturbo.com/download   → Download latest version
moneyprinterturbo.com/docs       → Documentation
moneyprinterturbo.com/portal     → Customer portal (manage devices)
moneyprinterturbo.com/templates  → Template marketplace
```

#### D. Webhook Handler: Vercel Serverless Function (FREE)

Khi user mua hàng, Paddle gửi webhook → Vercel function tạo license key:

```python
# api/webhook.py (deploy trên Vercel, ~50 dòng code)

import hmac, hashlib, json, requests

KEYGEN_API = "https://api.keygen.sh/v1/accounts/{ACCOUNT_ID}"
KEYGEN_TOKEN = "your-keygen-admin-token"
PADDLE_WEBHOOK_SECRET = "your-paddle-secret"

def handler(request):
    # 1. Verify webhook từ Paddle
    body = request.body
    signature = request.headers.get("Paddle-Signature")
    if not verify_paddle_signature(body, signature):
        return {"status": 401}

    event = json.loads(body)

    # 2. Lấy thông tin order
    if event["event_type"] != "transaction.completed":
        return {"status": 200}

    customer_email = event["data"]["customer"]["email"]
    product_id = event["data"]["items"][0]["price"]["product_id"]

    # 3. Xác định loại license dựa trên product
    if product_id == "PROD_PRO":
        max_machines = 3
        policy_id = "POLICY_PRO"
    elif product_id == "PROD_TEAM":
        max_machines = 15  # 5 users × 3 machines
        policy_id = "POLICY_TEAM"

    # 4. Tạo license key trên Keygen
    response = requests.post(
        f"{KEYGEN_API}/licenses",
        headers={
            "Authorization": f"Bearer {KEYGEN_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "data": {
                "type": "licenses",
                "attributes": {
                    "metadata": {"email": customer_email}
                },
                "relationships": {
                    "policy": {
                        "data": {"type": "policies", "id": policy_id}
                    }
                }
            }
        }
    )

    license_key = response.json()["data"]["attributes"]["key"]

    # 5. Gửi email chứa license key (hoặc Paddle đã gửi receipt)
    # send_email(customer_email, license_key)

    return {"status": 200, "key": license_key}
```

### 6.4 Team License: Hoạt Động Như Nào?

#### Câu hỏi: "5 người dùng = cài 5 máy luôn?"

**Không hẳn.** Team license = **5 seats (chỗ ngồi)**, mỗi seat = 1 user, mỗi user có thể dùng trên nhiều máy.

```
┌─ TEAM LICENSE: "ACME Corp" (5 seats) ───────────────┐
│                                                      │
│  Seat 1: admin@acme.com                              │
│  ├── Desktop (office) ✅                             │
│  └── Laptop (home) ✅                                │
│                                                      │
│  Seat 2: dev1@acme.com                               │
│  └── Laptop ✅                                       │
│                                                      │
│  Seat 3: dev2@acme.com                               │
│  └── Desktop ✅                                      │
│                                                      │
│  Seat 4: designer@acme.com                           │
│  ├── iMac ✅                                         │
│  └── MacBook ✅                                      │
│                                                      │
│  Seat 5: [Chưa assign]                               │
│                                                      │
│  Tổng: 5 seats, 6 machines active                    │
│  Rule: Mỗi user tối đa 3 machines                   │
│        Tối đa 5 users trong team                     │
└──────────────────────────────────────────────────────┘
```

#### Flow Mua Team License

```
1. Admin vào website → Chọn "Team Pack $99" → Thanh toán

2. Webhook tạo 1 GROUP trên Keygen:
   - Group: "ACME Corp"
   - Max users: 5
   - Max machines per user: 3

3. Admin nhận email với:
   - Team license key: MPT-TEAM-XXXX
   - Link invite team members: moneyprinterturbo.com/team/join/XXXX

4. Admin gửi link cho team members

5. Mỗi member:
   - Click link → Nhập email → Nhận personal activation code
   - Mở desktop app → Nhập activation code
   - App tạo fingerprint → Gọi Keygen API activate
   - ✅ Done

6. Admin quản lý trên web portal:
   - Xem ai đang dùng
   - Remove member (giải phóng seat)
   - Mời member mới
```

#### So Sánh Individual vs Team

| | Paid (Individual) | Team Pack $99 (Add-on) |
|--|---------------------|------------------------|
| **Users** | 1 người | 5 người |
| **Machines/user** | 3 máy | 3 máy |
| **Total machines max** | 3 | 15 |
| **Admin dashboard** | Không | Có (web portal) |
| **Invite members** | Không | Có |
| **Centralized billing** | Không | Có (1 invoice) |

> **Lưu ý:** Team Pack là **add-on**, buyer phải có paid plan trước. Ví dụ: Lifetime $89 + Team $99 = $188 cho 5 người = $37.6/người (one-time). Rất rẻ so với SaaS $20-30/người/tháng.

### 6.5 User Portal: Tự Quản Lý Devices

#### Phase 1 (MVP): Không cần web portal

User quản lý ngay trong desktop app:

```
┌─ Desktop App → Settings → License ──────────────────┐
│                                                      │
│  License: MPT-XXXX-XXXX-XXXX          Status: ✅    │
│  Plan: Pro                                           │
│  Devices: 2/3 used                                   │
│                                                      │
│  Your devices:                                       │
│  ┌────────────────────────────────────────────┐      │
│  │ 🖥️ DESKTOP-ABC  Windows 11  [This device] │      │
│  │ 💻 LAPTOP-XYZ   macOS 15    [Deactivate]  │      │
│  └────────────────────────────────────────────┘      │
│                                                      │
│  [Deactivate This Device]  [Buy More Seats]          │
└──────────────────────────────────────────────────────┘
```

- App gọi Keygen API `GET /machines` → hiển thị danh sách máy
- User click "Deactivate" → `DELETE /machines/{id}` → giải phóng slot
- **Không cần web portal**, mọi thứ trong app

#### Phase 2 (Growth): Web Portal đơn giản

```
moneyprinterturbo.com/portal
┌─────────────────────────────────────────────────────┐
│  👤 user@email.com              [Logout]            │
│                                                      │
│  License: MPT-XXXX-XXXX         Plan: Pro           │
│                                                      │
│  ┌─ Devices (2/3) ──────────────────────────────┐   │
│  │ 🖥️ DESKTOP-ABC  Win11   Active  [Deactivate]│   │
│  │ 💻 LAPTOP-XYZ   macOS   Active  [Deactivate]│   │
│  │ ➕ 1 slot available                           │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Downloads ───────────────────────────────────┐   │
│  │ v1.3.0 (latest) [Windows] [macOS] [Linux]    │   │
│  │ v1.2.1          [Windows] [macOS] [Linux]    │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Billing (Paddle) ───────────────────────────┐   │
│  │ [View Invoices]  [Manage Subscription]        │   │
│  │ (redirects to Paddle customer portal)         │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 6.6 Chi Phí Hạ Tầng Chi Tiết

#### Giai Đoạn Launch (0-100 customers)

| Service | Chi phí | Ghi chú |
|---------|---------|---------|
| Domain name | $12/năm (~$1/mo) | moneyprinterturbo.com |
| Carrd.co landing page | $9/năm (~$0.75/mo) | Hoặc Vercel free |
| Paddle account | $0/mo | Chỉ % per transaction |
| Keygen.sh Cloud | $0/mo | Free tier: 100 users |
| Vercel (webhook + portal) | $0/mo | Free tier đủ dùng |
| GitHub (releases hosting) | $0/mo | Free |
| Email (transactional) | $0/mo | Paddle gửi receipt hộ |
| **TỔNG CỐ ĐỊNH** | **~$2/tháng** | |

#### Chi phí per sale

```
User mua Lifetime $89:
  Paddle fee: 5% + $0.50 = $4.95
  → Bạn nhận: $84.05

User mua Team Pack $99:
  Paddle fee: 5% + $0.50 = $5.45
  → Bạn nhận: $93.55

User mua Cloud $9.99/mo:
  Paddle fee: 5% + $0.50 = $1.00
  → Bạn nhận: $8.99/mo
```

#### Giai Đoạn Growth (100-1000 customers)

| Service | Chi phí | Ghi chú |
|---------|---------|---------|
| Domain | $12/năm | Giữ nguyên |
| Vercel Pro | $20/mo | Custom domain, analytics |
| Keygen.sh Standard | ~$49-99/mo | Scale theo users |
| Paddle | $0/mo + % | Giữ nguyên |
| Transactional email (Resend) | $0-20/mo | Welcome emails, notifications |
| **TỔNG CỐ ĐỊNH** | **~$70-140/tháng** | |

#### Giai Đoạn Scale (1000+ customers)

| Service | Chi phí | Ghi chú |
|---------|---------|---------|
| Keygen self-hosted (Docker) | ~$20/mo VPS | Tiết kiệm vs cloud tier |
| Vercel Pro | $20/mo | Giữ nguyên |
| Hoặc: Custom Next.js trên VPS | $20-40/mo | Full control |
| **TỔNG CỐ ĐỊNH** | **~$40-60/tháng** | Tiết kiệm hơn nhờ self-host |

### 6.7 Timeline Setup Business Infrastructure

```
┌─ TUẦN 1-2: Payment + License ───────────────────────┐
│                                                      │
│  Ngày 1:  Đăng ký Paddle account (bắt đầu KYC)     │
│  Ngày 1:  Đăng ký Keygen.sh account (instant)       │
│  Ngày 2:  Setup Keygen policies:                     │
│           - Policy "Pro": maxMachines=3              │
│           - Policy "Team": maxUsers=5, maxMach=3/user│
│  Ngày 3:  Tạo products trên Paddle:                 │
│           - Lifetime $89 (one-time)                   │
│           - Team Pack $99 (one-time)                 │
│           - Cloud $9.99/mo (subscription)            │
│           - Add-ons ($19-29 each)                    │
│  Ngày 4-5: Code webhook (Vercel function):           │
│           - Paddle payment.completed → Keygen create │
│           - Test end-to-end flow                     │
│  Ngày 6-7: Integrate license check vào desktop app: │
│           - First launch: nhập key → activate        │
│           - Subsequent: cached token + periodic check│
│           - Offline grace: 30 days                   │
└──────────────────────────────────────────────────────┘

┌─ TUẦN 3: Landing Page ──────────────────────────────┐
│                                                      │
│  Ngày 8-9:  Mua domain + setup DNS                  │
│  Ngày 10-11: Tạo landing page (Carrd hoặc Next.js)  │
│  Ngày 12:   Embed Paddle checkout buttons            │
│  Ngày 13:   Setup download delivery (GitHub Releases)│
│  Ngày 14:   Test full purchase flow end-to-end       │
│             User → Landing → Buy → Key → App → ✅   │
└──────────────────────────────────────────────────────┘

┌─ TUẦN 4: Polish + Launch ───────────────────────────┐
│                                                      │
│  Ngày 15-16: Viết FAQ, docs, getting started guide  │
│  Ngày 17-18: Beta test với 5-10 users thật          │
│  Ngày 19:    Fix bugs từ beta feedback               │
│  Ngày 20:    LAUNCH 🚀                              │
│  Ngày 21:    Monitor + support first customers       │
└──────────────────────────────────────────────────────┘

┌─ SAU LAUNCH (khi có 50+ customers): ────────────────┐
│                                                      │
│  - Build web portal (device management)              │
│  - Add team management features                      │
│  - Setup transactional emails (welcome, tips...)     │
│  - Thêm analytics / customer insights               │
└──────────────────────────────────────────────────────┘
```

### 6.8 Tổng Kết Business Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│              TOÀN BỘ HỆ THỐNG BẠN CẦN                       │
│                                                              │
│  🌐 WEBSITE: Carrd ($9/năm) hoặc Next.js+Vercel (free)     │
│     → Landing page + pricing + download                      │
│                                                              │
│  💳 PAYMENT: Paddle (5%+$0.50/giao dịch, $0/tháng)         │
│     → Thu tiền, tax, invoice, refund, customer portal        │
│                                                              │
│  🔑 LICENSE: Keygen.sh (free ≤100 users)                    │
│     → License keys, machine binding, activation limits       │
│     → Team groups, heartbeat, offline validation             │
│                                                              │
│  ⚡ WEBHOOK: Vercel serverless function (free)               │
│     → Nối Paddle → Keygen: payment thành công → tạo key     │
│                                                              │
│  📦 DOWNLOAD: GitHub Releases (free)                         │
│     → Host .exe/.dmg/.AppImage files                         │
│                                                              │
│  🏢 TEAM: Keygen Groups API                                 │
│     → 5 seats/team, mỗi user 3 máy, admin quản lý          │
│                                                              │
│  💰 TỔNG CHI PHÍ: ~$2/tháng cố định + 5% per sale          │
│  ⏱️ SETUP TIME: ~3-4 tuần                                   │
│  🔧 SERVER MAINTENANCE: KHÔNG CẦN (all managed)             │
└─────────────────────────────────────────────────────────────┘
```

---

