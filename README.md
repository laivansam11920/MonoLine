# 🤖 MonoLine GitHub Auto-Updater

Dự án này là một hệ thống tự động cập nhật nội dung file `README.md` trên GitHub, sử dụng sức mạnh của Google Gemini AI. 
Hệ thống được thiết kế dưới dạng một server API (Flask). Ứng dụng hoạt động theo cơ chế nhận các HTTP request định kỳ từ bên ngoài (ví dụ: cron job mỗi giờ), sau đó gọi AI để sinh ra một nội dung mới và tự động commit, push thẳng lên repository GitHub của bạn.

---

## ⚙️ Nguồn cấu hình duy nhất: Biến Môi Trường (`.env`)

Toàn bộ ứng dụng được điều khiển thông qua các biến môi trường được định nghĩa bằng `pydantic-settings`. Đây là **nguồn thông tin duy nhất** bạn cần cấu hình trước khi chạy hệ thống. Không hardcode bất kỳ giá trị nào vào mã nguồn!

Bạn cần tạo một file `.env` ở thư mục gốc của dự án và điền đầy đủ các thông tin sau:

| Biến | Bắt buộc | Giải thích chi tiết | Mặc định |
|---|:---:|---|---|
| `HOST` | | Địa chỉ IP để bind server. Thường để `0.0.0.0` để có thể nhận request từ bên ngoài. | `0.0.0.0` |
| `PORT` | | Cổng mạng cho ứng dụng Flask chạy. | `2011` |
| `DEBUG` | | Chế độ debug của Flask (`True` hoặc `False`). Chỉ nên bật khi đang code. | `False` |
| `GENAI_API_KEY` | **Có** | Khóa API của Google Gemini để tạo text. Lấy từ Google AI Studio. | - |
| `MODEL_AI` | | Tên model AI muốn sử dụng (Khuyến nghị: `gemini-1.5-flash-lite`). | `gemma-4-31b-it` |
| `GITHUB_USERNAME` | **Có** | Tên định danh (username) tài khoản GitHub của bạn. Hệ thống dùng tên này để tạo link clone và gán tên tác giả vào lịch sử commit. | - |
| `GITHUB_USER_TOKEN` | **Có** | **Personal Access Token (PAT)**. Đây không phải mật khẩu tài khoản! Đó là một mã thông báo bảo mật do GitHub cấp phát để ứng dụng (hoặc script) có quyền truy cập repo của bạn qua API mà không cần đăng nhập trực tiếp. *Cách lấy:* Vào GitHub -> Settings -> Developer settings -> Personal access tokens. **Lưu ý quan trọng:** Bắt buộc phải cấp quyền `repo` (Full control of private/public repositories) thì code này mới push nội dung lên kho lưu trữ được. | - |
| `MONGO_URI` | **Có** | Chuỗi kết nối (URI) đến **MongoDB Cloud** (ví dụ: MongoDB Atlas). Hệ thống được tối ưu để không cần cài database nặng nề dưới máy cục bộ. Bạn chỉ cần tạo 1 cụm (cluster) online, lấy chuỗi URL kết nối dạng `mongodb+srv://<user>:<password>@cluster...` và dán vào đây là hệ thống tự kết nối và quản lý. | - |
| `DB_NAME` | | Tên cơ sở dữ liệu sẽ được tạo trên MongoDB Cloud để lưu trữ thông tin log và giới hạn thời gian. | `MonoLine` |
| `TIME_LIMIT` | | Giới hạn thời gian (rate limit) tối thiểu giữa các lần cập nhật (tính bằng giây). | `3600` (1 giờ) |

*⚠️ Lưu ý: Tuyệt đối không commit file `.env` lên GitHub để tránh lộ API Key và Token!*

---

## 🚀 Luồng hoạt động chính (App Logic)

Ứng dụng được thiết kế tối ưu và chặt chẽ qua các bước sau:

1. **Trigger từ bên ngoài:** Một hệ thống (như Cron job trên Linux, hoặc các dịch vụ trigger API miễn phí) sẽ gọi vào endpoint của server theo chu kỳ.
2. **Kiểm tra giới hạn thời gian (Rate Limiting):** Server sẽ đối chiếu dữ liệu trong MongoDB Cloud. Nếu khoảng thời gian từ lần chạy trước đến hiện tại chưa vượt quá `TIME_LIMIT` (3600 giây), yêu cầu sẽ bị từ chối để tránh spam request làm treo bot và bị GitHub khóa.
3. **AI Generate:** Server kết nối tới GenAI, truyền Prompt hệ thống để yêu cầu AI sinh ra một đoạn văn bản mới.
4. **Git Auto Update (Xử lý chuỗi):** 
   - Bot sử dụng thư viện `GitPython` kết hợp `GITHUB_USER_TOKEN` để clone repository của bạn về thư mục `./temp`.
   - Đọc file `README.md` và dùng Biểu thức chính quy (Regex) để tìm kiếm vùng cần cập nhật nội dung, giới hạn bởi 2 thẻ `<!--start--->` và `<!--end--->`.
   - Thay thế toàn bộ nội dung cũ ở giữa bằng đoạn văn bản AI vừa sinh ra.
5. **Commit & Push:** Bot tự động gán tên người commit là `GITHUB_USERNAME`, email dạng `@monoline.bot`, đính kèm một mã UUID vào mô tả commit để đảm bảo tính duy nhất, sau đó push ngược code lên GitHub. Cuối cùng, thư mục `./temp` sẽ bị xóa để giải phóng bộ nhớ.
6. **Lưu lịch sử:** Toàn bộ thông tin của phiên làm việc (Commit ID, nội dung sinh ra, mốc thời gian) được đẩy lên MongoDB Cloud để bạn tiện theo dõi sau này.

---

## 🛠 Hướng dẫn Cài đặt & Khởi chạy (Trên hệ điều hành Fedora)

Do đã sử dụng MongoDB trên Cloud, việc cài đặt môi trường giờ đây vô cùng nhanh gọn. Ông chỉ cần chuẩn bị Python và Git là đủ.

**1. Cài đặt các gói cơ bản:**
```bash
sudo dnf update
sudo dnf install python3 python3-pip python3-virtualenv git
```

**2. Tải mã nguồn và tạo môi trường ảo:**
```bash
git clone https://github.com/laivansam11920/MonoLine.git
cd MonoLine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Thiết lập cọc mốc trên GitHub:**
Để công cụ hoạt động đúng chỗ, ông **BẮT BUỘC** phải chèn hai thẻ HTML sau vào file `README.md` trên kho lưu trữ GitHub của mình. 
```markdown
<!--start-->
Nội dung ở đây sẽ tự động bị thay thế.
<!--end-->
```

**4. Khởi chạy Server:**
(Đừng quên điền thông tin vào file `.env` trước nhé).
```bash
python3 run.py 
```

**5. Hẹn giờ tự động chạy (Cron job):**
Trên Fedora, ông có thể dùng crontab để bot tự động gửi request kích hoạt mỗi giờ:
```bash
crontab -e
# Thêm dòng này để gọi server API cục bộ mỗi giờ:
# 0 * * * * curl http://localhost:2011/
```

---

## 📝 Tác giả & Giấy phép

- **Tác giả**: Lại Văn Sâm ([samvasang1192011@gmail.com](mailto:samvasang1192011@gmail.com))
- **Thời gian phát triển**: Tháng 7/2026
- **Giấy phép**: MIT License

---
