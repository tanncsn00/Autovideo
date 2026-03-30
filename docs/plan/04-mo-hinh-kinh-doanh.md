## 4. Mô Hình Kinh Doanh

### 4.1 Mô Hình: Open Core + Versioned Lifetime License + Cloud Add-on

#### Nguyên tắc cốt lõi

```
┌─────────────────────────────────────────────────────────────────┐
│  OPEN-SOURCE CORE (GitHub, MIT License)                        │
│  → Code pipeline cơ bản, CLI, API                               │
│  → Ai cũng clone về dùng FREE, hợp pháp                        │
│  → Mục đích: build community, trust, contributors               │
│                                                                  │
│  DESKTOP APP (Closed-source, bán license)                       │
│  → Repo riêng, KHÔNG public trên GitHub                         │
│  → Đóng gói bằng PyInstaller + PyArmor (encrypt/obfuscate)     │
│  → User phải mua license key để dùng                            │
│  → Đây là nguồn thu chính                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Tại sao open-source mà vẫn bán được?

| Câu hỏi | Trả lời |
|----------|---------|
| Code free trên GitHub, sao bán? | Desktop app là **closed-source riêng**, không có trên GitHub |
| User crack thì sao? | PyArmor + license server + hardware binding. 95% user không crack vì $89 rẻ hơn tốn công |
| Free user có giận không? | Không, core vẫn free. Developers dùng CLI/API thoải mái |
| Ai đã dùng mô hình này? | VS Code (free) + GitHub Copilot (paid), GitLab CE/EE, Grafana, Metabase, Supabase |

### 4.2 Pricing Tiers (CHỐT: 3 Options + Add-ons)

#### Bảng giá: Free + 3 Paid Options

```
┌─────────────────────────────────────────────────────────────┐
│                     PRICING MODEL                            │
│                                                              │
│  FREE (GitHub)        Dùng thử, có watermark                │
│  ──────────────────────────────────────────────────          │
│  MONTHLY  $7.99/mo    Trả dần, linh hoạt                    │
│  YEARLY   $59.99/yr   Tiết kiệm 37% vs monthly              │
│  LIFETIME $89         Trả 1 lần, dùng v1.x mãi mãi         │
│  ──────────────────────────────────────────────────          │
│  ADD-ONS (mua riêng, tùy chọn):                             │
│  Voice Cloning Pack     $29                                  │
│  Team Pack (5 seats)    $99                                  │
│  Cloud Rendering        $9.99/mo                             │
│  Analytics Pro          $19                                  │
│  Template Creator       $19                                  │
└─────────────────────────────────────────────────────────────┘
```

#### Chi tiết từng option

| | Free | Monthly $7.99 | Yearly $59.99 | Lifetime $89 |
|--|------|---------------|---------------|--------------|
| **Desktop app** | ❌ (CLI only) | ✅ | ✅ | ✅ |
| **API Providers** | 5 | All (20+) | All (20+) | All (20+) |
| **Templates** | 5 cơ bản | 50+ | 50+ | 50+ |
| **Effects/Transitions** | 3 basic | All (15+) | All (15+) | All (15+) |
| **Batch processing** | ❌ | 10 videos/lần | Unlimited | Unlimited |
| **Watermark** | Có | ❌ | ❌ | ❌ |
| **Auto-publish** | ❌ | ✅ | ✅ | ✅ |
| **Auto-update** | ❌ | ✅ | ✅ | ✅ (v1.x) |
| **Support** | Community | Email | Email | Email |

#### Add-ons (Mua Riêng, Tùy Chọn)

| Add-on | Giá | Mô tả |
|--------|-----|-------|
| **Voice Cloning Pack** | $29 one-time | Clone voice từ 30s audio, unlimited use |
| **Team Pack (5 seats)** | $99 one-time | 5 người dùng, admin dashboard, centralized billing |
| **Cloud Rendering** | $9.99/tháng | Render trên cloud, không cần GPU mạnh |
| **Analytics Pro** | $19 one-time | Dashboard, A/B testing, performance tracking |
| **Template Creator** | $19 one-time | Tự tạo + bán templates trên marketplace |

#### Tại sao 3 options hoạt động tốt

```
User nghèo / thử trước:
  → Monthly $7.99 (≈ 200k VND/tháng, bằng ly cà phê)
  → Dùng 1-2 tháng, thấy hay → chuyển Lifetime/Yearly

User biết giá trị, muốn tiết kiệm:
  → Yearly $59.99 (rẻ hơn 37% vs monthly, tiết kiệm $35.89/năm)
  → Lifetime $89 (hoàn vốn sau 1.5 năm yearly, ~11 tháng monthly)

Bạn win mọi trường hợp:
  → Monthly: recurring revenue, $95.88/năm/user
  → Yearly: $59.99/năm, user commit cả năm
  → Lifetime: $89 ngay, nhưng bán v2 upgrade sau ($53 upgrade, giảm 40%)
```

### 4.3 Revenue Projection: 1000 Khách (Cách 3)

#### Phân bổ thực tế 1000 khách

```
1000 khách chia ra (tỷ lệ industry average):
├── 200 người (20%) → Lifetime $89
├── 500 người (50%) → Monthly $7.99/mo
├── 200 người (20%) → Yearly $59.99/yr
└── 100 người (10%) → Mua add-ons
```

#### NĂM 1:

```
Lifetime:   200 × $89                        = $17,800
Monthly:    500 × $7.99 × 12 tháng           = $47,940
  (churn 5%/tháng: thực tế ~400 avg/tháng)   = $38,352
Yearly:     200 × $59.99                      = $11,998
Add-ons:    100 × $29 avg                     = $2,900
                                               ─────────
Doanh thu thô Năm 1:                          = $71,050

Trừ phí Paddle (5% + $0.50):                  = -$5,553
                                               ─────────
BẠN NHẬN NĂM 1:                                $65,497 ✅
```

#### NĂM 2 (khách cũ + 800 khách mới):

```
KHÁCH CŨ (recurring):
  Monthly: ~300 còn lại × $7.99 × 12          = $28,764
  Yearly:  170 renew × $59.99                  = $10,198
  v2 Upgrade: 120 lifetime users × $53         = $6,360
  Add-ons từ khách cũ:                         = $3,000
                                                ─────────
  Subtotal khách cũ:                            $48,322

KHÁCH MỚI (800 người):
  Lifetime: 160 × $89                          = $14,240
  Monthly:  400 × $7.99 × avg 8 tháng          = $25,568
  Yearly:   160 × $59.99                        = $9,598
  Add-ons:  80 × $29 avg                        = $2,320
                                                ─────────
  Subtotal khách mới:                           $51,726

TỔNG NĂM 2 (thô):                              $100,048
Trừ phí Paddle:                                 -$7,504
                                                ─────────
BẠN NHẬN NĂM 2:                                 $92,544 ✅
```

#### SO SÁNH: Chỉ Lifetime $89 vs 3 Options

| | Chỉ Lifetime $89 | 3 Options (Monthly+Yearly+Lifetime) |
|--|-------------------|-------------------------------------|
| **1000 khách, Năm 1** | $83,790 | **$65,497** |
| **Năm 2 (khách cũ)** | $0 💀 | **$48,322** |
| **Năm 2 (+ khách mới)** | $67,032 | **$92,544** |
| **Tổng 2 năm** | $150,822 | **$158,041** |
| **Năm 3+ chênh lệch** | Ngày càng thua | **Recurring compound tăng dần** |

> Năm 1: Lifetime-only tạm thời cao hơn (vì $89/khách vs phân bổ).
> Nhưng từ Năm 2 trở đi: 3 Options thắng vì recurring revenue từ Monthly/Yearly.
> Năm 3, 4, 5... gap ngày càng lớn.

### 4.4 Versioned Lifetime License (Cách Thu Phí Dài Hạn)

```
┌──────────────────────────────────────────────────────────────┐
│                    CÁCH HOẠT ĐỘNG                             │
│                                                               │
│  User mua $89 Lifetime → Nhận license cho v1.x               │
│                                                               │
│  v1.0 ──→ v1.1 ──→ v1.2 ──→ ... ──→ v1.9   FREE updates    │
│                                        │                      │
│                                        ▼                      │
│  v2.0 ra (sau ~12-18 tháng) ──→ $53 upgrade (giảm 40%)      │
│                                                               │
│  Không upgrade? v1.x VẪN CHẠY bình thường, mãi mãi          │
│  Chỉ là không có features mới của v2.0                       │
│                                                               │
│  Monthly/Yearly users: tự động được v2.0 (đang trả tiền)    │
└──────────────────────────────────────────────────────────────┘
```

#### Chi tiết version policy

| Hạng mục | Policy |
|----------|--------|
| **Minor updates (v1.0→v1.9)** | FREE, tự động qua auto-updater |
| **Major version (v1→v2)** | Paid upgrade, giảm 40% cho existing users |
| **Chu kỳ major version** | ~12-18 tháng |
| **Old version sau khi v2 ra** | Vẫn chạy bình thường, không bị khóa |
| **Bug fixes cho old version** | 6 tháng sau khi major version mới ra |
| **Ai đã dùng mô hình này** | Sketch, Sublime Text, JetBrains (Fallback License), Capture One |

### 4.4 License Enforcement (Cách Ràng Buộc Kỹ Thuật)

```
┌─ User mua trên LemonSqueezy ─────────────────────────────┐
│  1. Thanh toán ($7.99/mo hoặc $89 lifetime)                │
│  2. Nhận license key: MPT-XXXX-XXXX-XXXX                 │
│  3. Download desktop app (.exe / .dmg / .AppImage)        │
│  4. Mở app → nhập license key                             │
│  5. App gọi LemonSqueezy API verify key                   │
│  6. Server confirm → app unlock premium features          │
│  7. Offline grace period: 30 ngày (không cần online 24/7) │
└───────────────────────────────────────────────────────────┘
```

#### Anti-piracy layers

| Layer | Mô Tả |
|-------|--------|
| **PyArmor obfuscation** | Code Python encrypt, không đọc được plain text |
| **License server check** | Verify key online khi mở app (30-day offline grace) |
| **Hardware fingerprint** | 1 key = tối đa 3 máy tính |
| **Multi-point check** | License check ở nhiều điểm trong code, không phải 1 chỗ |
| **Tamper detection** | Detect nếu binary bị modify |

> **Thực tế:** Không tool nào chống crack 100%. Nhưng $89 vẫn đủ rẻ để 95% users chọn mua thay vì crack. Business users không dám dùng crack vì rủi ro pháp lý.

#### Payment platform

| Platform | Phí | Tại sao chọn |
|----------|-----|---------------|
| **LemonSqueezy** (recommend) | 5% + $0.50 | License key API built-in, tự handle VAT/tax toàn cầu, webhook |
| Paddle | 5% + $0.50 | Merchant of record, handle tax |
| Gumroad | 10% | Đơn giản nhưng phí cao hơn |

### 4.5 Revenue Streams

| # | Nguồn Thu | Loại | Dự Kiến % Revenue |
|---|-----------|------|-------------------|
| 1 | **License sales (Pro/Business)** | One-time | 50% |
| 2 | **Major version upgrades** | One-time (recurring ~18 tháng) | 15% |
| 3 | **Cloud add-on** | Monthly subscription | 15% |
| 4 | **Template marketplace** | 30% commission | 8% |
| 5 | **Plugin marketplace** | 30% commission | 5% |
| 6 | **Enterprise contracts** | Custom annual | 5% |
| 7 | **Affiliate (ElevenLabs, Storyblocks...)** | Commission | 2% |

### 4.6 Dự Kiến Revenue (Năm 1)

| Metric | Conservative (1,000 khách) | Optimistic (5,000 khách) |
|--------|---------------------------|--------------------------|
| Lifetime ($89) | 200 × $89 = $17,800 | 1,000 × $89 = $89,000 |
| Monthly ($7.99) | 500 × $7.99 × ~9.6mo avg = $38,352 | 2,500 × $7.99 × ~9.6mo avg = $191,760 |
| Yearly ($59.99) | 200 × $59.99 = $11,998 | 1,000 × $59.99 = $59,990 |
| Add-ons | 100 × $29 avg = $2,900 | 500 × $29 avg = $14,500 |
| **Doanh thu thô** | **$71,050** | **$355,250** |
| Trừ phí Paddle (~7%) | -$4,974 | -$24,868 |
| **Bạn nhận Year 1** | **$66,076** | **$330,382** |

### 4.7 So Sánh Giá Với Đối Thủ

| Tool | Giá Năm 1 | Giá Năm 2 | MPT Pro (Năm 1) | MPT Pro (Năm 2) |
|------|-----------|-----------|------------------|------------------|
| InVideo AI | $240 | $480 | **$89** | **$89** (đã mua) |
| Pictory | $276 | $552 | **$89** | **$89** |
| HeyGen | $348 | $696 | **$89** | **$89** |
| Synthesia | $264 | $528 | **$89** | **$89** |
| Opus Clip | $228 | $456 | **$89** | **$89** |

> **Selling point chính:** "Trả $89 một lần. Đối thủ tính $240-348/năm. Sau 2 năm bạn tiết kiệm $390-610."

### 4.8 Tổng Kết Mô Hình

```
┌─────────────────────────────────────────────────────────────┐
│                   MÔ HÌNH THU PHÍ CHỐT                      │
│                                                              │
│  1. OPEN CORE                                                │
│     Core pipeline → FREE trên GitHub (MIT)                   │
│     Desktop app   → PAID, closed-source                      │
│                                                              │
│  2. VERSIONED LIFETIME LICENSE                               │
│     $89 Lifetime = dùng v1.x trọn đời                        │
│     v2.0 ra → upgrade $29/$89 (optional, giảm 40%)          │
│     Không upgrade → v1.x vẫn chạy mãi                       │
│                                                              │
│  3. CLOUD ADD-ON (optional)                                  │
│     $9.99/tháng cho cloud rendering + sync                   │
│     Không bắt buộc, app chạy 100% local được                │
│                                                              │
│  4. MARKETPLACE COMMISSION                                   │
│     Templates + plugins: lấy 30% từ creators                │
│                                                              │
│  5. ENFORCEMENT                                              │
│     LemonSqueezy license key + PyArmor + hardware binding   │
│     95% users sẽ mua vì $7.99-$89 rẻ + legal safety         │
└─────────────────────────────────────────────────────────────┘
```

---

