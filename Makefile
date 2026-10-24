install:
	pip install -r requirements.txt

data:
	python scripts/download_data.py

demo:
	python scripts/download_data.py demo

run:
	streamlit run app.py
