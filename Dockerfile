FROM 3.13.16-slim-bookworm

ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip setuptools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]