# 🤖 MonoLine GitHub Auto-Updater

Dự án này là một hệ thống tự động cập nhật nội dung file `README.md` trên GitHub, sử dụng sức mạnh của Google Gemini AI. 
Hệ thống được thiết kế dưới dạng một server API (Flask). Ứng dụng hoạt động theo cơ chế nhận các HTTP request định kỳ từ bên ngoài (ví dụ: cron job mỗi giờ), sau đó gọi AI để sinh ra một nội dung mới và tự động commit, push thẳng lên repository GitHub của bạn.

---

## ⚙️ Nguồn cấu hình duy nhất: Biến Môi Trường (`.env`)

Toàn bộ ứng dụng được điều khiển thông qua các biến môi trường được định nghĩa bằng `pydantic-settings`. Đây là **nguồn thông tin duy nhất** bạn cần cấu hình trước khi chạy hệ thống.

Bạn cần tạo một file `.env` ở thư mục gốc của dự án và điền đầy đủ các thông tin sau:

| Biến | Bắt buộc | Giải thích chi tiết | Mặc định |
|---|:---:|---|---|
| `HOST` | Trống | Địa chỉ IP để bind server. | `0.0.0.0` |
| `PORT` | Trống | Cổng mạng cho ứng dụng Flask chạy. | `2011` |
| `DEBUG` | Trống | Chế độ debug của Flask (`True` hoặc `False`). | `False` |
| `GENAI_API_KEY` | **Có** | Khóa API của Google Gemini để tạo text từ AI. | - |
| `MODEL_AI` | Trống | Tên model AI muốn sử dụng (Khuyến nghị: `gemini-1.5-flash-lite`). | `gemma-4-31b-it` |
| `GITHUB_USERNAME` | **Có** | Tên tài khoản GitHub chứa repository bạn muốn auto-update. | - |
| `GITHUB_USER_TOKEN` | **Có** | Personal Access Token (PAT) có quyền `repo` để thực hiện push code. | - |
| `MONGO_URI` | **Có** | Chuỗi kết nối (URI) đến database MongoDB của bạn. | - |
| `DB_NAME` | Trống | Tên cơ sở dữ liệu trên MongoDB để lưu trữ dữ liệu. | `MonoLine` |
| `TIME_LIMIT` | Trống | Giới hạn thời gian (rate limit) tối thiểu giữa các lần cập nhật (tính bằng giây). | `3600` (1 giờ) |

*⚠️ Lưu ý: Tuyệt đối không commit file `.env` lên GitHub để tránh lộ API Key và Token!*

---

## 🚀 Luồng hoạt động chính (App Logic)

Ứng dụng được thiết kế tối ưu và chặt chẽ qua các bước sau:

1. **Trigger từ bên ngoài:** Một hệ thống (như Cron job, GitHub Actions, hoặc cron-job.org) sẽ gọi vào endpoint của server mỗi giờ một lần.
2. **Kiểm tra giới hạn thời gian (Rate Limiting):** Server sẽ query vào collection `time_limit` trên MongoDB. Nếu thời gian kể từ lần update trước chưa vượt quá `TIME_LIMIT` (3600 giây), yêu cầu sẽ bị từ chối để tránh spam request lên API và GitHub.
3. **AI Generate:** Server kết nối tới GenAI thông qua `GENAI_API_KEY`, sử dụng file prompt `prompts/system.prompt` để yêu cầu AI sinh ra một đoạn văn bản mới.
4. **Git Auto Update (Xử lý chuỗi):** 
   - Hệ thống dùng `GitPython` để clone repository của bạn về thư mục `./temp`.
   - Đọc file `README.md` và dùng Regex để tìm kiếm vùng kẹp giữa `<!--start--->` và `<!--end--->`.
   - Ghi đè đoạn văn bản AI vừa tạo vào vùng này.
5. **Commit & Push:** Bot tự động gán tên hiển thị, email dạng `@monoline.bot`, tạo commit với một mã UUID duy nhất và push ngược lên branch chính. Sau đó dọn dẹp thư mục tạm.
6. **Lưu lịch sử:** Thông tin của lần tạo thành công (bao gồm commit ID, văn bản AI, thời gian) được lưu lại vào MongoDB (`db.ai_res`).

---

## 🛠 Hướng dẫn Cài đặt & Khởi chạy (Fedora Linux)

Để chạy dự án, hệ thống cần cài đặt Python, Git và MongoDB. Dưới đây là các lệnh thiết lập trên môi trường Fedora:

**1. Cài đặt các gói phụ thuộc hệ thống:**
```bash
sudo dnf update
sudo dnf install python3 python3-pip python3-virtualenv git mongodb-server
```

**2. Bật dịch vụ MongoDB:**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**3. Clone repo và thiết lập môi trường ảo:**
```bash
git clone https://github.com/laivansam11920/MonoLine.git
cd MonoLine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Thiết lập File Mục tiêu trên GitHub:**
Bạn **BẮT BUỘC** phải chèn hai đoạn thẻ HTML sau vào bất kỳ đâu trong file `README.md` trên repo GitHub của bạn. AI sẽ chỉ ghi đè vào khoảng giữa 2 thẻ này:
```markdown
<!--start--->
Nội dung này sẽ bị AI ghi đè ở lần chạy đầu tiên.
<!--end--->
```

**5. Khởi chạy Server:**
```bash
python3 run.py 
# (hoặc tên file entrypoint chứa app.run của Flask)
```
Sau đó, thiết lập một cron job trên Fedora để tự động trigger server:
```bash
crontab -e
# Thêm dòng sau để gửi request mỗi giờ:
# 0 * * * * curl http://localhost:2011/duong-dan-trigger
```

---

## 📝 Tác giả & Giấy phép

- **Tác giả**: Lại Văn Sâm ([samvasang1192011@gmail.com](mailto:samvasang1192011@gmail.com))
- **Thời gian phát triển**: Tháng 7/2026
- **Giấy phép**: MIT License

---
