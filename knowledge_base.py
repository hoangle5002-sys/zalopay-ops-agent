"""
ZaloPay Merchant Support Knowledge Base — v2
=============================================
Kiến trúc mới: Sub-intent per domain
- Mỗi domain chia thành nhiều sub-intent cụ thể
- Response ngắn gọn, đúng trọng tâm câu hỏi
- Không trả template dài khi merchant chỉ hỏi 1 việc cụ thể
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import re
import unicodedata


def _normalize(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


# ─────────────────────────────────────────────────────────────────────────────
# Core data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SubIntent:
    """Một câu hỏi cụ thể trong domain, với response riêng"""
    intent_id: str
    trigger_keywords: List[str]           # keyword đặc trưng của intent này
    trigger_patterns: List[str]           # regex pattern để match câu hỏi
    response: str                         # câu trả lời đúng trọng tâm
    follow_up: Optional[str] = None       # câu hỏi gợi mở tiếp theo nếu cần


@dataclass
class DomainEntry:
    domain: str
    domain_keywords: List[str]            # keyword chung để nhận diện domain
    sub_intents: List[SubIntent]          # danh sách intent con


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 1 — Onboarding & Sandbox (Quy định 2345)
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_ONBOARDING = DomainEntry(
    domain="onboarding_sandbox",
    domain_keywords=[
        "onboarding", "onboard", "đăng ký", "tích hợp", "sandbox", "thử nghiệm",
        "quy định 2345", "qd2345", "môi trường test", "app_id", "api key",
        "merchant id", "hợp đồng", "kích hoạt", "phê duyệt", "kyc",
        "xác minh danh tính", "giấy phép kinh doanh", "tài khoản merchant",
        "production", "go live", "chuyển production", "đại diện pháp lý",
        "hồ sơ đăng ký", "xét duyệt", "merchant mới", "trở thành merchant",
    ],
    sub_intents=[

        SubIntent(
            intent_id="onboarding.ho_so_phap_ly",
            trigger_keywords=["hồ sơ", "giấy tờ", "tài liệu", "nộp", "chuẩn bị", "cần gì", "kyc", "xác minh"],
            trigger_patterns=[
                r"(hồ sơ|giấy tờ|tài liệu).*(cần|yêu cầu|nộp|chuẩn bị)",
                r"(đăng ký|onboarding).*(cần|yêu cầu).*(gì|những gì|tài liệu|giấy tờ)",
                r"(kyc|xác minh).*(cần|gồm|bao gồm|yêu cầu)",
                r"(điều kiện|yêu cầu).*(trở thành|làm).*(merchant|đối tác)",
            ],
            response="""Để đăng ký làm Merchant ZaloPay, Quý đối tác cần chuẩn bị các tài liệu KYC sau:

**Đối với doanh nghiệp:**
- Giấy chứng nhận đăng ký kinh doanh còn hiệu lực (bản sao công chứng)
- CMND/CCCD của người đại diện pháp lý (2 mặt)
- Giấy ủy quyền (nếu người làm thủ tục không phải đại diện pháp lý)
- Mô tả mô hình kinh doanh và lĩnh vực hoạt động

**Đối với cá nhân kinh doanh:**
- CMND/CCCD còn hiệu lực
- Giấy phép kinh doanh hộ cá thể (nếu có)

Bộ phận Compliance sẽ xác minh trong **03 ngày làm việc** sau khi nhận đủ hồ sơ.

Nộp hồ sơ qua: merchant-support@zalopay.vn hoặc Merchant Portal tại merchant.zalopay.vn/onboarding""",
            follow_up="Quý đối tác cần hỗ trợ thêm về cách nộp hồ sơ hay theo dõi tiến độ xét duyệt không?"
        ),

        SubIntent(
            intent_id="onboarding.sandbox_credentials",
            trigger_keywords=["app_id", "api key", "secret key", "lấy key", "cấp key", "credential", "thông tin sandbox"],
            trigger_patterns=[
                r"(app_id|api.?key|secret.?key).*(lấy|nhận|cấp|ở đâu|như thế nào)",
                r"(sandbox|môi trường test).*(thông tin|credential|key|app.?id)",
                r"(cấp|nhận|lấy).*(app_id|api.?key|thông tin tích hợp)",
                r"(tích hợp|kết nối).*(sandbox|test).*(bắt đầu|bước đầu|như thế nào)",
            ],
            response="""Sau khi hồ sơ KYC được phê duyệt, hệ thống sẽ **tự động gửi thông tin Sandbox** qua email đã đăng ký trong vòng 24 giờ, gồm:

- **App ID** — định danh ứng dụng của Quý đối tác
- **API Key** — dùng để xác thực API call
- **Secret Key** — dùng để ký (sign) các request

⚠️ **Lưu ý bảo mật:**
- Không chia sẻ Secret Key cho bất kỳ ai, kể cả nhân viên ZaloPay
- Thông tin Sandbox và Production là **hoàn toàn riêng biệt**, không dùng lẫn
- Nếu nghi ngờ bị lộ key, báo ngay: security@zalopay.vn

Chưa nhận được email sau 24 giờ? Kiểm tra thư mục Spam hoặc liên hệ merchant-support@zalopay.vn để được cấp lại.""",
            follow_up=None
        ),

        SubIntent(
            intent_id="onboarding.sandbox_duration",
            trigger_keywords=["thời gian", "bao lâu", "thời hạn", "sandbox hết hạn", "30 ngày", "gia hạn sandbox"],
            trigger_patterns=[
                r"(sandbox|môi trường test).*(thời hạn|hết hạn|bao lâu|bao nhiêu ngày|gia hạn)",
                r"(thời gian|hạn).*(tích hợp|test|thử nghiệm|hoàn thiện)",
                r"(có bao nhiêu|được bao nhiêu).*(ngày|thời gian).*(sandbox|test)",
            ],
            response="""Môi trường Sandbox có thời hạn **30 ngày** kể từ ngày được cấp thông tin.

Nếu chưa hoàn thiện tích hợp trong 30 ngày, Quý đối tác có thể **yêu cầu gia hạn thêm 15 ngày** (tối đa 1 lần) bằng cách gửi email đến merchant-support@zalopay.vn với tiêu đề: `[Sandbox Extension] Tên Merchant - App ID`.

Trong thời gian Sandbox, Quý đối tác cần hoàn thiện:
1. Luồng tạo đơn hàng và thanh toán
2. Xử lý callback từ ZaloPay
3. Luồng tra cứu trạng thái giao dịch (Query Order)
4. Luồng hoàn tiền (Refund) nếu có sử dụng""",
            follow_up=None
        ),

        SubIntent(
            intent_id="onboarding.go_live",
            trigger_keywords=["production", "go live", "chuyển production", "môi trường thật", "triển khai thật", "lên production"],
            trigger_patterns=[
                r"(chuyển|nâng lên|go.?live|deploy).*(production|môi trường thật|thật)",
                r"(production).*(khi nào|điều kiện|yêu cầu|được chưa|thủ tục)",
                r"(hoàn thiện sandbox|test xong).*(bước tiếp theo|làm gì|production)",
            ],
            response="""Để chuyển lên môi trường **Production**, Quý đối tác cần đáp ứng đủ 3 điều kiện:

**1. Vượt qua Technical Review** (05 ngày làm việc)
Bộ phận Kỹ thuật ZaloPay sẽ kiểm tra toàn bộ luồng tích hợp Sandbox. Yêu cầu test case bao gồm: thanh toán thành công, thanh toán thất bại, callback handling, query order, và refund.

**2. Ký kết Hợp đồng hợp tác chính thức**
Hợp đồng được gửi qua email sau khi Technical Review thông qua. Thời gian ký kết và xử lý pháp lý: 03–05 ngày làm việc.

**3. Nhận thông tin Production**
Sau khi hợp đồng có hiệu lực, App ID và Key Production sẽ được cấp riêng biệt qua email.

Gửi yêu cầu Technical Review: partner-integration@zalopay.vn với tiêu đề `[Go-Live Request] Tên Merchant - App ID Sandbox`""",
            follow_up="Quý đối tác đã hoàn thiện tích hợp Sandbox chưa? Cần hỗ trợ chuẩn bị test case không?"
        ),

        SubIntent(
            intent_id="onboarding.tien_do_xet_duyet",
            trigger_keywords=["tiến độ", "tình trạng", "trạng thái hồ sơ", "xét duyệt đến đâu", "chờ bao lâu", "hồ sơ đến đâu rồi"],
            trigger_patterns=[
                r"(tiến độ|tình trạng|trạng thái).*(hồ sơ|đăng ký|xét duyệt|onboarding)",
                r"(nộp hồ sơ|đăng ký).*(bao lâu|khi nào|mấy ngày).*(xong|xét duyệt|có kết quả)",
                r"(hồ sơ).*(đến đâu|xử lý chưa|duyệt chưa|kết quả chưa)",
                r"(chờ|đợi).*(xét duyệt|kyc|hồ sơ).*(lâu|mấy ngày)",
            ],
            response="""Thời gian xét duyệt KYC tiêu chuẩn là **03 ngày làm việc** kể từ khi nhận đủ hồ sơ hợp lệ.

Để tra cứu tiến độ hồ sơ, Quý đối tác có thể:

1. **Tra cứu tự động**: Đăng nhập Merchant Portal → Mục "Trạng thái hồ sơ"
2. **Liên hệ trực tiếp**: merchant-support@zalopay.vn, ghi rõ tên doanh nghiệp và mã số thuế trong email

Lý do phổ biến khiến hồ sơ bị trì hoãn:
- Giấy tờ chưa đủ hoặc hết hạn
- Thông tin đăng ký không khớp với giấy phép kinh doanh
- Lĩnh vực kinh doanh cần thẩm định bổ sung

Nếu đã quá 05 ngày làm việc mà chưa có phản hồi, vui lòng báo ngay để được ưu tiên xử lý.""",
            follow_up=None
        ),

        SubIntent(
            intent_id="onboarding.thay_doi_thong_tin",
            trigger_keywords=["cập nhật thông tin", "thay đổi thông tin", "đổi đại diện", "đổi địa chỉ", "thay đổi sau khi", "cập nhật hồ sơ"],
            trigger_patterns=[
                r"(thay đổi|cập nhật|chỉnh sửa).*(thông tin|hồ sơ|đăng ký).*(merchant|doanh nghiệp|đối tác)",
                r"(đổi|thay).*(đại diện pháp lý|giám đốc|chủ sở hữu|địa chỉ|ngành nghề)",
                r"(sau khi onboard|đã merchant rồi).*(muốn đổi|muốn thay|thay đổi)",
            ],
            response="""Theo **Quy định 2345**, mọi thay đổi thông tin sau khi onboarding thành công đều yêu cầu cập nhật hồ sơ và phê duyệt lại.

**Các thay đổi phổ biến và tài liệu cần thiết:**

| Loại thay đổi | Tài liệu cần nộp |
|---|---|
| Đổi người đại diện pháp lý | Quyết định bổ nhiệm + CMND/CCCD người mới |
| Thay đổi ngành nghề kinh doanh | Giấy phép kinh doanh cập nhật + mô tả nghiệp vụ mới |
| Đổi tên doanh nghiệp | Giấy chứng nhận đăng ký kinh doanh mới |
| Thay đổi địa chỉ | Giấy phép kinh doanh cập nhật |

Thời gian xử lý: **03–05 ngày làm việc** tùy mức độ thay đổi.
Trong thời gian xem xét, tài khoản Merchant vẫn hoạt động bình thường.

Gửi hồ sơ thay đổi: merchant-support@zalopay.vn — tiêu đề: `[Cập nhật hồ sơ] Tên Merchant - Mã Merchant`""",
            follow_up=None
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 2 — Lỗi dòng tiền & tài khoản thụ hưởng
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_CASHFLOW = DomainEntry(
    domain="cashflow_errors",
    domain_keywords=[
        "số dư", "dòng tiền", "tài khoản thụ hưởng", "cập nhật tài khoản",
        "thanh toán thất bại", "lệnh chi thất bại", "settlement", "quyết toán",
        "chuyển tiền thất bại", "disbursement", "nạp tiền", "balance",
        "insufficient", "không đủ số dư", "tài khoản nhận tiền", "bank account",
        "ngân hàng nhận", "tài khoản nhận", "đổi tài khoản", "tài khoản chi",
    ],
    sub_intents=[

        SubIntent(
            intent_id="cashflow.so_du_bang_0",
            trigger_keywords=["số dư bằng 0", "số dư âm", "không đủ số dư", "số dư không đủ", "hết tiền ví"],
            trigger_patterns=[
                r"(số dư|balance).*(bằng 0|về 0|âm|không đủ|thiếu|hết)",
                r"(ví merchant|tài khoản merchant).*(không đủ|hết|bằng 0|thiếu tiền)",
                r"(lệnh chi|settlement|quyết toán).*(thất bại|không thực hiện|bị giữ).*(số dư)",
            ],
            response="""Khi số dư ví Merchant về 0, các lệnh chi sẽ bị **giữ trong hàng đợi** và chờ xử lý lại sau khi có số dư.

**Cách xử lý nhanh nhất:**

1. **Nạp bổ sung số dư** — Thực hiện qua Merchant Portal → "Nạp tiền vào ví"
   - Sau khi nạp, hệ thống tự xử lý lại lệnh tồn trong **vòng 15 phút**

2. **Yêu cầu tạm ứng khẩn cấp** *(chỉ áp dụng với đối tác đủ điều kiện)*
   - Gửi email: finance-ops@zalopay.vn
   - Tiêu đề: `[KHẨN] Tạm ứng - [Tên Merchant] - [Mã Merchant]`
   - Điều kiện: đối tác có lịch sử giao dịch tốt, volume tháng > ngưỡng quy định

3. **Kiểm tra danh sách lệnh chi tồn đọng** qua Merchant Portal → "Lịch sử Settlement"

Quý đối tác có thể cho biết số lệnh chi đang bị giữ và tổng giá trị để được hỗ trợ ưu tiên không?""",
            follow_up=None
        ),

        SubIntent(
            intent_id="cashflow.cap_nhat_tai_khoan_thu_huong",
            trigger_keywords=[
                "đổi tài khoản", "cập nhật tài khoản thụ hưởng", "thay đổi ngân hàng",
                "tài khoản nhận tiền mới", "đổi ngân hàng nhận", "tài khoản thụ hưởng",
                "tài khoản nhận", "ngân hàng nhận", "bank account",
            ],
            trigger_patterns=[
                r"(cập nhật|thay đổi|đổi|thêm).*(tài khoản thụ hưởng|tài khoản nhận|ngân hàng nhận)",
                r"(tài khoản nhận tiền|tài khoản thụ hưởng|bank account).*(mới|đổi|thay|cập nhật)",
                r"(muốn|cần|yêu cầu).*(đổi|thay|cập nhật).*(ngân hàng|tài khoản).*(nhận|settlement|thụ hưởng)",
                r"(đổi|thay).*(tài khoản|ngân hàng).*(nhận tiền|nhận|thụ hưởng)",
            ],
            response="""Để cập nhật tài khoản thụ hưởng, Quý đối tác cần gửi hồ sơ qua **email chính thức của doanh nghiệp** (yêu cầu bắt buộc — không xử lý qua điện thoại hoặc chat).

**Hồ sơ cần chuẩn bị:**
1. Công văn yêu cầu thay đổi — có chữ ký và dấu doanh nghiệp
2. Bản sao sổ/thẻ tài khoản ngân hàng mới hoặc giấy xác nhận mở tài khoản
3. CMND/CCCD của người đại diện pháp lý

**Gửi về:** finance-ops@zalopay.vn
**Tiêu đề:** `[Cập nhật TK thụ hưởng] Tên Merchant - Mã Merchant`

**Thời gian xử lý:** 02 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ.

⚠️ Trong thời gian chờ cập nhật, các lệnh settlement vẫn chạy về **tài khoản cũ** — vui lòng không đóng tài khoản cũ trước khi có xác nhận cập nhật thành công.""",
            follow_up=None
        ),

        SubIntent(
            intent_id="cashflow.settlement_that_bai",
            trigger_keywords=["settlement thất bại", "quyết toán thất bại", "lệnh chi lỗi", "tiền không về", "disbursement lỗi", "chuyển tiền không thành công"],
            trigger_patterns=[
                r"(settlement|quyết toán|lệnh chi|disbursement).*(thất bại|lỗi|fail|không thực hiện|bị trả về)",
                r"(tiền|số tiền).*(không về|chưa về|mất|biến mất).*(tài khoản|ví|ngân hàng)",
                r"(chuyển tiền|thanh toán).*(thất bại|không thành công|lỗi).*(merchant|đối tác)",
            ],
            response="""Để tra cứu lệnh chi thất bại, Quý đối tác cung cấp các thông tin sau:

- **Transaction ID / Settlement Batch ID** (mã lô quyết toán)
- **Thời điểm phát sinh** (ngày giờ)
- **Số tiền** và **tài khoản thụ hưởng đích**
- **Mã lỗi** hiển thị (nếu có)

**Nguyên nhân phổ biến:**
| Lỗi | Nguyên nhân | Xử lý |
|---|---|---|
| Số dư không đủ | Ví Merchant về 0 | Nạp thêm → hệ thống tự retry |
| Thông tin TK sai | Tài khoản thụ hưởng không hợp lệ | Cập nhật thông tin TK |
| Ngân hàng đối tác bảo trì | Timeout từ phía ngân hàng | Chờ 30 phút → retry tự động |
| Tài khoản bị hạn chế | Risk control | Liên hệ risk-management@zalopay.vn |

Gửi yêu cầu tra cứu: finance-ops@zalopay.vn — tiêu đề: `[Tra cứu Settlement] Mã lô - Tên Merchant`
**Cam kết phản hồi trong 04 giờ làm việc.**""",
            follow_up="Quý đối tác có thể cung cấp Transaction ID hoặc Settlement Batch ID để mình kiểm tra chính xác hơn không?"
        ),

        SubIntent(
            intent_id="cashflow.nap_so_du",
            trigger_keywords=["nạp tiền", "nạp số dư", "bổ sung số dư", "cách nạp", "nạp ví merchant", "top up"],
            trigger_patterns=[
                r"(nạp|bổ sung|top.?up).*(tiền|số dư|ví).*(merchant|đối tác|như thế nào|bằng cách nào)",
                r"(cách|hướng dẫn|quy trình).*(nạp tiền|nạp số dư).*(ví merchant)",
                r"(muốn|cần|có thể).*(nạp|bổ sung).*(số dư|tiền vào ví)",
            ],
            response="""Có **3 cách** nạp tiền vào ví Merchant ZaloPay:

**Cách 1 — Qua Merchant Portal** *(nhanh nhất)*
Đăng nhập merchant.zalopay.vn → "Quản lý số dư" → "Nạp tiền"
→ Quét mã QR hoặc chuyển khoản ngân hàng theo thông tin hiển thị
→ Số dư cập nhật trong **vòng 15 phút** (giờ hành chính)

**Cách 2 — Chuyển khoản ngân hàng trực tiếp**
- STK: được cấp riêng cho từng Merchant (xem tại Merchant Portal)
- Nội dung chuyển khoản: `NAP [Mã Merchant] [Số tiền]`
- Thời gian ghi nhận: 15–30 phút trong giờ hành chính, có thể chậm hơn ngoài giờ

**Cách 3 — Đề nghị Kế toán ZaloPay hỗ trợ nạp hộ** *(cho số tiền lớn)*
Liên hệ: finance-ops@zalopay.vn với thông tin chuyển khoản

Hạn mức nạp tiền: không giới hạn. Số dư tối đa ví Merchant: theo thỏa thuận hợp đồng.""",
            follow_up=None
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 3 — Tra soát & hoàn tiền
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_DISPUTE = DomainEntry(
    domain="dispute_refund",
    domain_keywords=[
        "tra soát", "chargeback", "hoàn tiền", "refund", "khiếu nại giao dịch",
        "hoàn tiền hàng loạt", "bulk refund", "beta cinemas", "rạp chiếu phim",
        "refund policy", "giao dịch lỗi hoàn tiền", "người dùng khiếu nại",
        "dispute", "hoàn hàng", "hủy đơn hàng", "hủy vé", "batch refund",
    ],
    sub_intents=[

        SubIntent(
            intent_id="dispute.quy_trinh_tra_soat_don_le",
            trigger_keywords=["tra soát", "chargeback", "khiếu nại", "1 giao dịch", "một giao dịch", "giao dịch cụ thể"],
            trigger_patterns=[
                r"(tra soát|chargeback).*(giao dịch|thanh toán|cụ thể|đơn lẻ)",
                r"(khiếu nại|dispute).*(1|một|giao dịch).*(cụ thể|riêng lẻ)",
                r"(quy trình|thủ tục|làm thế nào).*(tra soát|chargeback)",
                r"khách hàng.*(khiếu nại|phàn nàn|yêu cầu hoàn).*(1|một|giao dịch)",
            ],
            response="""**Quy trình tra soát giao dịch đơn lẻ:**

**Thông tin cần cung cấp:**
- Mã giao dịch ZaloPay (`zptransid`) — bắt buộc
- Thời điểm giao dịch (ngày, giờ)
- Số tiền giao dịch
- Lý do tra soát (lỗi kỹ thuật / không nhận được dịch vụ / bị trừ 2 lần / ...)
- Bằng chứng: ảnh chụp màn hình, log hệ thống (nếu có)

**Thời hạn nộp tra soát:** Tối đa **45 ngày** kể từ ngày phát sinh giao dịch.

**Thời gian xử lý:** 03 ngày làm việc kể từ khi nhận đủ thông tin.

**Gửi yêu cầu:** dispute-team@zalopay.vn
Tiêu đề: `[Tra soát] zptransid - Tên Merchant`

**Kết quả tra soát** sẽ được thông báo qua email và cập nhật trên Merchant Portal → mục "Lịch sử tra soát".""",
            follow_up="Quý đối tác có thể cung cấp mã zptransid của giao dịch cần tra soát để được hỗ trợ nhanh hơn không?"
        ),

        SubIntent(
            intent_id="dispute.hoan_tien_hang_loat",
            trigger_keywords=["hoàn tiền hàng loạt", "bulk refund", "batch refund", "nhiều giao dịch", "hàng loạt", "sự cố kỹ thuật"],
            trigger_patterns=[
                r"(hoàn tiền|refund).*(hàng loạt|bulk|batch|nhiều|tất cả)",
                r"(sự cố|lỗi kỹ thuật).*(ảnh hưởng|nhiều).*(giao dịch|khách hàng)",
                r"(beta cinema|rạp phim|vé phim).*(hoàn|refund|lỗi|sự cố)",
                r"(hàng loạt|bulk|batch).*(refund|hoàn tiền|hoàn)",
            ],
            response="""**Quy trình Bulk Refund (Hoàn tiền hàng loạt):**

Áp dụng khi sự cố kỹ thuật từ phía Merchant ảnh hưởng nhiều giao dịch cùng lúc.

**Bước 1 — Chuẩn bị hồ sơ:**
- File danh sách giao dịch theo **template chuẩn ZaloPay** (tải tại Merchant Portal → Templates)
- Định dạng: `.xlsx`, tối đa **10,000 dòng/file**
- Công văn xác nhận sự cố có chữ ký và dấu doanh nghiệp

**Bước 2 — Nộp hồ sơ:**
Gửi về: dispute-team@zalopay.vn
Tiêu đề: `[Bulk Refund] Tên Merchant - Số lượng GD - Tổng giá trị`

**Bước 3 — Xử lý:**
- Xác minh từng giao dịch: **05 ngày làm việc**
- Sau phê duyệt, hoàn tiền trong:
  - **24 giờ** → ví ZaloPay
  - **05–07 ngày làm việc** → thẻ/tài khoản ngân hàng

⚠️ **Lưu ý:** Nếu tổng giá trị hoàn > **500 triệu đồng**, cần phê duyệt thêm từ Giám đốc Vận hành → thêm 02 ngày làm việc.""",
            follow_up="Quý đối tác có thể cho biết số lượng giao dịch và tổng giá trị cần hoàn để mình đánh giá timeline xử lý không?"
        ),

        SubIntent(
            intent_id="dispute.chinh_sach_hoan_tien",
            trigger_keywords=["chính sách hoàn tiền", "refund policy", "điều kiện hoàn", "hoàn được không", "có hoàn không"],
            trigger_patterns=[
                r"(chính sách|điều kiện|quy định).*(hoàn tiền|refund)",
                r"(có thể|được|không được).*(hoàn tiền|refund).*(trường hợp|khi nào|loại)",
                r"(hoàn tiền|refund).*(áp dụng|điều kiện|khi nào|loại nào)",
                r"giao dịch.*(loại nào|nào thì).*(được hoàn|có thể hoàn|refund được)",
            ],
            response="""**Chính sách hoàn tiền ZaloPay đối với Merchant:**

**Các trường hợp được hoàn tiền:**
✅ Lỗi kỹ thuật từ phía ZaloPay (giao dịch bị trừ tiền nhưng không ghi nhận)
✅ Lỗi kỹ thuật từ phía Merchant dẫn đến không cung cấp được dịch vụ
✅ Giao dịch bị trừ 2 lần (duplicate charge)
✅ Khách hàng không nhận được hàng/dịch vụ và được Merchant xác nhận

**Các trường hợp không áp dụng hoàn tiền tự động:**
❌ Khách hàng đổi ý sau khi giao dịch thành công (do Merchant quyết định chính sách riêng)
❌ Giao dịch đã quá 45 ngày
❌ Merchant không cung cấp được bằng chứng hợp lệ

**Thời hạn nộp yêu cầu:** 45 ngày kể từ ngày phát sinh.

Có trường hợp cụ thể nào Quý đối tác cần xác nhận có đủ điều kiện hoàn tiền không?""",
            follow_up=None
        ),

        SubIntent(
            intent_id="dispute.theo_doi_trang_thai_hoan",
            trigger_keywords=["theo dõi hoàn tiền", "tiền hoàn đến đâu", "trạng thái refund", "kiểm tra hoàn tiền", "refund chưa về"],
            trigger_patterns=[
                r"(theo dõi|kiểm tra|xem).*(trạng thái|tiến độ).*(hoàn tiền|refund)",
                r"(hoàn tiền|refund).*(chưa về|bao giờ về|khi nào về|đến đâu rồi)",
                r"(trạng thái|tình trạng).*(yêu cầu hoàn|tra soát|dispute)",
            ],
            response="""**Cách theo dõi tiến độ hoàn tiền:**

**1. Merchant Portal** *(nhanh nhất)*
Đăng nhập merchant.zalopay.vn → "Tra soát & Hoàn tiền" → Lọc theo trạng thái:
- `Đang xử lý` — đã tiếp nhận, đang xác minh
- `Chờ phê duyệt` — xác minh xong, chờ duyệt chi
- `Đã hoàn tiền` — hoàn thành
- `Từ chối` — không đủ điều kiện (có lý do kèm theo)

**2. Kiểm tra qua email** — ZaloPay gửi cập nhật tự động qua từng bước xử lý.

**3. Liên hệ trực tiếp** nếu cần gấp:
dispute-team@zalopay.vn — ghi rõ mã yêu cầu tra soát (dispute ID) hoặc zptransid.

Thời gian xử lý tra soát đơn lẻ: **03 ngày làm việc**.
Thời gian xử lý bulk refund: **05 ngày làm việc** (+ thêm 02 ngày nếu > 500 triệu đồng).""",
            follow_up=None
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 4 — Kiểm soát rủi ro, khóa ví, khoanh giữ số dư
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_RISK = DomainEntry(
    domain="risk_control",
    domain_keywords=[
        "khóa ví", "tạm khóa", "khóa tài khoản", "khoanh giữ số dư", "khoanh giữ",
        "hold balance", "freeze", "kiểm soát rủi ro", "risk control",
        "vietcombank", "bidv", "msb", "techcombank", "nghi ngờ gian lận",
        "aml", "kyc nâng cao", "phong tỏa", "tạm dừng giao dịch",
        "hạn chế giao dịch", "merchant bị khóa", "unlock", "mở khóa",
        "số dư bị giữ", "bị phong tỏa", "giữ tiền",
    ],
    sub_intents=[

        SubIntent(
            intent_id="risk.tai_khoan_bi_khoa",
            trigger_keywords=["tài khoản bị khóa", "ví bị khóa", "merchant bị khóa", "tại sao bị khóa", "lý do khóa"],
            trigger_patterns=[
                r"(ví|tài khoản|merchant).*(bị khóa|bị tạm khóa|không giao dịch được|bị dừng)",
                r"(tại sao|lý do|vì sao).*(bị khóa|tài khoản khóa|không dùng được)",
                r"(khóa|freeze|tạm dừng).*(tài khoản|ví|merchant).*(nguyên nhân|lý do)",
            ],
            response="""ZaloPay sẽ gửi **thông báo bằng văn bản qua email đã đăng ký** khi khóa tài khoản Merchant, kèm lý do cụ thể.

**Các nguyên nhân phổ biến dẫn đến khóa tài khoản:**
- Tần suất giao dịch tăng đột biến bất thường
- Tỷ lệ hoàn tiền / khiếu nại vượt ngưỡng cho phép (>2% volume tháng)
- Thông tin đăng ký không nhất quán với hoạt động thực tế
- Yêu cầu từ cơ quan có thẩm quyền (Ngân hàng Nhà nước, công an,...)
- Ngân hàng đối tác (Vietcombank/BIDV/MSB/Techcombank) báo cáo tài khoản liên quan

**Kiểm tra ngay:**
1. Xem email đã đăng ký với ZaloPay (kể cả Spam)
2. Đăng nhập Merchant Portal — mục "Trạng thái tài khoản" sẽ hiển thị lý do

Để giải quyết nhanh, Quý đối tác liên hệ:
📧 risk-management@zalopay.vn
☎️ Hotline bảo mật 24/7: 1800 577 200""",
            follow_up="Quý đối tác đã nhận được email thông báo từ ZaloPay chưa? Nội dung thông báo có ghi lý do cụ thể nào không?"
        ),

        SubIntent(
            intent_id="risk.khoanh_giu_so_du_48h",
            trigger_keywords=[
                "khoanh giữ số dư", "hold balance", "48 giờ", "giữ tiền",
                "số dư bị giữ", "freeze balance", "khoanh giữ", "emergency hold",
                "số dư bị khóa", "không rút được tiền",
            ],
            trigger_patterns=[
                r"(khoanh giữ|emergency hold|freeze).*(số dư|tiền|balance)",
                r"(số dư|tiền).*(bị giữ|bị khóa|không rút được|bị phong tỏa)",
                r"48.?(giờ|h|hour).*(khoanh giữ|hold|giữ|xử lý|risk)",
                r"(vietcombank|bidv|msb|techcombank).*(yêu cầu|thông báo|giữ|phong tỏa|hold)",
                r"(khoanh|giữ).*(số dư).*(khẩn cấp|rủi ro|nghi ngờ|đáng ngờ)",
            ],
            response="""**Cơ chế Khoanh giữ số dư khẩn cấp (Emergency Balance Hold):**

Khi ZaloPay nhận được thông báo từ ngân hàng đối tác (**Vietcombank, BIDV, MSB, Techcombank**) về giao dịch đáng ngờ, hệ thống sẽ tự động khoanh giữ số dư trong **tối đa 48 giờ làm việc** để phục vụ điều tra.

**Trong thời gian khoanh giữ:**
- ✅ Vẫn nhận thanh toán từ khách hàng bình thường
- ❌ Không thực hiện được lệnh rút tiền / settlement
- ❌ Không thực hiện disbursement ra ngoài

**Sau 48 giờ:**
- Nếu không có vấn đề: số dư tự động mở khóa
- Nếu cần điều tra thêm: ZaloPay thông báo và cung cấp timeline cụ thể

**Để biết lý do và tiến độ xử lý:**
📧 risk-management@zalopay.vn — ghi rõ Mã Merchant và thời điểm phát hiện
☎️ 1800 577 200 (24/7)""",
            follow_up="Số dư bị khoanh giữ từ khi nào? Quý đối tác đã nhận được thông báo từ ZaloPay hay từ ngân hàng đối tác chưa?"
        ),

        SubIntent(
            intent_id="risk.khieu_nai_mo_khoa",
            trigger_keywords=["mở khóa", "unlock", "khiếu nại khóa", "yêu cầu mở", "kháng cáo", "muốn mở khóa tài khoản"],
            trigger_patterns=[
                r"(mở khóa|unlock|khiếu nại).*(tài khoản|ví|merchant)",
                r"(yêu cầu|muốn|cần).*(mở khóa|unlock|khôi phục).*(tài khoản|ví)",
                r"(kháng cáo|phản đối|giải trình).*(quyết định|khóa|tạm dừng)",
                r"(làm thế nào|thủ tục|quy trình).*(mở khóa|unlock|khiếu nại)",
            ],
            response="""**Quy trình khiếu nại và mở khóa tài khoản:**

Quý đối tác có quyền nộp khiếu nại trong vòng **48 giờ** kể từ khi nhận thông báo khóa.

**Hồ sơ khiếu nại cần chuẩn bị:**
1. **Công văn giải trình** — có chữ ký người đại diện pháp lý và dấu doanh nghiệp
2. **Bằng chứng hợp pháp** của các giao dịch bị nghi ngờ:
   - Hóa đơn bán hàng / chứng từ giao dịch
   - Log hệ thống, ảnh chụp màn hình
   - Hợp đồng với đối tác/khách hàng liên quan (nếu có)
3. **Thông tin liên hệ trực tiếp** để làm việc với Bộ phận Tuân thủ

**Nộp hồ sơ:**
📧 risk-management@zalopay.vn
Tiêu đề: `[Khiếu nại khóa tài khoản] Mã Merchant - Ngày nhận thông báo`

**Thời gian xem xét:** 02 ngày làm việc kể từ khi nhận đủ hồ sơ.
Trong thời gian xem xét, Quý đối tác sẽ được cung cấp số điện thoại của chuyên viên phụ trách để liên lạc trực tiếp.""",
            follow_up=None
        ),

        SubIntent(
            intent_id="risk.dieu_kien_khoa_nen_tranh",
            trigger_keywords=["tránh bị khóa", "ngưỡng rủi ro", "tỷ lệ hoàn tiền", "risk threshold", "điều kiện khóa", "bao nhiêu % thì bị khóa"],
            trigger_patterns=[
                r"(tránh|phòng ngừa|ngăn chặn).*(bị khóa|khóa tài khoản|risk)",
                r"(ngưỡng|mức|tỷ lệ).*(hoàn tiền|refund|chargeback|khiếu nại).*(bao nhiêu|bao nhiêu %|tối đa)",
                r"(điều kiện|tiêu chí|khi nào).*(bị khóa|bị tạm dừng|bị hạn chế)",
            ],
            response="""**Các ngưỡng rủi ro phổ biến Merchant cần lưu ý:**

| Chỉ số | Ngưỡng cảnh báo | Ngưỡng xử lý |
|---|---|---|
| Tỷ lệ hoàn tiền / volume | > 1.5% | > 2% |
| Tỷ lệ chargeback | > 0.5% | > 1% |
| Tăng đột biến volume | > 3x bình thường | > 5x bình thường |
| Giao dịch giá trị lớn bất thường | Cảnh báo tự động | Review thủ công |

**Thực hành tốt để duy trì tài khoản:**
- Đảm bảo mô tả sản phẩm/dịch vụ rõ ràng, tránh hoàn tiền do không đúng kỳ vọng
- Xử lý khiếu nại khách hàng nhanh, trước khi leo thang lên ZaloPay
- Thông báo sớm cho ZaloPay nếu có sự kiện marketing lớn dẫn đến tăng volume đột biến
- Giữ thông tin doanh nghiệp luôn cập nhật và nhất quán

Nếu Quý đối tác nhận được email cảnh báo rủi ro từ ZaloPay, hãy liên hệ ngay để được tư vấn điều chỉnh trước khi bị tạm khóa.""",
            follow_up=None
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 5 — Đối soát phí & sai lệch trạng thái giao dịch
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_RECONCILIATION = DomainEntry(
    domain="reconciliation_fee",
    domain_keywords=[
        "đối soát", "reconciliation", "phí dịch vụ", "service fee",
        "mdr", "merchant discount rate", "phí thanh toán", "phí giao dịch",
        "báo cáo đối soát", "sai lệch", "chênh lệch",
        "trạng thái giao dịch", "pending", "sai trạng thái", "giao dịch treo",
        "giao dịch chờ xử lý", "hóa đơn phí", "invoice", "sao kê",
    ],
    sub_intents=[

        SubIntent(
            intent_id="recon.phi_mdr",
            trigger_keywords=["phí mdr", "merchant discount rate", "mức phí", "phí bao nhiêu", "phí % là bao nhiêu", "phí giao dịch"],
            trigger_patterns=[
                r"(phí mdr|merchant discount rate|mdr).*(bao nhiêu|mức|tính|áp dụng|là gì)",
                r"(mức phí|phí dịch vụ|service fee).*(zalopay|merchant|bao nhiêu|%)",
                r"(tính phí|cách tính|áp dụng phí).*(giao dịch|thanh toán|merchant)",
                r"(phí|fee).*(zalopay thu|trừ|khấu trừ).*(bao nhiêu|%)",
            ],
            response="""**Phí MDR (Merchant Discount Rate) tại ZaloPay:**

Mức phí MDR **khác nhau theo từng Merchant** và được quy định rõ trong **Phụ lục Hợp đồng** — không có mức phí chung cho tất cả.

**Các yếu tố ảnh hưởng đến mức phí:**
- Ngành nghề kinh doanh (ăn uống, bán lẻ, thương mại điện tử, dịch vụ,...)
- Khối lượng giao dịch hàng tháng (volume càng cao, phí càng ưu đãi)
- Thỏa thuận riêng trong quá trình ký kết hợp đồng
- Phương thức thanh toán (QR, ví ZaloPay, liên kết thẻ/ngân hàng)

**Để biết mức phí áp dụng cho tài khoản của Quý đối tác:**
1. Xem lại **Phụ lục Hợp đồng** đã ký
2. Đăng nhập Merchant Portal → "Cấu hình phí"
3. Liên hệ Account Manager phụ trách hoặc gửi email: finance-ops@zalopay.vn""",
            follow_up=None
        ),

        SubIntent(
            intent_id="recon.bao_cao_doi_soat_phi",
            trigger_keywords=["báo cáo đối soát", "đối soát phí", "sao kê phí", "báo cáo phí", "tổng kết phí tháng", "cuối tháng"],
            trigger_patterns=[
                r"(báo cáo|sao kê|report).*(đối soát|phí|fee).*(tháng|định kỳ|hàng tháng)",
                r"(đối soát phí|phí dịch vụ).*(tháng|hàng tháng|định kỳ|cuối tháng)",
                r"(xem|lấy|tải|download).*(báo cáo đối soát|sao kê|statement)",
                r"(ngày nào|khi nào).*(gửi|có).*(báo cáo|sao kê|đối soát).*(phí|tháng)",
            ],
            response="""**Lịch đối soát phí dịch vụ hàng tháng:**

- **Ngày 05 hàng tháng**: Hệ thống gửi tự động Báo cáo Đối soát Phí Dịch vụ qua email đã đăng ký
- Báo cáo bao gồm: phí MDR theo từng phương thức, phí dịch vụ gia tăng (nếu có), phí hạ tầng kỹ thuật, tổng khấu trừ trong tháng

**Tải báo cáo thủ công:**
Merchant Portal → "Báo cáo tài chính" → "Đối soát phí" → Chọn kỳ

**Quy trình phản hồi:**
- Quý đối tác có **10 ngày làm việc** kể từ ngày nhận báo cáo để phản hồi nếu có sai lệch
- Hóa đơn VAT được xuất sau khi hết thời hạn phản hồi

Nếu chưa nhận được báo cáo tháng (đã qua ngày 07), vui lòng email: finance-ops@zalopay.vn""",
            follow_up=None
        ),

        SubIntent(
            intent_id="recon.sai_lech_doi_soat",
            trigger_keywords=[
                "sai lệch", "chênh lệch", "không khớp", "số liệu sai",
                "phí sai", "tính sai phí", "phát hiện sai", "số liệu không đúng",
                "khác nhau giữa hai hệ thống", "mismatch", "báo cáo sai",
                "số liệu chênh", "phí bị tính sai", "phí không đúng",
                "phát hiện", "tìm thấy lỗi", "phát sinh sai",
            ],
            trigger_patterns=[
                r"(sai lệch|chênh lệch|không khớp|mismatch).*(đối soát|phí|fee|số liệu|dữ liệu)",
                r"(phát hiện|tìm thấy|nhận ra).*(sai lệch|chênh lệch|lỗi|sai).*(đối soát|phí|dữ liệu)",
                r"(số liệu|phí|fee|số tiền).*(sai|không đúng|khác).*(hệ thống zalopay|báo cáo zalopay)",
                r"(báo cáo zalopay|hệ thống zalopay).*(khác|không khớp|chênh).*(hệ thống|thực tế|merchant)",
                r"(xử lý|phản hồi|báo).*(sai lệch|chênh lệch).*(đối soát|phí tháng)",
            ],
            response="""**Quy trình xử lý sai lệch đối soát:**

**Bước 1 — Chuẩn bị hồ sơ:**
- Tải mẫu báo cáo sai lệch: Merchant Portal → Templates → "Dispute Reconciliation Form"
- Điền đầy đủ: kỳ đối soát, loại sai lệch, số tiền chênh lệch, giải thích
- Đính kèm file log giao dịch tương ứng từ hệ thống của Quý đối tác

**Bước 2 — Nộp trong thời hạn:**
⚠️ Phải nộp trong vòng **10 ngày làm việc** kể từ ngày nhận báo cáo đối soát
Gửi về: finance-ops@zalopay.vn
Tiêu đề: `[Sai lệch đối soát] Tháng X/YYYY - Tên Merchant`

**Bước 3 — Xử lý và điều chỉnh:**
- Bộ phận Đối soát xác minh trong **05 ngày làm việc**
- Kết quả gửi bằng văn bản qua email
- Điều chỉnh (nếu có) phản ánh vào **kỳ đối soát liền kề**

Sau deadline 10 ngày, ZaloPay không thể xử lý điều chỉnh cho kỳ đó.""",
            follow_up="Quý đối tác phát hiện sai lệch ở kỳ nào và loại phí nào? Cung cấp thêm để mình hỗ trợ cụ thể hơn."
        ),

        SubIntent(
            intent_id="recon.giao_dich_pending",
            trigger_keywords=["giao dịch pending", "giao dịch treo", "giao dịch chờ", "pending mãi", "trạng thái sai", "không cập nhật trạng thái"],
            trigger_patterns=[
                r"(giao dịch|transaction).*(pending|treo|chờ).*(lâu|mãi|không cập nhật|quá lâu|30 phút)",
                r"(trạng thái|status).*(giao dịch|transaction).*(sai|không đúng|không cập nhật|pending hoài)",
                r"(giao dịch|đơn hàng).*(pending|không thành công|không fail|lơ lửng)",
                r"(callback|webhook).*(không nhận|không gửi|fail|lỗi)",
            ],
            response="""**Xử lý giao dịch Pending / Trạng thái không cập nhật:**

Giao dịch ở trạng thái "Pending" quá **30 phút** được xem là bất thường.

**Bước 1 — Tra cứu ngay qua API:**
```
GET /v2/merchant/orderstatus?apptransid={apptransid}
```
Tài liệu đầy đủ: developer.zalopay.vn → API Reference → Query Order

**Bước 2 — Xác định nguyên nhân:**
| Nguyên nhân | Dấu hiệu | Xử lý |
|---|---|---|
| Timeout kết nối | Không nhận callback | Gọi Query Order để lấy trạng thái thật |
| Callback lỗi | Log nhận 4xx/5xx | Kiểm tra endpoint callback, đảm bảo response 200 |
| Hệ thống trung gian | Nhiều GD cùng lúc | Theo dõi thêm 15 phút |
| Lỗi phía ZaloPay | Query vẫn Pending | Báo ngay tech-support |

**Bước 3 — Nếu không tự xử lý được:**
📧 tech-support@zalopay.vn — đính kèm danh sách `apptransid` bị ảnh hưởng
**Cam kết phản hồi trong 02 giờ làm việc.**

⚠️ Không tự ý hoàn tiền cho khách khi chưa xác nhận trạng thái cuối cùng — tránh hoàn tiền nhầm.""",
            follow_up="Quý đối tác có thể cung cấp apptransid hoặc zptransid của các giao dịch đang pending không?"
        ),

        SubIntent(
            intent_id="recon.hoa_don_vat",
            trigger_keywords=["hóa đơn VAT", "invoice", "xuất hóa đơn", "hóa đơn phí", "thuế VAT", "hóa đơn điện tử"],
            trigger_patterns=[
                r"(hóa đơn|invoice).*(vat|thuế|điện tử|xuất|lấy|nhận|khi nào)",
                r"(xuất|cung cấp|gửi).*(hóa đơn|invoice).*(phí|dịch vụ|zalopay)",
                r"(cần|muốn|yêu cầu).*(hóa đơn vat|invoice).*(đối soát|phí dịch vụ)",
            ],
            response="""**Quy trình xuất Hóa đơn VAT phí dịch vụ:**

Hóa đơn VAT được xuất **sau khi kết thúc thời hạn phản hồi đối soát** (tức sau ngày 15 của tháng sau).

**Timeline:**
- Ngày 05: Gửi báo cáo đối soát phí
- Ngày 05–15: Thời gian phản hồi sai lệch (10 ngày làm việc)
- Sau ngày 15: Xuất hóa đơn VAT và gửi qua email

**Hóa đơn điện tử** gửi đến email kế toán đã đăng ký. Nếu chưa nhận được hoặc cần điều chỉnh thông tin, gửi yêu cầu: finance-ops@zalopay.vn kèm:
- Mã Merchant
- Kỳ cần xuất hóa đơn (tháng/năm)
- Thông tin hóa đơn: Tên công ty, MST, địa chỉ (nếu cần chỉnh)

**Lưu ý:** Hóa đơn đã xuất không thể điều chỉnh số tiền. Nếu phát hiện sai số tiền, phải xử lý qua quy trình sai lệch đối soát trước khi xuất hóa đơn.""",
            follow_up=None
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# Tập hợp tất cả domains
# ─────────────────────────────────────────────────────────────────────────────

ALL_DOMAINS: List[DomainEntry] = [
    DOMAIN_ONBOARDING,
    DOMAIN_CASHFLOW,
    DOMAIN_DISPUTE,
    DOMAIN_RISK,
    DOMAIN_RECONCILIATION,
]


# ─────────────────────────────────────────────────────────────────────────────
# Sensitive & negative keywords (giữ nguyên từ v1)
# ─────────────────────────────────────────────────────────────────────────────

SENSITIVE_KEYWORDS: List[str] = [
    "tranh chấp pháp lý", "tranh chấp", "kiện", "kiện tụng", "khởi kiện",
    "tòa án", "cơ quan điều tra", "công an", "cảnh sát", "bộ công an",
    "viện kiểm sát", "tố tụng", "truy tố", "bắt giữ", "phong tỏa tài sản",
    "gian lận", "lừa đảo", "chiếm đoạt", "rửa tiền", "money laundering",
    "fraud", "scam", "hack", "tấn công", "đánh cắp tài khoản",
    "mất tiền oan", "bị lừa", "thiệt hại nặng", "tổn thất lớn",
    "khủng hoảng", "sự cố nghiêm trọng", "báo chí", "truyền thông",
    "đăng lên mạng", "chia sẻ lên facebook", "tố cáo công khai",
    "luật sư", "tư vấn pháp lý", "pháp lý", "vi phạm pháp luật",
    "vi phạm hợp đồng", "đền bù", "bồi thường thiệt hại",
]

HIGH_NEGATIVE_KEYWORDS: List[str] = [
    "tức giận", "bực bội", "thất vọng hoàn toàn", "không thể chấp nhận",
    "quá tệ", "cực kỳ tệ", "dịch vụ kém", "phục vụ tệ", "không chuyên nghiệp",
    "vô trách nhiệm", "lừa đảo", "scam", "tắc trách", "thờ ơ",
    "không giải quyết", "không ai giúp", "bị bỏ rơi", "mất niềm tin",
    "sẽ chấm dứt hợp đồng", "hủy hợp đồng", "không hợp tác nữa",
    "chuyển sang đơn vị khác", "báo cáo lên cấp trên", "leo thang",
]


# ─────────────────────────────────────────────────────────────────────────────
# Classifier — 2 cấp: domain → sub-intent
# ─────────────────────────────────────────────────────────────────────────────

def detect_sensitive(text: str) -> bool:
    text_norm = _normalize(text)
    return any(_normalize(kw) in text_norm for kw in SENSITIVE_KEYWORDS)


def detect_high_negative(text: str) -> bool:
    text_norm = _normalize(text)
    return any(_normalize(kw) in text_norm for kw in HIGH_NEGATIVE_KEYWORDS)


def should_escalate(text: str) -> bool:
    return detect_sensitive(text) or detect_high_negative(text)


def _score_sub_intent(text_norm: str, sub: SubIntent) -> int:
    score = 0
    for kw in sub.trigger_keywords:
        if _normalize(kw) in text_norm:
            score += 2
    for pattern in sub.trigger_patterns:
        norm_pattern = _normalize(pattern)
        if re.search(norm_pattern, text_norm, re.IGNORECASE | re.UNICODE):
            score += 5
    return score


def find_best_match(text: str) -> Optional[Tuple[DomainEntry, SubIntent]]:
    """
    Trả về (domain, sub_intent) phù hợp nhất với câu hỏi của merchant.
    Áp dụng scoring 2 cấp:
    1. Domain score: keyword match tổng quát
    2. Sub-intent score: keyword + pattern đặc thù
    """
    text_norm = _normalize(text)
    best_domain: Optional[DomainEntry] = None
    best_sub: Optional[SubIntent] = None
    best_score = 0

    for domain in ALL_DOMAINS:
        # Domain-level keyword score
        domain_score = sum(
            2 for kw in domain.domain_keywords
            if _normalize(kw) in text_norm
        )
        if domain_score == 0:
            continue

        # Sub-intent scoring within domain
        for sub in domain.sub_intents:
            sub_score = _score_sub_intent(text_norm, sub)
            total = domain_score + sub_score
            if total > best_score:  # strict: only update on improvement
                best_score = total
                best_domain = domain
                best_sub = sub

    if best_score >= 2 and best_domain is not None and best_sub is not None:
        return (best_domain, best_sub)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Backward-compatible wrapper (agent.py vẫn dùng được)
# ─────────────────────────────────────────────────────────────────────────────

class MatchResult:
    """Wrapper để agent.py có thể dùng .response và .follow_up như cũ"""
    def __init__(self, domain: str, response: str, follow_up: Optional[str]):
        self.domain = domain
        self.response = response
        self.follow_up = follow_up


def find_matching_domain(text: str) -> Optional[MatchResult]:
    result = find_best_match(text)
    if result is None:
        return None
    domain_entry, sub_intent = result
    return MatchResult(
        domain=f"{domain_entry.domain}.{sub_intent.intent_id}",
        response=sub_intent.response,
        follow_up=sub_intent.follow_up,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standard responses
# ─────────────────────────────────────────────────────────────────────────────

ESCALATION_RESPONSE = """Kính gửi Quý đối tác,

ZaloPay đã ghi nhận yêu cầu của Quý đối tác. Nội dung phản ánh cần được xử lý trực tiếp bởi chuyên viên có thẩm quyền để đảm bảo quyền lợi tối đa.

Chúng tôi cam kết có nhân viên chuyên trách liên hệ lại trong vòng **02 giờ làm việc**.

Trong thời gian chờ, Quý đối tác có thể liên hệ khẩn:
- **Hotline ưu tiên:** 1800 577 577 (miễn phí, 8:00–22:00)
- **Email:** escalation@zalopay.vn

Mã tiếp nhận sẽ được gửi qua email đã đăng ký trong vòng 15 phút.

ZaloPay trân trọng sự tin tưởng của Quý đối tác."""

OUT_OF_SCOPE_RESPONSE = """Kính gửi Quý đối tác,

Nội dung câu hỏi hiện nằm ngoài phạm vi hỗ trợ tự động, vốn được thiết kế cho 05 nhóm nghiệp vụ chính:

1. Quy trình Onboarding và tích hợp Sandbox (Quy định 2345)
2. Xử lý lỗi dòng tiền và cập nhật tài khoản thụ hưởng
3. Tra soát và hoàn tiền hàng loạt
4. Kiểm soát rủi ro, khóa ví và khoanh giữ số dư khẩn cấp
5. Đối soát phí dịch vụ và xử lý sai lệch trạng thái giao dịch

Để được hỗ trợ, Quý đối tác vui lòng liên hệ:
- **Email:** merchant-support@zalopay.vn
- **Hotline:** 1800 577 577 (miễn phí, 8:00–22:00)
- **Merchant Portal:** merchant.zalopay.vn/support

Đội ngũ chuyên viên sẽ phản hồi trong vòng 01 ngày làm việc."""
