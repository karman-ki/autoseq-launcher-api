# Format: FROM repository[:version]

FROM python:3.8
ENV app_location /usr/src
COPY . $app_location/app
WORKDIR $app_location/app
RUN pip install -r requirements.txt
EXPOSE 8100
ENTRYPOINT ["python"]
CMD ["app.py"]