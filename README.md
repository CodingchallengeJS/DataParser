## Mục đích
Parse tất cả file pdf trong thư mục yêu cầu, sẽ output ra thư mục `<tên file>/output` ở trong thư mục yêu cầu đấy

Trong output này có quan trọng nhất là file final.md là ghép tất cả các trang

## Hướng dẫn chạy
File chính ở đây là `main.ipynb`
Đầu tiên bạn cần chắc chắn mình có jupyter được cài sẵn và cài các thư viện ban đầu:
`python -m pip install requirements.txt`
Sau đó bạn hãy chạy lệnh này để auto-parse file thành file md tổng quát:
`jupyter nbconvert --to notebook --execute main.ipynb --output executed_notebook.ipynb`
Output của mỗi file pdf sẽ được lưu tại `<đường dẫn file>/<tên file>/output/`
Nếu bạn muốn convert sang qti file thì bạn có thể chạy lệnh sau:
`jupyter nbconvert --to notebook --execute QTIconvert.ipynb --output executed_notebook2.ipynb`