# 💸 ỨNG DỤNG QUẢN LÝ VÀ CHIA TIỀN NHÓM
*Đồ án môn Kỹ thuật lập trình - Khoa Hệ thống Thông tin*
## 👨‍💻 Thành viên phát triển
1. Nguyễn Phạm Hồng Thương - K254161804
2. Nguyễn Ngọc Trúc Giang - K254161759
3. Nguyễn Nam Phương - K254161790
4. Bùi Lê Khánh Như - K254161786
5. Võ Thị Yến Nhi - K254161784
## 📖 Giới thiệu
Đây là ứng dụng Desktop được phát triển bằng Python và PyQt6 nhằm mục đích tự động hóa quá trình quản lý chi tiêu nhóm, giải quyết bài toán "ai nợ ai bao nhiêu" một cách nhanh chóng, minh bạch sau các chuyến du lịch, ăn uống.

## 🚀 Tính năng nổi bật
- **Quản lý thu chi trực quan:** Thêm thành viên, ghi nhận khoản chi và thanh toán với vài thao tác.
- **Thuật toán tối ưu hóa nợ:** Sử dụng thuật toán tham lam (Greedy) để rút gọn các khoản nợ chéo, giảm thiểu số vòng chuyển khoản.
- **Trợ lý ảo AI:** Truy vấn thông tin chi tiêu bằng câu lệnh nhanh gọn.
- **Xuất báo cáo:** Hỗ trợ kết xuất hóa đơn lưu trữ bằng định dạng PDF và thống kê chi tiết bằng tệp Text.
- **Giao diện hiện đại:** Được xây dựng theo kiến trúc Single-Page Application mượt mà bằng QStackedWidget.

## 🛠 Nền tảng và Công nghệ sử dụng
- **Ngôn ngữ:** Python 3.17
- **Giao diện (GUI):** PyQt6 & Qt Designer
- **Cấu trúc lưu trữ:** Object-Oriented Programming (In-Memory RAM)
- **Thư viện tích hợp:** `datetime`, `random`, `PyQt6.QtPrintSupport`

## ⚙️ Hướng dẫn cài đặt và chạy ứng dụng
1. Đảm bảo máy tính đã cài đặt Python.
2. Cài đặt thư viện PyQt6 thông qua terminal:
   ```bash
   pip install PyQt6
