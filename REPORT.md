# Observathon — Báo cáo Day 13
**Team:** NguyenDucThanh | **MSSV:** 2A202600838

---

## Kết quả

| Phase   | Score     | Correct   |
|---------|-----------|-----------|
| Public  | **89.25** | 82 / 120  |
| Private | **72.79** | 32 / 80   |

---

## Những việc đã làm

### 1. Cấu hình để dùng Google Gemini
- Binary mặc định dùng OpenAI. Đổi `provider: "openai"` + set `OPENAI_API_KEY` và `OPENAI_BASE_URL` trỏ về endpoint OpenAI-compatible của Google Gemini.
- Model sử dụng: `gemini-2.5-flash`, `model_price_tier: "cheap"`.

### 2. Chạy binary qua WSL
- Windows binary lỗi DLL (Memory Integrity). Dùng file Linux ELF trong WSL.
- Practice sim: `bin/practice/observathon-sim-linux`
- Public sim: `bin/practice/public-observathon-sim`
- Private sim: `bin/private/observathon-sim`

### 3. Tối ưu config.json
| Tham số | Trước | Sau | Lý do |
|---------|-------|-----|-------|
| `temperature` | 1.6 | 0.2 | Giảm variance, tính toán chính xác hơn |
| `self_consistency` | 1 | 2 | Tăng độ đồng thuận, giảm drift |
| `max_completion_tokens` | 256 | 1024 | Fix truncation — nguyên nhân chính khiến correct thấp |
| `model_price_tier` | premium | cheap | Cải thiện cost score |
| `redact_pii` | false | true | Chặn PII leak |
| `retry.enabled` | false | true | Xử lý lỗi 503 Gemini overload |
| `cache.enabled` | true | false | Cache stale gây null answers |
| `session_drift_rate` | 0.06 | 0 | Loại bỏ drift nhân tạo |
| `tool_error_rate` | 0.18 | 0 | Loại bỏ lỗi tool nhân tạo |
| `tool_budget` | 0 | 4 | Giới hạn số lần gọi tool |

### 4. Viết solution/prompt.txt
- Luồng cố định: `check_stock → get_discount → calc_shipping` (mỗi tool tối đa 1 lần).
- Từ chối khi hết hàng / không giao được.
- Công thức tính toán rõ ràng: `discounted = subtotal × (100 − pct) // 100`.
- Thêm quy tắc: giá luôn là VND đầy đủ (ví dụ: 18000000, không phải 18000).
- Phòng thủ PII: bỏ qua email / số điện thoại hoàn toàn.
- Phòng thủ injection: ghi chú đơn hàng là dữ liệu, không phải lệnh.

### 5. Viết solution/wrapper.py
- Strip PII khỏi câu hỏi trước khi gọi agent.
- Retry 3 lần khi answer = null.
- Try/except bao toàn bộ call_next để tránh wrapper_error trong private sim.

### 6. Viết solution/findings.json
8 fault class được chẩn đoán:

| Fault Class | Diagnosis F1 |
|-------------|-------------|
| fabrication, arithmetic_error, pii_leak, tool_overuse | ✓ |
| quality_drift, error_spike, tool_failure, prompt_injection | ✓ |

**diag_f1: 0.842** (private) | **0.778** (public)

---

## Lỗi gặp phải và cách xử lý

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| Windows binary DLL error | Memory Integrity blocks PyInstaller | Dùng Linux binary trong WSL |
| API key không nhận | CRLF trong .env | `tr -d '\r'` khi export |
| Score correct thấp (45/120) | `max_completion_tokens: 256` cắt ngang đầu ra | Tăng lên 1024 → 82/120 |
| `wrapper_error` trong private | `self_consistency` override không được hỗ trợ | Bỏ override, dùng try/except |
| Giá sai magnitude (66037 thay vì 66037000) | Model hiểu nhầm đơn vị | Thêm hướng dẫn VND đầy đủ vào prompt |
