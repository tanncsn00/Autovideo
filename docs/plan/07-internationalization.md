## 7. Internationalization (i18n) - Bán Toàn Cầu

### 7.1 Hiện Trạng i18n Của Dự Án

Dự án **đã có sẵn** i18n cơ bản trong `/webui/i18n/` với 7 ngôn ngữ:

| Ngôn ngữ | File | Status |
|-----------|------|--------|
| English (en) | ✅ Đã có | Baseline |
| Chinese (zh) | ✅ Đã có | Thị trường lớn nhất |
| German (de) | ✅ Đã có | Châu Âu |
| Portuguese (pt) | ✅ Đã có | Brazil |
| Russian (ru) | ✅ Đã có | Đông Âu |
| Turkish (tr) | ✅ Đã có | Trung Đông |
| Vietnamese (vi) | ✅ Đã có | Thị trường nhà |

### 7.2 Ngôn Ngữ Cần Thêm (Theo Thứ Tự Ưu Tiên ROI)

| Ưu Tiên | Ngôn Ngữ | Lý Do | Thị Trường |
|----------|----------|-------|------------|
| 🔴 Cao | **Spanish (es)** | 500M+ speakers, Latin America + Spain | Mexico, Argentina, Colombia, Spain |
| 🔴 Cao | **Japanese (ja)** | ARPU cao nhất, 140M users video tools | Japan |
| 🔴 Cao | **Korean (ko)** | Creator economy mạnh, chi tiêu cao | South Korea |
| 🟡 Trung bình | **French (fr)** | Thị trường EU lớn | France, Canada (Quebec), Africa |
| 🟡 Trung bình | **Thai (th)** | SE Asia growth market | Thailand |
| 🟡 Trung bình | **Indonesian (id)** | 270M dân, creator economy đang bùng nổ | Indonesia |
| 🟢 Sau | **Arabic (ar)** | Thị trường lớn nhưng cần RTL layout | Middle East |
| 🟢 Sau | **Hindi (hi)** | 500M users nhưng price-sensitive | India |

> **Phase 1:** Thêm Spanish, Japanese, Korean → Cover 80% thị trường có sức mua cao
> **Phase 2:** Thêm French, Thai, Indonesian → Mở rộng reach
> **Phase 3:** Thêm Arabic, Hindi → Volume markets

### 7.3 Multi-Currency & PPP Pricing (Giá Theo Sức Mua)

**Purchasing Power Parity (PPP):** Giá khác nhau theo quốc gia, nhưng **chỉ áp dụng cho Monthly/Yearly** (subscription). Lifetime giữ giá cố định toàn cầu để không lỗ.

#### Bảng Giá PPP (Chỉ Cho Monthly/Yearly)

| Tier | Quốc Gia | Monthly | Yearly | Lifetime |
|------|----------|---------|--------|----------|
| **Tier 1 (Full)** | US, UK, EU, AU, CA, JP, KR | **$7.99/mo** | **$59.99/yr** | **$89** |
| **Tier 2 (75%)** | SG, HK, TW, CN | **$5.99/mo** | **$44.99/yr** | **$89** |
| **Tier 3 (50%)** | BR, MX, TR, TH, PL | **$3.99/mo** | **$29.99/yr** | **$89** |
| **Tier 4 (40%)** | VN, IN, ID, PH, EG, NG | **$2.99/mo** | **$24.99/yr** | **$89** |

> **Lifetime $89 giống nhau toàn cầu** - ai muốn dùng cả đời thì trả full price.
> **Monthly/Yearly có PPP** - user nghèo trả dần, bạn vẫn có recurring revenue.

```
Ví dụ thực tế:
  User ở Mỹ    → Monthly: $7.99/mo | Yearly: $59.99 | Lifetime: $89
  User ở Japan  → Monthly: ¥1,200/mo | Yearly: ¥9,000 | Lifetime: ¥13,350
  User ở Brazil → Monthly: R$20/mo | Yearly: R$150 | Lifetime: R$445
  User ở VN     → Monthly: 75,000₫/mo | Yearly: 625,000₫ | Lifetime: 2,225,000₫

→ Paddle tự detect quốc gia + chuyển đổi currency
→ Bạn set giá override cho từng quốc gia trên Paddle dashboard
```

**Kết quả thực tế của PPP:** Tăng revenue 15-30% vì unlock mua từ markets price-sensitive.

#### Cách Setup Trên Paddle

```
Paddle Dashboard → Products → Pro License → Prices
┌────────────────────────────────────────────────┐
│  Base price: $89 USD (Lifetime, giống toàn cầu)                            │
│                                                  │
│  Country overrides:                              │
│  ├── Brazil: $29 USD (auto-convert to BRL)      │
│  ├── India: $19 USD (auto-convert to INR)       │
│  ├── Vietnam: $19 USD (auto-convert to VND)     │
│  ├── Turkey: $29 USD (auto-convert to TRY)      │
│  ├── Mexico: $29 USD (auto-convert to MXN)      │
│  ├── Indonesia: $19 USD (auto-convert to IDR)   │
│  └── ... (set cho từng nước)                    │
│                                                  │
│  All other countries: $89 USD (auto-convert)    │
└────────────────────────────────────────────────┘
```

### 7.4 Local Payment Methods (Thanh Toán Địa Phương)

Paddle tự động hiện payment method phù hợp theo quốc gia user:

| Quốc Gia | Payment Methods | Paddle Support |
|-----------|----------------|----------------|
| **Toàn cầu** | Visa, Mastercard, PayPal, Apple Pay, Google Pay | ✅ |
| **China** | Alipay | ✅ (WeChat Pay chưa có) |
| **South Korea** | KakaoPay, NaverPay, Samsung Pay, Payco | ✅ |
| **Brazil** | PIX | ✅ (early access) |
| **Netherlands** | iDEAL | ✅ |
| **Poland** | BLIK | ✅ |
| **EU** | SEPA Direct Debit | ✅ |
| **India** | UPI | ✅ (early access) |

```
Ví dụ: User ở Korea mở checkout
┌────────────────────────────────────┐
│  MoneyPrinterTurbo Pro             │
│  ₩133,000 (≈$89)                  │
│                                     │
│  Thanh toán bằng:                  │
│  [💳 Card]                         │
│  [📱 KakaoPay]  ← tự hiện         │
│  [📱 NaverPay]  ← cho Korea       │
│  [📱 Samsung Pay]                  │
│  [ PayPal]                         │
│  [🍎 Apple Pay]                    │
└────────────────────────────────────┘

User ở Vietnam:
┌────────────────────────────────────┐
│  MoneyPrinterTurbo Pro             │
│  475,000₫ (≈$19 PPP)              │
│                                     │
│  [💳 Card]                         │
│  [ PayPal]                         │
│  [🍎 Apple Pay]                    │
└────────────────────────────────────┘
```

> **Bạn không cần làm gì** - Paddle tự detect quốc gia và hiện payment methods phù hợp.

### 7.5 Desktop App i18n (Technical)

#### Hiện tại (Streamlit): Giữ nguyên JSON approach

```
webui/i18n/
├── en.json    # English
├── zh.json    # Chinese
├── vi.json    # Vietnamese
├── ja.json    # Japanese (thêm mới)
├── es.json    # Spanish (thêm mới)
└── ko.json    # Korean (thêm mới)
```

#### Desktop App Mới (React + Tauri): react-i18next

```
src/
├── i18n/
│   ├── index.ts          # i18n config
│   └── locales/
│       ├── en.json
│       ├── zh.json
│       ├── ja.json
│       ├── es.json
│       ├── ko.json
│       └── vi.json
├── components/
│   └── LanguageSwitcher.tsx
```

```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)     // Auto-detect OS language
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    resources: { en, zh, ja, es, ko, vi, ... },
    interpolation: { escapeValue: false }
  });
```

```typescript
// Sử dụng trong component
function App() {
  const { t } = useTranslation();
  return <h1>{t('welcome_message')}</h1>;
  // English: "Create Videos with AI"
  // Japanese: "AIで動画を自動作成"
  // Vietnamese: "Tạo Video Tự Động Bằng AI"
}
```

#### Locale Detection (Tự Nhận Ngôn Ngữ)

```
Desktop App:
  1. Đọc OS language (locale.getdefaultlocale())
  2. Nếu có trong supported languages → dùng luôn
  3. Nếu không → fallback English
  4. User thay đổi → lưu vào config, ưu tiên cao nhất

Landing Page:
  1. Đọc Accept-Language header từ browser
  2. Suggest (KHÔNG auto-redirect): "🇯🇵 日本語版はこちら"
  3. User click language switcher → lưu cookie preference
```

### 7.6 Landing Page i18n

#### URL Structure (Subdirectory - Recommended)

```
moneyprinterturbo.com/           → English (default)
moneyprinterturbo.com/ja/        → Japanese
moneyprinterturbo.com/es/        → Spanish
moneyprinterturbo.com/ko/        → Korean
moneyprinterturbo.com/zh/        → Chinese
moneyprinterturbo.com/vi/        → Vietnamese
moneyprinterturbo.com/pt/        → Portuguese
```

#### SEO: hreflang Tags (Bắt Buộc)

```html
<!-- Trên MỌI trang -->
<link rel="alternate" hreflang="en" href="https://moneyprinterturbo.com/" />
<link rel="alternate" hreflang="ja" href="https://moneyprinterturbo.com/ja/" />
<link rel="alternate" hreflang="es" href="https://moneyprinterturbo.com/es/" />
<link rel="alternate" hreflang="ko" href="https://moneyprinterturbo.com/ko/" />
<link rel="alternate" hreflang="zh" href="https://moneyprinterturbo.com/zh/" />
<link rel="alternate" hreflang="vi" href="https://moneyprinterturbo.com/vi/" />
<link rel="alternate" hreflang="x-default" href="https://moneyprinterturbo.com/" />
```

> Google dùng hreflang để hiện đúng version cho đúng người. User Nhật search → thấy trang Japanese.

#### Dịch Landing Page

| Cách | Chi phí | Chất lượng | Speed |
|------|---------|------------|-------|
| **AI translate (Claude/GPT) + native review** | ~$50-100/ngôn ngữ | Tốt (nếu có native review) | Nhanh |
| **Weglot (auto-translate widget)** | $150+/tháng | Trung bình | Instant |
| **Professional translator** | $200-500/ngôn ngữ | Tốt nhất | Chậm |
| **Community contribution** | Free | Varies | Không kiểm soát |

> **Recommend:** AI translate + tìm 1 native speaker review cho mỗi ngôn ngữ (Fiverr ~$20-50/ngôn ngữ).

### 7.7 Top Target Markets (Chiến Lược Từng Thị Trường)

| Thị Trường | Quy Mô | Giá PPP | Ngôn Ngữ | Payment | Ưu Tiên |
|-----------|---------|---------|----------|---------|---------|
| **US/Canada** | 45% global spend | $89 LT / $7.99/mo | en | Card, PayPal | 🔴 Must |
| **China** | 380M video users | $29 | zh | Alipay | 🔴 Must |
| **Japan** | 140M users, ARPU cao | $89 LT / $7.99/mo | ja | Card, PayPal | 🔴 Must |
| **South Korea** | Creator economy mạnh | $89 LT / $7.99/mo | ko | KakaoPay, NaverPay | 🔴 Must |
| **Brazil** | 200M users, growth nhanh | $29 | pt | PIX, Card | 🟡 High |
| **EU (DE/FR/UK)** | Mature market | $89 LT / $7.99/mo | de/fr/en | Card, iDEAL, SEPA | 🟡 High |
| **SE Asia (VN/TH/ID)** | Growth market | $19 | vi/th/id | Card | 🟡 High |
| **India** | 500M users, price-sensitive | $19 | en/hi | UPI | 🟢 Later |
| **Latin America** | Creator economy bùng nổ | $29 | es | Card | 🟡 High |

### 7.8 Tổng Kết i18n Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    i18n STRATEGY                             │
│                                                              │
│  🌐 APP LANGUAGES                                           │
│     Phase 1 (Launch): en, zh, vi + ja, es, ko (thêm mới)   │
│     Phase 2: fr, th, id                                      │
│     Phase 3: ar, hi                                          │
│     Tổng: 13 ngôn ngữ                                       │
│                                                              │
│  💰 PRICING (PPP)                                           │
│     Tier 1 ($7.99/mo, $89 LT): US, EU, JP, KR, AU, CA     │
│     Tier 2 ($42): SG, HK, TW                               │
│     Tier 3 ($29): BR, MX, TR, TH, PL, CN                   │
│     Tier 4 ($19): VN, IN, ID, PH, EG, NG                   │
│     → Setup trên Paddle dashboard, auto-convert currency    │
│                                                              │
│  💳 PAYMENT                                                 │
│     Paddle tự hiện payment method theo quốc gia             │
│     Card + PayPal (toàn cầu)                                │
│     + Alipay (China) + KakaoPay (Korea) + PIX (Brazil)...  │
│     → Bạn không cần làm gì thêm                            │
│                                                              │
│  🌍 LANDING PAGE                                            │
│     Subdirectory: /ja/, /es/, /ko/, /zh/, /vi/              │
│     hreflang tags cho SEO                                    │
│     AI translate + native speaker review ($20-50/lang)       │
│                                                              │
│  📱 LOCALE DETECTION                                        │
│     App: OS language → saved preference → fallback en       │
│     Web: Accept-Language header → suggest, not force         │
└─────────────────────────────────────────────────────────────┘
```

---

