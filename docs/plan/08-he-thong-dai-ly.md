## 8. Hệ Thống Đại Lý (Agent/Reseller) - Scale Toàn Cầu

### 8.1 Mô Hình Đại Lý

```
┌─────────────────────────────────────────────────────────────┐
│                    MÔ HÌNH PHÂN PHỐI                         │
│                                                              │
│  BẠN (Vendor)                                                │
│    │                                                         │
│    ├── Bán trực tiếp (Website, Paddle)  ← giá retail        │
│    │                                                         │
│    └── Bán qua Đại Lý (Reseller Portal) ← giá sỉ -40%     │
│         │                                                    │
│         ├── Đại lý VN: tự bán giá tùy ý cho thị trường VN  │
│         ├── Đại lý JP: tự bán cho thị trường Nhật           │
│         ├── Đại lý BR: tự bán cho thị trường Brazil         │
│         ├── Đại lý IN: tự bán cho thị trường Ấn Độ         │
│         └── ... (mỗi nước/khu vực 1 đại lý)                │
│                                                              │
│  Đại lý TỰ tạo key, TỰ bán, TỰ thu tiền                   │
│  Bạn KHÔNG quan tâm họ bán bao nhiêu, giá bao nhiêu        │
│  Bạn CHỈ thu tiền sỉ khi đại lý mua key                    │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Cách Hoạt Động Chi Tiết

#### Flow Đại Lý Mua Key

```
1. Đại lý đăng ký trên Reseller Portal
   → Duyệt + ký hợp đồng đại lý online

2. Đại lý nạp tiền / mua key theo batch
   ┌─────────────────────────────────────┐
   │  Mua 50 keys Lifetime  × $53.40    │ (giá sỉ = $89 × 60%)
   │  = Trả bạn $2,670                  │
   │                                      │
   │  Mua 100 keys Monthly  × $4.79/key │ (giá sỉ = $7.99 × 60%)
   │  = Trả bạn $479                    │
   └─────────────────────────────────────┘

3. Đại lý nhận keys trong portal
   → Keys nằm trong "kho" của đại lý
   → Đại lý activate cho khách khi bán

4. Đại lý tự bán cho khách
   → Giá bán TÙY đại lý (miễn ≥ MAP)
   → Đại lý tự thu tiền từ khách
   → Đại lý tự support khách (tier 1)
```

#### Flow Khách Mua Từ Đại Lý

```
Khách ở VN muốn mua:
  1. Vào website đại lý VN (hoặc Shopee, Facebook...)
  2. Chuyển khoản / MoMo / ZaloPay cho đại lý
  3. Đại lý vào Reseller Portal → Activate 1 key cho khách
  4. Khách nhận key qua email/Zalo
  5. Khách nhập key vào app → Done ✅

Lợi ích cho khách VN:
  → Trả bằng VND, qua MoMo/ZaloPay (không cần thẻ quốc tế!)
  → Được support bằng tiếng Việt
  → Giá có thể rẻ hơn (đại lý tự quyết)
```

### 8.3 Phân Chia Rõ: Đại Lý Bán Gì, Bạn Bán Gì?

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ĐẠI LÝ CHỈ BÁN ONE-TIME:        BẠN BÁN TRỰC TIẾP:      │
│  ✅ Lifetime $89                   ✅ Monthly $7.99/mo      │
│  ✅ Voice Cloning $29              ✅ Yearly $59.99/yr      │
│  ✅ Team Pack $99                  ✅ Lifetime $89           │
│  ✅ Analytics Pro $19              ✅ Tất cả add-ons        │
│  ✅ Template Creator $19                                     │
│                                                              │
│  Đại lý thu tiền 1 lần            Paddle thu recurring      │
│  Đại lý support local             Bạn support global        │
│                                                              │
│  TẠI SAO TÁCH:                                              │
│  - Monthly cần billing system → đại lý không có             │
│  - Khách cancel tháng 2 → ai refund? ai chịu?              │
│  - Quá phức tạp → đại lý chỉ bán one-time = sạch sẽ       │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 Gói Key Lifetime Cho Đại Lý

#### 4 Gói Mua Sỉ

| Gói | Số Key | Discount | Giá/Key | Tổng Trả Trước | Đại Lý Lời/Key |
|-----|--------|----------|---------|----------------|----------------|
| **Starter** | 20 keys | 35% off | $57.85 | **$1,157** | $31.15 (35%) |
| **Growth** | 100 keys | 40% off | $53.40 | **$5,340** | $35.60 (40%) |
| **Pro** | 300 keys | 45% off | $48.95 | **$14,685** | $40.05 (45%) |
| **Enterprise** | 1000 keys | 50% off | $44.50 | **$44,500** | $44.50 (50%) |

#### Add-ons Đại Lý Mua Kèm (Cùng % Discount Theo Tier)

| Gói Đại Lý | Voice Cloning ($29) | Team Pack ($99) | Analytics ($19) | Template Creator ($19) |
|-------------|--------------------|-----------------| ----------------| ----------------------|
| Starter (35%) | $18.85 | $64.35 | $12.35 | $12.35 |
| Growth (40%) | $17.40 | $59.40 | $11.40 | $11.40 |
| Pro (45%) | $15.95 | $54.45 | $10.45 | $10.45 |
| Enterprise (50%) | $14.50 | $49.50 | $9.50 | $9.50 |

#### Chi Tiết Lợi Nhuận Từng Gói

```
┌─ GÓI STARTER (20 keys = $1,157) ────────────────────────┐
│                                                           │
│  Đại lý bán retail $89/key:                               │
│    20 × $89 = $1,780 → Lời $623 (35% margin)            │
│                                                           │
│  Đại lý bán $79/key (giảm chút cho local):              │
│    20 × $79 = $1,580 → Lời $423 (27% margin)            │
│                                                           │
│  Timeline bán hết: 1-3 tháng (đại lý mới)               │
│  Target: Đại lý mới muốn test thị trường                 │
└───────────────────────────────────────────────────────────┘

┌─ GÓI GROWTH (100 keys = $5,340) ────────────────────────┐
│                                                           │
│  Đại lý bán retail $89/key:                               │
│    100 × $89 = $8,900 → Lời $3,560 (40% margin)         │
│                                                           │
│  Đại lý bán $75/key (cạnh tranh):                        │
│    100 × $75 = $7,500 → Lời $2,160 (29% margin)         │
│                                                           │
│  Timeline bán hết: 2-4 tháng                              │
│  Target: Đại lý đã có khách, bán đều                      │
└───────────────────────────────────────────────────────────┘

┌─ GÓI PRO (300 keys = $14,685) ──────────────────────────┐
│                                                           │
│  Đại lý bán retail $89/key:                               │
│    300 × $89 = $26,700 → Lời $12,015 (45% margin)       │
│                                                           │
│  Đại lý bán $69/key (giá cực tốt cho local market):     │
│    300 × $69 = $20,700 → Lời $6,015 (29% margin)        │
│                                                           │
│  Timeline bán hết: 3-6 tháng                              │
│  Target: Đại lý chuyên nghiệp, có kênh bán hàng         │
└───────────────────────────────────────────────────────────┘

┌─ GÓI ENTERPRISE (1000 keys = $44,500) ──────────────────┐
│                                                           │
│  Đại lý bán retail $89/key:                               │
│    1000 × $89 = $89,000 → Lời $44,500 (50% margin!)     │
│                                                           │
│  Đại lý bán $65/key (dominate local market):             │
│    1000 × $65 = $65,000 → Lời $20,500 (32% margin)      │
│                                                           │
│  Timeline bán hết: 6-12 tháng                             │
│  Target: Distributor lớn, agency                          │
└───────────────────────────────────────────────────────────┘
```

#### Ví Dụ Thực Tế: Đại Lý VN Mua Gói Growth

```
Đại lý VN trả: $5,340 (≈ 134 triệu VND) → Nhận 100 Lifetime keys

Bán cho khách VN giá 1,800,000₫/key (≈ $72):
  Thu về: 100 × 1,800,000 = 180 triệu VND
  Chi:    134 triệu VND
  LỜI:    46 triệu VND (34% margin)

Hoặc bán 2,000,000₫/key (≈ $80):
  Thu về: 200 triệu VND
  LỜI:    66 triệu VND (33% margin)

Khách VN lợi gì?
  → Trả bằng MoMo/ZaloPay/bank transfer (không cần thẻ quốc tế!)
  → Được support tiếng Việt
  → Giá rẻ hơn mua trực tiếp ($72-80 vs $89)

Timeline bán hết: 2-4 tháng
→ Đại lý kiếm 46-66 triệu/2-4 tháng chỉ bán key
```

### 8.5 Thanh Toán Đại Lý: Trả Trước, Nhận Key Ngay

| Gói | Tổng Tiền | Cách Trả | Nhận Key |
|-----|-----------|----------|----------|
| **Starter** ($1,157) | Trả 100% trước | 20 keys ngay lập tức |
| **Growth** ($5,340) | 100% trước, hoặc 2 đợt (50/50) | 100% → nhận hết, hoặc 50 keys/đợt |
| **Pro** ($14,685) | 3 đợt: 40% / 30% / 30% trong 60 ngày | Nhận keys tương ứng mỗi đợt |
| **Enterprise** ($44,500) | Thương lượng riêng | Thương lượng riêng |

```
Gói Pro trả 3 đợt:
  Ngày 0:   Trả $5,874 (40%)  → Nhận 120 keys
  Ngày 30:  Trả $4,406 (30%)  → Nhận 90 keys
  Ngày 60:  Trả $4,406 (30%)  → Nhận 90 keys

  Không trả đợt 2? → Chỉ có 120 keys, stop
  Bạn đã nhận $5,874 cho 120 keys → không mất gì

Gói Growth trả 2 đợt:
  Ngày 0:   Trả $2,670 (50%)  → Nhận 50 keys
  Ngày 30:  Trả $2,670 (50%)  → Nhận 50 keys

  Không trả đợt 2? → Chỉ có 50 keys
  Bạn đã nhận $2,670 cho 50 keys → vẫn đúng giá Growth
```

> **Nguyên tắc: Bạn LUÔN nhận tiền trước khi giao key. Zero risk.**

### 8.6 Reseller Portal (Trang Quản Lý Cho Đại Lý)

```
┌─ reseller.moneyprinterturbo.com ────────────────────────────┐
│                                                              │
│  👤 Đại Lý: TechVN Corp          Tier: Growth (40% off)    │
│  Territory: Vietnam + SEA         Keys còn: 23              │
│                                                              │
│  ┌─ Dashboard ──────────────────────────────────────────┐   │
│  │  Lifetime keys còn: 23                                │   │
│  │  Đã bán tháng này: 27 keys                           │   │
│  │  Tổng khách active: 142                               │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Mua Thêm Keys ────────────────────────────────────┐    │
│  │                                                      │    │
│  │  Gói hiện tại: Growth (40% off)                      │    │
│  │  Giá/key: $53.40                                     │    │
│  │                                                      │    │
│  │  Mua thêm: [10] [20] [50] [100] keys                │    │
│  │  Thanh toán: [Wire Transfer] [Wise] [PayPal]        │    │
│  │                                                      │    │
│  │  Nâng tier Pro (300+ keys total): giảm thêm 5%      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Key Management ───────────────────────────────────┐     │
│  │                                                     │     │
│  │  [  ACTIVATE KEY CHO KHÁCH  ]                       │     │
│  │                                                     │     │
│  │  Key Pool (Lifetime):                               │     │
│  │  ├── MPT-LT-001  Available   [Activate]             │     │
│  │  ├── MPT-LT-002  Available   [Activate]             │     │
│  │  ├── MPT-LT-003  Sold → user@email.com  2 devices  │     │
│  │  └── ...                                            │     │
│  │                                                     │     │
│  │  Add-ons Pool:                                      │     │
│  │  ├── MPT-VC-001  Voice Cloning  Available           │     │
│  │  ├── MPT-TP-001  Team Pack      Sold → biz@co.vn   │     │
│  │  └── ...                                            │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ Customers ────────────────────────────────────────┐     │
│  │  user@email.com    Lifetime  2 devices  Active     │     │
│  │  biz@company.vn    LT+Team   8 devices  Active     │     │
│  │  other@gmail.com   Lifetime  1 device   Active     │     │
│  │  [Export CSV]                                       │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ Reports ──────────────────────────────────────────┐     │
│  │  [Doanh số tháng] [Doanh số quý] [Export CSV]      │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─ API Access ───────────────────────────────────────┐     │
│  │  API Key: rsl_xxxxxxxxxxxx                          │     │
│  │  Docs: reseller.moneyprinterturbo.com/api/docs     │     │
│  │  → Tích hợp vào hệ thống bán hàng riêng            │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### 8.7 Technical: Xây Dựng Reseller System

#### Kiến Trúc

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Reseller    │     │  Your Backend│     │  Keygen.sh   │
│  Portal      │────→│  (API)       │────→│  (License    │
│  (React)     │     │  (FastAPI)   │     │   Server)    │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────┴─────┐
                     │  Your DB  │
                     │ (SQLite/  │
                     │ Postgres) │
                     └───────────┘

  Reseller Portal lưu:         Keygen.sh lưu:
  - Reseller accounts          - License keys
  - Pricing tiers              - Machine activations
  - Purchase history           - Groups (per reseller)
  - Revenue reports            - Metadata (reseller_id)
  - Payout records             - Heartbeat
```

#### Keygen.sh Setup Cho Mỗi Đại Lý

```python
# 1. Tạo Group cho đại lý
POST /v1/accounts/{account}/groups
{
  "data": {
    "type": "groups",
    "attributes": {
      "name": "Reseller-TechVN",
      "maxLicenses": 500,
      "metadata": {
        "reseller_id": "techvn",
        "territory": "VN,TH,ID",
        "tier": "silver",
        "discount": 0.45
      }
    }
  }
}

# 2. Tạo scoped API token cho đại lý
# Chỉ cho phép: tạo license, đọc license, validate
# KHÔNG cho phép: xóa, sửa policy, admin

# 3. Đại lý tạo key cho khách
POST /v1/accounts/{account}/licenses
{
  "data": {
    "type": "licenses",
    "attributes": {
      "metadata": {
        "reseller_id": "techvn",
        "customer_email": "user@email.com",
        "sold_price": 1800000  // VND
      }
    },
    "relationships": {
      "policy": { "data": { "type": "policies", "id": "LIFETIME" } },
      "group": { "data": { "type": "groups", "id": "reseller-techvn" } }
    }
  }
}
```

### 8.8 Chống Đại Lý Phá Giá (MAP Policy)

#### MAP = Minimum Advertised Price

```
┌─────────────────────────────────────────────────────────────┐
│  QUY TẮC: Đại lý KHÔNG được quảng cáo giá thấp hơn MAP    │
│                                                              │
│  MAP Lifetime: $79  (retail $89, đại lý lời ít nhất $25)   │
│  MAP Yearly:   $49  (retail $59.99)                         │
│  MAP Monthly:  $5.99 (retail $7.99)                         │
│                                                              │
│  Đại lý có thể:                                             │
│  ✅ Bán giá $79-$89 (trong khoảng MAP → retail)             │
│  ✅ Giảm giá thêm cho khách VIP (riêng tư, không quảng cáo)│
│  ✅ Bundle với services khác                                 │
│                                                              │
│  Đại lý KHÔNG được:                                         │
│  ❌ Quảng cáo giá dưới $79 trên website/Facebook/Shopee    │
│  ❌ Bán key cho đại lý khác (sub-distribution)              │
│  ❌ Bán ngoài territory được assign                         │
│                                                              │
│  Vi phạm:                                                    │
│  Lần 1: Cảnh báo                                            │
│  Lần 2: Giảm discount tier                                  │
│  Lần 3: Chấm dứt hợp tác, revoke keys chưa bán            │
└─────────────────────────────────────────────────────────────┘
```

### 8.9 Đại Lý Từng Khu Vực

| Khu Vực | Đại Lý Cần | Tại Sao | Payment Khách Local |
|---------|-----------|---------|---------------------|
| **Vietnam** | 1-2 | Khách VN trả MoMo/ZaloPay, không có thẻ quốc tế | MoMo, ZaloPay, bank transfer |
| **China** | 1-2 | WeChat Pay, Alipay dominant, cần entity local | WeChat, Alipay, UnionPay |
| **Japan** | 1 | Konbini payment, domestic cards preferred | Konbini, JCB, PayPay |
| **South Korea** | 1 | KakaoPay, Toss dominant | KakaoPay, Toss, Samsung Pay |
| **Brazil** | 1 | PIX, Boleto popular | PIX, Boleto, Mercado Pago |
| **India** | 1-2 | UPI dominant, giá PPP cần local knowledge | UPI, Paytm, PhonePe |
| **SE Asia** | 1-2 | GrabPay, GCash, các ví local | GrabPay, GCash, DANA |
| **Middle East** | 1 | Arabic support cần native speaker | STC Pay, Mada |

> **Lợi thế lớn nhất:** Đại lý giải quyết payment methods local mà Paddle không hỗ trợ.
> Khách VN muốn trả MoMo? → Đại lý VN thu MoMo, activate key. Done.

### 8.10 Revenue Từ Đại Lý vs Trực Tiếp

```
GIẢ SỬ: 1000 khách qua trực tiếp + 2000 khách qua đại lý

TRỰC TIẾP (1000 khách, bạn nhận ~93% sau phí Paddle):
  Lifetime: 200 × $89 × 93%                    = $16,554
  Monthly:  500 × $7.99 × 9.6mo avg × 93%      = $35,607
  Yearly:   200 × $59.99 × 93%                  = $11,158
  Add-ons:  100 × $29 × 93%                     = $2,697
                                                  ─────────
  Subtotal trực tiếp:                             $66,016

ĐẠI LÝ (2000 khách, chỉ bán Lifetime + add-ons, bạn nhận giá sỉ):
  Lifetime: 1600 × $53.40 (avg Growth tier)     = $85,440
  Add-ons:  400 × $17.40 avg                    = $6,960
                                                  ─────────
  Subtotal đại lý:                                $92,400

TỔNG NĂM 1 (3000 khách):                         $158,416 ✅
```

> **So sánh: Không có đại lý = $66K. Có đại lý = $158K.** Gấp 2.4x!
> Đại lý CHỈ bán Lifetime + add-ons (one-time). Monthly/Yearly bạn bán trực tiếp qua Paddle.
> Đại lý mang đến 2000 khách mà bạn KHÔNG THỂ tiếp cận trực tiếp (vì payment local, language, trust).

### 8.11 Timeline Xây Dựng Hệ Thống Đại Lý

```
┌─ PHASE 1 (Tháng 1-2): MVP Reseller Portal ─────────────────┐
│                                                              │
│  Tuần 1-2: Backend API cho reseller (FastAPI)                │
│    - Reseller registration + approval                        │
│    - Key purchase/generation (gọi Keygen.sh API)             │
│    - Key activation cho khách                                │
│    - Basic reporting                                         │
│                                                              │
│  Tuần 3-4: Frontend Portal (React)                           │
│    - Dashboard, key management, customer list                │
│    - Purchase keys (integrate payment)                       │
│    - Reports export                                          │
│                                                              │
│  Chi phí dev: ~2-4 tuần fulltime                             │
└──────────────────────────────────────────────────────────────┘

┌─ PHASE 2 (Tháng 3-4): Recruit Đại Lý Đầu Tiên ────────────┐
│                                                              │
│  Tháng 3: Recruit 3-5 đại lý (VN, China, Japan)            │
│  Tháng 4: Onboard, training, test full flow                  │
│  Tháng 5: Đại lý bắt đầu bán                               │
│                                                              │
│  Cách tìm đại lý:                                           │
│  - Tech distributors có sẵn trong nước                       │
│  - Freelancers/agencies làm marketing AI tools               │
│  - Existing customers muốn kinh doanh thêm                  │
│  - Facebook groups, forums cộng đồng tech local             │
└──────────────────────────────────────────────────────────────┘

┌─ PHASE 3 (Tháng 5+): Scale ────────────────────────────────┐
│                                                              │
│  - Thêm đại lý cho các khu vực mới                          │
│  - API access cho đại lý lớn (tích hợp vào hệ thống họ)    │
│  - Volume tier auto-upgrade                                  │
│  - White-label option cho đại lý Platinum                    │
│  - Đại lý tuyển sub-agents (nếu cho phép)                  │
└──────────────────────────────────────────────────────────────┘
```

### 8.12 Thanh Toán Quốc Tế Cho/Từ Đại Lý

#### Mô hình: Đại Lý MUA SỈ trước, bán sau

```
Đại lý mua 50 keys:
  1. Đại lý chuyển $2,670 cho bạn (wire/Wise/Payoneer)
  2. Bạn confirm payment
  3. System tạo 50 keys trong pool đại lý
  4. Đại lý bán dần, activate cho từng khách

  → Bạn KHÔNG CẦN trả tiền cho đại lý
  → Đại lý tự thu tiền từ khách, tự giữ margin
  → Cash flow tốt: bạn nhận tiền TRƯỚC khi khách dùng
```

#### Thanh toán quốc tế

| Platform | Phí | Tốt cho |
|----------|-----|---------|
| **Wise** | 0.5-1.5% | Đại lý ở mọi nơi, phí thấp nhất |
| **Payoneer** | 1-2% | Đại lý ở markets khó (India, SE Asia) |
| **Bank wire** | $15-30/lần | Đại lý lớn, mua batch lớn |
| **PayPal** | 3-5% | Đại lý nhỏ, tiện lợi |

### 8.13 Tổng Kết Hệ Thống Đại Lý

```
┌─────────────────────────────────────────────────────────────┐
│              HỆ THỐNG ĐẠI LÝ TOÀN CẦU                      │
│                                                              │
│  🏪 MÔ HÌNH: Đại lý CHỈ bán Lifetime + add-ons (one-time) │
│     Monthly/Yearly bạn bán trực tiếp qua Paddle             │
│                                                              │
│  💰 4 GÓI:                                                  │
│     Starter (20 keys)  35% off  $1,157                      │
│     Growth (100 keys)  40% off  $5,340                      │
│     Pro (300 keys)     45% off  $14,685                     │
│     Enterprise (1000)  50% off  $44,500                     │
│                                                              │
│  📊 THANH TOÁN: Trả trước nhận key ngay                    │
│     Gói lớn cho trả 2-3 đợt (nhận key tương ứng mỗi đợt)  │
│                                                              │
│  🌍 ĐẠI LÝ: 8-10 khu vực (VN, CN, JP, KR, BR, IN, SEA...)│
│                                                              │
│  🖥️ PORTAL: Dashboard + key management + reports + API      │
│                                                              │
│  📜 MAP POLICY: Giá quảng cáo tối thiểu để không phá giá   │
│                                                              │
│  💸 CASH FLOW: Đại lý trả trước → nhận keys → bán dần     │
│     Bạn nhận tiền TRƯỚC, không rủi ro                        │
│                                                              │
│  🚀 SCALE: 2000+ khách/năm qua đại lý mà không tốn        │
│     marketing budget, đại lý tự lo local marketing           │
│                                                              │
│  ⏱️ BUILD TIME: ~4 tuần (portal + API + onboard)            │
│  💵 REVENUE IMPACT: +140% (từ $66K → $158K/năm)            │
└─────────────────────────────────────────────────────────────┘
```

---

