# Mục đích
Mục đích của chương trình này là tự động hóa chuyển hàng loạt file .pdf sang file định dạng .txt

Parse tất cả file .pdf trong thư mục `input/` và xuất kết quả ra thư mục `<tên file>/output` trong thư mục này

Trong thư mục output này, file final.md là ghép tất cả các trang

# Hướng dẫn chạy

* *Để tự động hóa, chúng tôi đã tạo file `run_py.bat` cho phiên bản python(chính) và `run_ipynb` cho phiên bản jupyter notebook(mục đích nghiên cứu) để tự động chạy chương trình. Nếu bạn muốn chạy thủ công thì hãy đọc tiếp phần dưới đây.*

Đầu tiên bạn cần chắc chắn mình đã cài đầy đủ các thư viện cần thiết, do đó hãy chạy lệnh này:
```
python -m pip install -r requirements.txt
```

## Chạy bằng Python

File chính ở đây là `main.py`

Sau đó bạn hãy chạy lệnh này để auto-parse file .pdf thành file .md tổng quát:
```
python main.py
```
Output của mỗi file pdf sẽ được lưu tại `<đường dẫn file>/<tên file>/output/`

Nếu bạn muốn convert sang qti file thì bạn có thể chạy lệnh sau:
```
python convert2qti.py
```

## Chạy bằng Jupyter Notebook (Dành cho mục đích phát triển)

File chính ở đây là `main.ipynb`

Sau đó bạn hãy chạy lệnh này để auto-parse file .pdf thành file .md tổng quát:
```
jupyter nbconvert --to notebook --execute src/main.ipynb --output executed_notebook.ipynb
```
Output của mỗi file pdf sẽ được lưu tại `<đường dẫn file>/<tên file>/output/`

Nếu bạn muốn convert sang qti file thì bạn có thể chạy lệnh sau:
```
jupyter nbconvert --to notebook --execute src/QTIconvert.ipynb --output executed_notebook2.ipynb
```

# Cách hoạt động của chương trình
Upload lần lượt các file .pdf trong thư mục `input/` lên máy chủ ![OCR](https://dotsocr.xiaohongshu.com) online

Download file zip kết quả của mỗi file xuống lần lượt các thư mục cùng tên với file

Giải nén file zip

Ghép lại file các trang thành một file mang tên final.md

Chương trình dựa theo các bước cơ bản này mà bắt đầu thực hiện tự động hóa, xử lý hàng loạt file pdf một cách tự động.
