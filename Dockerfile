FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/app
RUN apt-get update \
&& apt-get install -y --n0-install-recommends gcc libpq-dev \
&& apt-get purge -y --auto-remove -o APT::Autoremove::recommendsImportant=false \
&& rm -rf /var/lib/apt/lists/*
COPY requirements.txt/usr/src/app/
RUN pip install --upgrade pip \
  && pip install install -r requirements.txt
COPY. /usr/src/app/
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn","--bind", "0.0.0.0:8000", "socialmedia.wsgi:application"]
