# ZaloPay Merchant Support Chatbot

Hệ thống chatbot hỗ trợ tự động cho đối tác (merchant) của ZaloPay, xây dựng bằng Python (Flask). Chatbot tiếp nhận câu hỏi nghiệp vụ và định tuyến qua một trong ba luồng xử lý tùy theo nội dung yêu cầu.

## Kiến trúc luồng xử lý

```
Tin nhắn đến
     │
     ▼
[Phát hiện từ khóa nhạy cảm?] ──YES──► Flow A: Escalate → nhân viên liên hệ lại
     │ NO
     ▼
[Khớp knowledge base?] ──YES──► Flow B: Tự động trả lời từ dữ liệu nghiệp vụ
     │ NO
     ▼
Flow C: Từ chối lịch sự, hướng dẫn gửi email bộ phận chuyên trách
```

### Flow A — Escalate sang nhân viên
Kích hoạt khi phát hiện từ khóa nhạy cảm như: tranh chấp pháp lý, kiện tụng, gian lận, lừa đảo, tâm lý tiêu cực cao (doạ chấm dứt hợp đồng, lên mạng xã hội). Hệ thống thông báo sẽ có nhân viên liên hệ lại trong 2 giờ làm việc.

### Flow B — Tự động trả lời
Knowledge base bao gồm 5 nhóm nghiệp vụ:

| # | Nhóm | Nội dung |
|---|------|----------|
| 1 | **Onboarding & Sandbox** | Quy trình đăng ký, tích hợp, kiểm tra kỹ thuật, go-live theo Quy định 2345 |
| 2 | **Lỗi dòng tiền** | Số dư bằng 0, lệnh chi thất bại, cập nhật tài khoản thụ hưởng |
| 3 | **Tra soát & hoàn tiền** | Chargeback đơn lẻ, bulk refund cho đối tác (ví dụ: Beta Cinemas) |
| 4 | **Kiểm soát rủi ro** | Khóa ví, khoanh giữ số dư 48h, phối hợp Vietcombank/BIDV/MSB/Techcombank |
| 5 | **Đối soát phí** | Đối soát MDR định kỳ, sai lệch trạng thái giao dịch, hóa đơn VAT |

### Flow C — Ngoài phạm vi
Câu hỏi không thuộc 5 nhóm trên được từ chối lịch sự kèm hướng dẫn liên hệ bộ phận chuyên trách.

## Cài đặt và chạy

### Yêu cầu
- Python 3.10+

### Cài đặt

```bash
pip install -r requirements.txt
```

### Chạy

```bash
python agent.py
```

Truy cập giao diện web tại: `http://localhost:5000`

### Chạy production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 agent:app
```

## Cấu trúc project

```
zalopay-ops-agent/
├── agent.py              # Flask app, định tuyến 3 luồng xử lý
├── knowledge_base.py     # Dữ liệu nghiệp vụ + classifier functions
├── requirements.txt      # Dependencies
├── README.md
└── templates/
    └── index.html        # Giao diện web chat
```

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/` | Giao diện web |
| POST | `/api/session` | Tạo session chat mới |
| POST | `/api/chat` | Gửi tin nhắn, nhận phản hồi |
| GET | `/api/history/<session_id>` | Lấy lịch sử hội thoại |
| GET | `/api/health` | Health check |

### POST /api/chat

Request:
```json
{
  "session_id": "uuid",
  "message": "Câu hỏi của merchant"
}
```

Response:
```json
{
  "session_id": "uuid",
  "flow": "auto_answer | out_of_scope | escalated",
  "response": "Nội dung phản hồi",
  "domain": "onboarding_sandbox | cashflow_errors | dispute_refund | risk_control | reconciliation_fee | null",
  "timestamp": "2026-06-14T10:00:00Z",
  "escalated": false
}
```

## Phong cách phản hồi

Toàn bộ phản hồi được soạn theo văn phong hành chính, học thuật, chuyên nghiệp — không dùng bullet points, sử dụng cách đánh số thứ tự và bố cục đoạn văn rõ ràng, phù hợp với môi trường giao tiếp doanh nghiệp B2B.
