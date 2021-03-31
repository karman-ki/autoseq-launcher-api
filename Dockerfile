# Format: FROM repository[:version]
FROM postgres:latest
COPY init.sql /docker-entrypoint-initdb.d/

FROM python:3.8
ENV app_location /usr/src
COPY . $app_location/app
WORKDIR $app_location/app
RUN pip install -r requirements.txt
EXPOSE 8100
ENTRYPOINT ["python"]
CMD ["app.py"]