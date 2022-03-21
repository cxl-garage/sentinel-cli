FROM python:3

COPY app.py /
COPY requirements.txt /

RUN pip install -r /requirements.txt

EXPOSE 8050
CMD ["python", "app.py"]