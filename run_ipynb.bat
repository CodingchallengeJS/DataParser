cd src/ipynb
python -m pip install -r requirements.txt
jupyter nbconvert --to notebook --execute main.ipynb --output main_out.ipynb
::jupyter nbconvert --to notebook --execute QTIconvert.ipynb --output QTIconvert_out.ipynb