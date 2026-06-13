FROM python:3.12-slim
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest uvicorn

EXPOSE 8000

ARG MODE=app
CMD ["sh", "-c", "if [ \"$MODE\" = \"test\" ]; then pytest --maxfail=1 --disable-warnings -q; else uvicorn main:app --host 0.0.0.0 --port 8000; fi"]