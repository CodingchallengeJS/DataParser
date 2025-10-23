# Mục đích
Mục đích của chương trình này là tự động hóa chuyển hàng loạt từ file .pdf sang định dạng .txt

Parse tất cả file .pdf trong thư mục `input/` thư mục `<tên file>/output` trong thư mục này

Trong output này có quan trọng nhất là file final.md là ghép tất cả các trang

# Hướng dẫn chạy

## Chạy bằng Python

File chính ở đây là `main.py`

Đầu tiên bạn cần chắc chắn mình có jupyter được cài sẵn và cài các thư viện ban đầu:
```
python -m pip install -r requirements.txt
```
Sau đó bạn hãy chạy lệnh này để auto-parse file thành file md tổng quát:
```
python main.py
```
Output của mỗi file pdf sẽ được lưu tại `<đường dẫn file>/<tên file>/output/`

Nếu bạn muốn convert sang qti file thì bạn có thể chạy lệnh sau:
```
python convert2qti.py
```
* Chúng tôi cũng đã tạo file `run_py.bat` để tự động chạy các lệnh này

## Chạy bằng Jupyter Notebook (Dành cho mục đích phát triển)

File chính ở đây là `main.ipynb`

Đầu tiên bạn cần chắc chắn mình có jupyter được cài sẵn và cài các thư viện ban đầu:
```
python -m pip install -r requirements.txt
```

Sau đó bạn hãy chạy lệnh này để auto-parse file thành file md tổng quát:
```
jupyter nbconvert --to notebook --execute src/main.ipynb --output executed_notebook.ipynb
```
Output của mỗi file pdf sẽ được lưu tại `<đường dẫn file>/<tên file>/output/`

Nếu bạn muốn convert sang qti file thì bạn có thể chạy lệnh sau:
```
jupyter nbconvert --to notebook --execute src/QTIconvert.ipynb --output executed_notebook2.ipynb
```
* Chúng tôi cũng đã tạo file `run_ipynb.bat` để tự động chạy các lệnh này