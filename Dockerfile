FROM python:3.10
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8090
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8090"]
# CMD ["python", "./app.py"]