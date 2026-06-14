"""
ZaloPay Merchant Support Knowledge Base
Covers 5 operational domains as per internal guidelines.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re
import unicodedata


def _normalize(text: str) -> str:
    """Strip Vietnamese diacritics so matching works regardless of whether
    the merchant types with or without accent marks."""
    nfd = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


@dataclass
class KnowledgeEntry:
    domain: str
    keywords: List[str]
    question_patterns: List[str]
    response: str
    follow_up: Optional[str] = None


KNOWLEDGE_BASE: List[KnowledgeEntry] = [

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 1: Onboarding & Sandbox theo Quy định 2345
    # ─────────────────────────────────────────────────────────────────
    KnowledgeEntry(
        domain="onboarding_sandbox",
        keywords=[
            "onboarding", "đăng ký", "tích hợp", "sandbox", "thử nghiệm",
            "quy định 2345", "qd2345", "môi trường test", "app_id", "key",
            "merchant id", "hợp đồng", "kích hoạt", "phê duyệt", "kyc",
            "xác minh danh tính", "giấy phép kinh doanh", "tài khoản merchant",
            "production", "go live", "chuyển production", "api key",
        ],
        question_patterns=[
            r"(đăng ký|tích hợp|onboard).*(zalopay|merchant|đối tác)",
            r"(sandbox|môi trường test|thử nghiệm).*(như thế nào|ra sao|hướng dẫn)",
            r"quy định 2345",
            r"(app_id|api key|merchant id).*(lấy|nhận|cấp|tạo)",
            r"(hợp đồng|kyc|xác minh).*(merchant|đối tác)",
            r"(chuyển|nâng lên|go.?live).*(production|môi trường thật)",
        ],
        response="""Kính gửi Quý đối tác,

Quy trình onboarding và tích hợp môi trường Sandbox của ZaloPay được thực hiện theo Quy định số 2345 về Tiêu chuẩn Kỹ thuật Tích hợp Đối tác, gồm các bước chính như sau:

Bước 1 — Nộp hồ sơ pháp lý: Quý đối tác cung cấp Giấy chứng nhận đăng ký kinh doanh còn hiệu lực, thông tin đại diện pháp lý, và mô tả mô hình kinh doanh. Đội ngũ Tuân thủ (Compliance) sẽ tiến hành xác minh KYC trong vòng 03 ngày làm việc kể từ ngày nhận đủ hồ sơ.

Bước 2 — Cấp thông tin môi trường Sandbox: Sau khi hồ sơ được phê duyệt, hệ thống sẽ tự động cấp App ID, API Key và Secret Key cho môi trường Sandbox qua email đã đăng ký. Quý đối tác có 30 ngày để hoàn thiện tích hợp kỹ thuật và chạy thử nghiệm.

Bước 3 — Kiểm tra kỹ thuật (Technical Review): Bộ phận Kỹ thuật ZaloPay sẽ thực hiện kiểm tra toàn bộ luồng thanh toán, xử lý callback, và cơ chế đối soát. Kết quả kiểm tra sẽ được phản hồi trong vòng 05 ngày làm việc.

Bước 4 — Chuyển môi trường Production: Sau khi vượt qua Technical Review và ký kết hợp đồng hợp tác chính thức, thông tin Production (App ID, Key) sẽ được cấp riêng biệt. Quý đối tác không được sử dụng thông tin Sandbox trên môi trường thật.

Lưu ý quan trọng: Theo Quy định 2345, mọi thay đổi về mô hình kinh doanh sau khi onboarding thành công đều yêu cầu cập nhật hồ sơ và phê duyệt lại từ Bộ phận Tuân thủ.

Để được hỗ trợ trực tiếp về quy trình onboarding, Quý đối tác vui lòng liên hệ: merchant-support@zalopay.vn hoặc gọi hotline 1800 577 577 (miễn phí, từ 8:00–22:00 hàng ngày).""",
        follow_up="Quý đối tác có cần hỗ trợ thêm về bước cụ thể nào trong quy trình onboarding không?"
    ),

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 2: Xử lý lỗi dòng tiền và cập nhật tài khoản thụ hưởng khi số dư bằng 0
    # ─────────────────────────────────────────────────────────────────
    KnowledgeEntry(
        domain="cashflow_errors",
        keywords=[
            "số dư bằng 0", "số dư âm", "số dư không đủ", "dòng tiền",
            "tài khoản thụ hưởng", "cập nhật tài khoản", "đổi ngân hàng",
            "thanh toán thất bại", "giao dịch lỗi", "lệnh chi thất bại",
            "settlement", "quyết toán", "chuyển tiền thất bại", "disbursement",
            "nạp tiền", "số dư ví", "balance", "insufficient", "không đủ số dư",
            "tài khoản nhận tiền", "thay đổi tài khoản", "bank account",
        ],
        question_patterns=[
            r"(số dư|balance).*(bằng 0|âm|không đủ|thiếu)",
            r"(lỗi|thất bại|fail).*(dòng tiền|thanh toán|settlement|quyết toán)",
            r"(cập nhật|thay đổi|đổi).*(tài khoản thụ hưởng|tài khoản nhận|ngân hàng nhận)",
            r"(chuyển tiền|disbursement|settlement).*(lỗi|thất bại|không thực hiện)",
            r"(nạp|bổ sung).*(số dư|ví|tiền).*(merchant|đối tác)",
        ],
        response="""Kính gửi Quý đối tác,

Đối với các sự cố liên quan đến lỗi dòng tiền và cập nhật tài khoản thụ hưởng, ZaloPay xử lý theo quy trình sau:

Trường hợp 1 — Số dư ví Merchant bằng 0, dẫn đến lệnh chi thất bại: Khi số dư không đủ để thực hiện quyết toán (settlement), hệ thống sẽ giữ lại các lệnh chi trong hàng đợi và gửi cảnh báo tự động qua email đã đăng ký. Quý đối tác cần nạp bổ sung số dư hoặc liên hệ Bộ phận Tài chính để được duyệt tạm ứng khẩn cấp (áp dụng cho đối tác đủ điều kiện). Sau khi số dư được bổ sung, hệ thống sẽ tự động xử lý lại các lệnh chi tồn đọng trong vòng 15 phút.

Trường hợp 2 — Cập nhật tài khoản thụ hưởng: Yêu cầu thay đổi tài khoản ngân hàng nhận tiền phải được thực hiện qua email chính thức của doanh nghiệp (không chấp nhận yêu cầu qua điện thoại hoặc chat). Hồ sơ yêu cầu bao gồm: (a) Công văn yêu cầu thay đổi có chữ ký và dấu doanh nghiệp; (b) Bản sao sổ tài khoản ngân hàng mới hoặc xác nhận mở tài khoản; (c) CMND/CCCD của người đại diện pháp lý. Thời gian xử lý là 02 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ. Trong thời gian chờ cập nhật, các lệnh settlement vẫn được xử lý về tài khoản cũ.

Trường hợp 3 — Lỗi kỹ thuật dòng tiền không rõ nguyên nhân: Quý đối tác cung cấp mã giao dịch (Transaction ID), thời điểm phát sinh, và số tiền liên quan để Bộ phận Kỹ thuật tra cứu. Cam kết phản hồi trong vòng 04 giờ làm việc.

Để được hỗ trợ khẩn cấp về dòng tiền, Quý đối tác vui lòng gửi yêu cầu đến: finance-ops@zalopay.vn với tiêu đề "[KHẨN] Lỗi dòng tiền - [Tên Merchant] - [Mã Merchant]".""",
        follow_up="Quý đối tác đang gặp phải trường hợp nào trong số các tình huống trên? Vui lòng cho biết thêm để được hỗ trợ chính xác hơn."
    ),

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 3: Tiếp nhận tra soát và hoàn tiền hàng loạt
    # ─────────────────────────────────────────────────────────────────
    KnowledgeEntry(
        domain="dispute_refund",
        keywords=[
            "tra soát", "chargeback", "hoàn tiền", "refund", "khiếu nại giao dịch",
            "hoàn tiền hàng loạt", "bulk refund", "đối tác beta cinemas",
            "rạp chiếu phim", "vé xem phim", "sự cố kỹ thuật đối tác",
            "refund policy", "chính sách hoàn tiền", "giao dịch lỗi hoàn tiền",
            "khách hàng khiếu nại", "người dùng khiếu nại", "dispute",
            "hoàn hàng", "đổi trả", "hủy đơn hàng", "hủy vé",
            "hàng loạt", "batch", "nhiều giao dịch cùng lúc",
        ],
        question_patterns=[
            r"(tra soát|chargeback|khiếu nại).*(giao dịch|thanh toán)",
            r"(hoàn tiền|refund).*(hàng loạt|bulk|nhiều|batch)",
            r"(beta cinema|rạp phim|vé phim).*(hoàn|refund|lỗi)",
            r"(quy trình|thủ tục|hướng dẫn).*(hoàn tiền|refund|tra soát)",
            r"(khách hàng|người dùng).*(khiếu nại|phàn nàn|yêu cầu hoàn)",
            r"(hủy|cancel).*(đơn|vé|giao dịch).*(hoàn tiền|refund)",
        ],
        response="""Kính gửi Quý đối tác,

ZaloPay hỗ trợ hai hình thức tra soát và hoàn tiền như sau:

Hình thức 1 — Tra soát giao dịch đơn lẻ: Áp dụng khi khách hàng khiếu nại về một giao dịch cụ thể. Quý đối tác cần cung cấp: (a) Mã giao dịch ZaloPay (zptransid); (b) Thời điểm giao dịch; (c) Số tiền; (d) Lý do tra soát kèm bằng chứng liên quan (ảnh chụp màn hình, log hệ thống). Thời hạn tra soát tối đa là 45 ngày kể từ ngày phát sinh giao dịch. Bộ phận Tra soát sẽ phản hồi kết quả trong vòng 03 ngày làm việc.

Hình thức 2 — Hoàn tiền hàng loạt (Bulk Refund): Áp dụng khi sự cố kỹ thuật từ phía đối tác ảnh hưởng đến nhiều giao dịch cùng lúc (ví dụ: sự cố hệ thống của Beta Cinemas dẫn đến lỗi xuất vé sau khi thanh toán thành công). Quy trình xử lý như sau: Quý đối tác gửi file danh sách giao dịch theo template chuẩn của ZaloPay (định dạng .xlsx, tối đa 10,000 dòng/file) kèm công văn xác nhận sự cố lên địa chỉ dispute-team@zalopay.vn. Bộ phận Tra soát sẽ xác minh từng giao dịch trong vòng 05 ngày làm việc. Sau khi phê duyệt, tiền sẽ được hoàn vào ví ZaloPay của khách hàng trong vòng 24 giờ (đối với ví ZaloPay) hoặc 05-07 ngày làm việc (đối với thẻ ngân hàng/tài khoản ngân hàng liên kết).

Lưu ý đặc biệt: Đối với các trường hợp hoàn tiền hàng loạt có giá trị tổng trên 500 triệu đồng, yêu cầu phải được phê duyệt bởi Giám đốc Vận hành ZaloPay trước khi xử lý. Thời gian xử lý trong trường hợp này có thể kéo dài thêm 02 ngày làm việc.

Để được hỗ trợ, Quý đối tác liên hệ: dispute-team@zalopay.vn hoặc gọi đường dây chuyên biệt 1800 577 100 (8:00–18:00, thứ Hai đến thứ Sáu).""",
        follow_up="Quý đối tác cần hỗ trợ tra soát giao dịch đơn lẻ hay hoàn tiền hàng loạt? Vui lòng cung cấp thêm thông tin để được xử lý nhanh hơn."
    ),

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 4: Kiểm soát rủi ro – khóa ví và khoanh giữ số dư khẩn cấp
    # ─────────────────────────────────────────────────────────────────
    KnowledgeEntry(
        domain="risk_control",
        keywords=[
            "khóa ví", "tạm khóa", "khóa tài khoản", "khoanh giữ số dư",
            "hold balance", "freeze", "kiểm soát rủi ro", "risk control",
            "vietcombank", "bidv", "msb", "techcombank", "ngân hàng phối hợp",
            "48 giờ làm việc", "khẩn cấp", "nghi ngờ gian lận", "suspicious",
            "aml", "kyc nâng cao", "điều tra", "phong tỏa", "tạm dừng giao dịch",
            "tài khoản bị hạn chế", "hạn chế giao dịch", "merchant bị khóa",
            "unlock", "mở khóa", "khiếu nại khóa ví",
        ],
        question_patterns=[
            r"(khóa|tạm khóa|freeze|phong tỏa).*(ví|tài khoản|merchant)",
            r"(khoanh giữ|hold|giữ lại).*(số dư|tiền|balance)",
            r"(kiểm soát|kiểm tra).*(rủi ro|risk).*(như thế nào|quy trình)",
            r"(vietcombank|bidv|msb|techcombank).*(phối hợp|yêu cầu|thông báo)",
            r"(48 giờ|2 ngày).*(làm việc|xử lý|khóa|giữ)",
            r"(mở khóa|unlock|khiếu nại).*(ví|tài khoản|khóa)",
            r"(tạm dừng|ngừng|dừng).*(giao dịch|thanh toán).*(merchant)",
        ],
        response="""Kính gửi Quý đối tác,

Chính sách Kiểm soát Rủi ro của ZaloPay được thực hiện theo quy định của Ngân hàng Nhà nước Việt Nam và các thỏa thuận hợp tác với ngân hàng đối tác, bao gồm Vietcombank, BIDV, MSB và Techcombank. Thông tin chi tiết như sau:

Cơ chế khóa ví và tạm dừng giao dịch: ZaloPay có quyền áp dụng biện pháp tạm khóa tài khoản Merchant khi phát hiện các dấu hiệu bất thường bao gồm nhưng không giới hạn ở: tần suất giao dịch tăng đột biến bất thường, tỷ lệ hoàn tiền/khiếu nại vượt ngưỡng cho phép, thông tin đăng ký không nhất quán với hoạt động thực tế, hoặc nhận được yêu cầu từ cơ quan có thẩm quyền.

Cơ chế khoanh giữ số dư khẩn cấp (Emergency Balance Hold): Trong trường hợp nhận được thông báo từ ngân hàng đối tác (Vietcombank, BIDV, MSB, Techcombank) về tài khoản liên quan đến giao dịch đáng ngờ, ZaloPay sẽ tiến hành khoanh giữ số dư trong thời hạn tối đa 48 giờ làm việc để phục vụ quá trình điều tra. Trong thời gian này, Merchant không thể thực hiện giao dịch rút tiền, nhưng vẫn có thể tiếp tục nhận thanh toán từ khách hàng (trừ khi có lệnh tạm dừng toàn phần).

Quy trình khiếu nại và mở khóa: Quý đối tác có quyền gửi khiếu nại chính thức trong vòng 48 giờ kể từ khi nhận thông báo khóa tài khoản. Hồ sơ khiếu nại bao gồm: công văn giải trình có chữ ký đại diện pháp lý, tài liệu chứng minh tính hợp pháp của các giao dịch bị nghi ngờ, và thông tin liên hệ để làm việc trực tiếp với Bộ phận Tuân thủ. Thời gian xem xét và phản hồi là 02 ngày làm việc kể từ khi nhận đủ hồ sơ.

Mọi quyết định khóa tài khoản đều được thông báo bằng văn bản qua email đã đăng ký. Trong trường hợp khẩn cấp, Quý đối tác liên hệ ngay: risk-management@zalopay.vn hoặc hotline bảo mật 1800 577 200 (hoạt động 24/7).""",
        follow_up="Tài khoản Merchant của Quý đối tác hiện đang ở trạng thái nào? Vui lòng cung cấp Mã Merchant để được kiểm tra và hỗ trợ kịp thời."
    ),

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 5: Đối soát phí dịch vụ và xử lý sai lệch trạng thái giao dịch
    # ─────────────────────────────────────────────────────────────────
    KnowledgeEntry(
        domain="reconciliation_fee",
        keywords=[
            "đối soát", "reconciliation", "phí dịch vụ", "service fee",
            "mdr", "merchant discount rate", "phí thanh toán", "phí giao dịch",
            "báo cáo đối soát", "sai lệch", "chênh lệch", "inconsistency",
            "trạng thái giao dịch", "transaction status", "pending", "success",
            "failed", "processing", "sai trạng thái", "giao dịch treo",
            "giao dịch chờ xử lý", "định kỳ", "cuối tháng", "monthly",
            "hóa đơn phí", "invoice", "thanh toán phí", "pay fee",
            "báo cáo tài chính", "statement", "sao kê",
        ],
        question_patterns=[
            r"(đối soát|reconciliation|sao kê).*(phí|fee|tháng|định kỳ)",
            r"(phí dịch vụ|mdr|service fee).*(tính|áp dụng|bao nhiêu|mức)",
            r"(sai lệch|chênh lệch|không khớp).*(đối soát|giao dịch|số tiền|trạng thái)",
            r"(trạng thái|status).*(giao dịch|transaction).*(sai|không đúng|pending mãi|treo)",
            r"(giao dịch|transaction).*(pending|treo|chờ).*(lâu|không cập nhật|quá lâu)",
            r"(báo cáo|report|statement).*(tài chính|giao dịch|đối soát)",
            r"(hóa đơn|invoice|bill).*(phí|fee).*(zalopay|merchant)",
        ],
        response="""Kính gửi Quý đối tác,

ZaloPay thực hiện đối soát phí dịch vụ và xử lý sai lệch trạng thái giao dịch theo quy trình sau:

Đối soát phí dịch vụ định kỳ: Hệ thống ZaloPay tự động tổng hợp và gửi Báo cáo Đối soát Phí Dịch vụ vào ngày 05 hàng tháng, bao gồm chi tiết từng loại phí: Phí MDR (Merchant Discount Rate) theo từng phương thức thanh toán, phí dịch vụ gia tăng (nếu có đăng ký), và phí hạ tầng kỹ thuật. Quý đối tác có 10 ngày làm việc kể từ ngày nhận báo cáo để xem xét và phản hồi nếu có sai lệch. Hóa đơn VAT sẽ được xuất sau khi kết thúc thời hạn phản hồi.

Xử lý sai lệch trong đối soát: Khi phát hiện chênh lệch giữa dữ liệu hệ thống ZaloPay và hệ thống của Quý đối tác, vui lòng gửi báo cáo sai lệch theo mẫu chuẩn (tải tại Merchant Portal) kèm file log giao dịch tương ứng. Bộ phận Đối soát sẽ xác minh trong vòng 05 ngày làm việc và gửi kết quả bằng văn bản. Mọi điều chỉnh phát sinh sẽ được phản ánh vào kỳ đối soát liền kề.

Xử lý sai lệch trạng thái giao dịch: Giao dịch ở trạng thái "Pending" quá 30 phút được xem là bất thường. Nguyên nhân phổ biến bao gồm: timeout kết nối giữa hệ thống đối tác và ZaloPay, lỗi callback không được gửi lại, hoặc sự cố hệ thống trung gian. Để tra cứu và cập nhật lại trạng thái, Quý đối tác sử dụng API Query Order (tài liệu tại Developer Portal) hoặc gửi yêu cầu kèm danh sách Transaction ID đến tech-support@zalopay.vn. Hệ thống sẽ xác nhận trạng thái cuối cùng trong vòng 02 giờ làm việc.

Lưu ý: Mức phí MDR hiện hành được quy định trong Phụ lục Hợp đồng của từng Merchant và có thể khác nhau tùy theo ngành nghề, khối lượng giao dịch, và thỏa thuận riêng. Để biết mức phí áp dụng cho tài khoản của Quý đối tác, vui lòng liên hệ Account Manager phụ trách hoặc gửi email đến finance-ops@zalopay.vn.""",
        follow_up="Quý đối tác cần hỗ trợ đối soát phí hay xử lý sai lệch trạng thái giao dịch? Vui lòng cung cấp thêm thông tin cụ thể."
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Sensitive keywords that trigger escalation to human agents
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


# ─────────────────────────────────────────────────────────────────────────────
# Negative sentiment indicators
# ─────────────────────────────────────────────────────────────────────────────

HIGH_NEGATIVE_KEYWORDS: List[str] = [
    "tức giận", "bực bội", "thất vọng hoàn toàn", "không thể chấp nhận",
    "quá tệ", "cực kỳ tệ", "dịch vụ kém", "phục vụ tệ", "không chuyên nghiệp",
    "vô trách nhiệm", "lừa đảo", "scam", "tắc trách", "thờ ơ",
    "không giải quyết", "không ai giúp", "bị bỏ rơi", "mất niềm tin",
    "sẽ chấm dứt hợp đồng", "hủy hợp đồng", "không hợp tác nữa",
    "chuyển sang đơn vị khác", "báo cáo lên cấp trên", "leo thang",
]


# ─────────────────────────────────────────────────────────────────────────────
# Classifier functions
# ─────────────────────────────────────────────────────────────────────────────

def detect_sensitive(text: str) -> bool:
    text_norm = _normalize(text)
    return any(_normalize(kw) in text_norm for kw in SENSITIVE_KEYWORDS)


def detect_high_negative(text: str) -> bool:
    text_norm = _normalize(text)
    return any(_normalize(kw) in text_norm for kw in HIGH_NEGATIVE_KEYWORDS)


def should_escalate(text: str) -> bool:
    return detect_sensitive(text) or detect_high_negative(text)


def find_matching_domain(text: str) -> Optional[KnowledgeEntry]:
    text_norm = _normalize(text)
    best_match: Optional[KnowledgeEntry] = None
    best_score = 0

    for entry in KNOWLEDGE_BASE:
        score = 0

        # Keyword matching (weight: 1 per keyword) — normalized both sides
        for kw in entry.keywords:
            if _normalize(kw) in text_norm:
                score += 1

        # Pattern matching on normalized text (weight: 3 per matched pattern)
        for pattern in entry.question_patterns:
            norm_pattern = _normalize(pattern)
            if re.search(norm_pattern, text_norm, re.IGNORECASE | re.UNICODE):
                score += 3

        if score > best_score:
            best_score = score
            best_match = entry

    # Require minimum confidence score
    if best_score >= 1:
        return best_match
    return None


ESCALATION_RESPONSE = """Kính gửi Quý đối tác,

ZaloPay đã ghi nhận yêu cầu của Quý đối tác. Căn cứ vào nội dung phản ánh, hệ thống nhận thấy đây là tình huống cần được xử lý trực tiếp bởi chuyên viên có thẩm quyền nhằm đảm bảo quyền lợi tối đa cho Quý đối tác.

Chúng tôi cam kết sẽ có nhân viên chuyên trách liên hệ lại với Quý đối tác trong vòng 02 giờ làm việc kể từ thời điểm tiếp nhận yêu cầu này.

Trong thời gian chờ đợi, nếu có yêu cầu khẩn cấp, Quý đối tác có thể liên hệ trực tiếp qua:
Hotline ưu tiên: 1800 577 577 (miễn phí, 8:00–22:00 hàng ngày)
Email chuyên biệt: escalation@zalopay.vn

Mã tiếp nhận yêu cầu của Quý đối tác sẽ được gửi qua email đã đăng ký trong vòng 15 phút.

ZaloPay trân trọng sự tin tưởng và đồng hành của Quý đối tác."""


OUT_OF_SCOPE_RESPONSE = """Kính gửi Quý đối tác,

ZaloPay trân trọng sự quan tâm của Quý đối tác. Tuy nhiên, nội dung câu hỏi vừa gửi hiện nằm ngoài phạm vi hỗ trợ tự động của hệ thống, vốn được thiết kế để giải đáp các vấn đề thuộc 05 nhóm nghiệp vụ chính:

(1) Quy trình Onboarding và tích hợp môi trường Sandbox theo Quy định 2345
(2) Xử lý lỗi dòng tiền và cập nhật tài khoản thụ hưởng khi số dư bằng 0
(3) Tiếp nhận tra soát và hoàn tiền hàng loạt cho đối tác
(4) Kiểm soát rủi ro, khóa ví và khoanh giữ số dư khẩn cấp
(5) Đối soát phí dịch vụ định kỳ và xử lý sai lệch trạng thái giao dịch

Đối với các vấn đề nằm ngoài phạm vi trên, Quý đối tác vui lòng liên hệ bộ phận chuyên trách theo một trong các phương thức sau:

Email tổng hợp: merchant-support@zalopay.vn
Hotline hỗ trợ: 1800 577 577 (miễn phí, 8:00–22:00 hàng ngày)
Merchant Portal: merchant.zalopay.vn/support

Đội ngũ chuyên viên sẽ tiếp nhận và phản hồi yêu cầu trong vòng 01 ngày làm việc.

ZaloPay rất mong tiếp tục đồng hành cùng Quý đối tác."""
