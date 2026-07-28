# 🚀 MonoLine

MonoLine là một ứng dụng máy chủ tự động cập nhật nội dung file `README.md` trên GitHub repository dựa trên sức mạnh của AI. Thay vì phải cập nhật thủ công, dự án này hoạt động bằng cách nhận một request (trigger) từ bên ngoài theo một khoảng thời gian cố định. Sau đó, server sẽ gọi AI sinh ra nội dung mới, tự động commit và push thẳng lên GitHub.

Dự án được xây dựng hoàn toàn "data-driven" từ file cấu hình, không nhận bất kỳ payload nội dung nào từ external request để đảm bảo tính đóng gói và bảo mật cao.

---

## 🏗 Cơ chế hoạt động

1. **Trigger:** Một hệ thống bên ngoài (như cron job, webhook) gửi GET request tới route `/` của server.
2. **Rate Limiting:** Server kiểm tra trong cơ sở dữ liệu MongoDB (`time_limit`). Nếu thời gian từ lần cập nhật cuối cùng nhỏ hơn `TIME_LIMIT`, server sẽ từ chối cập nhật để tránh việc spam commit.
3. **AI Generation:** Nếu thỏa mãn điều kiện thời gian, server gọi Google GenAI API (với system prompt lấy từ file `prompts/system.prompt`) để tạo nội dung mới.
4. **Git Automation:**
   - Clone repository về thư mục tạm (`./temp`).
   - Ghi đè câu nói/nội dung mới vào `README.md`.
   - Cấu hình thông tin git với tên bot (`<username>@monoline.bot`).
   - Tạo commit với một ID (UUID) duy nhất.
   - Push lên origin.
   - Xóa thư mục tạm dọn dẹp hệ thống.
5. **Logging:** Lưu lịch sử commit (bao gồm nội dung AI sinh ra và ID) vào collection `ai_res` trong MongoDB để tiện theo dõi.

---

## ⚙️ Cấu hình hệ thống (Environment Variables)

Vì toàn bộ hệ thống MonoLine **không nhận dữ liệu từ request bên ngoài**, nên cấu hình `.env` chính là "trái tim" của dự án. Mọi hoạt động từ kết nối database, khởi tạo AI đến thao tác git đều phụ thuộc 100% vào các biến môi trường này.

Tạo một file `.env` ở thư mục gốc (root directory) và định nghĩa các biến sau:

### 1. 🌐 Server Configs
- `HOST`: Cấu hình địa chỉ IP host (Mặc định: `0.0.0.0`).
- `PORT`: Cổng chạy server Flask (Mặc định: `2011`).
- `DEBUG`: Bật/Tắt chế độ debug (`True` hoặc `False`).
- `TESTING`: Bật/Tắt chế độ testing.

### 2. 🧠 AI Configs
- `GENAI_API_KEY` **(Bắt buộc)**: API Key của hệ sinh thái Google GenAI.
- `MODEL_AI`: Tên mô hình AI được sử dụng để sinh text. Mặc định là `gemma-4-31b-it`. Có thể đổi sang các model khác như `gemini-3.1-flash-lite`. (Lưu ý: Prompt để điều khiển cách AI nói chuyện được lấy cố định từ `prompts/system.prompt`).

### 3. 🐙 GitHub Configs (Cực kỳ lưu ý bảo mật)
- `GITHUB_USERNAME` **(Bắt buộc)**: Tên đăng nhập GitHub (Nơi chứa repo cần cập nhật).
- `GITHUB_USER_TOKEN` **(Bắt buộc)**: Personal Access Token (PAT) của GitHub. **Lưu ý:** Token này cần cấp đủ quyền thao tác với repository (repo permissions) để thư viện Git có thể clone, commit và push code lên. Tuyệt đối không để lộ token này!

### 4. 🗄️ Database Configs (MongoDB)
- `MONGO_URI` **(Bắt buộc)**: Chuỗi kết nối đến MongoDB (VD: `mongodb+srv://<user>:<password>@cluster...`). Dùng để lưu trữ bộ đếm thời gian và lịch sử AI text.
- `DB_NAME`: Tên cơ sở dữ liệu sẽ sử dụng. (Mặc định: `MonoLine`).

### 5. ⏳ Time Configs
- `TIME_LIMIT`: Thời gian tối thiểu (tính bằng giây) giữa 2 lần cập nhật thành công. (Mặc định: `3600` tương đương 1 giờ). Tính năng này ngăn chặn việc endpoint bị trigger liên tục, bảo vệ tài nguyên server và tránh việc nhồi nhét commit rác lên GitHub.

---

## 🚀 Hướng dẫn triển khai (Deployment)

Nếu bạn đưa dự án này lên các nền tảng đám mây (ví dụ như **Render.com**), **hãy nhớ KHÔNG push file `.env` lên git**. Thay vào đó, bạn phải khai báo toàn bộ các biến môi trường này (đặc biệt là GITHUB_USER_TOKEN) trực tiếp ở phần **Environment Variables (Settings)** trên bảng điều khiển (Dashboard) của dịch vụ hosting.

Để duy trì vòng lặp tự động, bạn có thể thiết lập một dịch vụ cron-job (như cron-job.org) liên tục ping vào đường dẫn API chính của bạn (VD: `https://monoline.onrender.com/`) theo định kỳ (VD: 15-30 phút/lần). Hệ thống backend sẽ tự động kiểm tra biến `TIME_LIMIT` để quyết định có thực thi push code hay không.

---

## 📝 Tác giả & Giấy phép

- **Tác giả**: Lại Văn Sâm ([samvasang1192011@gmail.com](mailto:samvasang1192011@gmail.com))
- **Thời gian phát triển**: Tháng 7/2026
- **Giấy phép**: MIT License

---
