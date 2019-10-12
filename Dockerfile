FROM python:3.6.5-jessie

COPY requirements.txt requirements.txt
COPY /data /data

RUN pip install --no-cache-dir -r requirements.txt --default-timeout=1000

COPY data_wrangling.py data_wrangling.py
COPY run_website.py run_website.py

EXPOSE 5000

CMD ["python","run_website.py"]

