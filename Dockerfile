FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini ./pytest.ini

EXPOSE 8050

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "1", "--timeout", "120", "app.main:server"]