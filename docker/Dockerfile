# Build command : docker build --tag junnsorran/comic-back --file .\docker\Dockerfile .
FROM python:3.11
WORKDIR /comic-back
COPY requirements.txt /comic-back/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /comic-back/requirements.txt
COPY ./app /comic-back/app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","80"]