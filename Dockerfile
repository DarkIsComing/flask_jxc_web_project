#flask_web
FROM python:3.6
LABEL author="ZhaoTengWei"


WORKDIR /app


COPY . /app
RUN pip3 install flask flask_sqlalchemy pymysql flask_wtf flask_bootstrap pandas
RUN pip3 install gunicorn

EXPOSE 5000
CMD ["gunicorn","-w 2","-b 0.0.0.0:5000","manage:app"]