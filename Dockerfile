# 베이스 이미지
FROM python:3.9.0

# pip 설치
RUN apt-get update && apt-get install -y python3-pip

# for mariadb
RUN apt-get update && apt-get -y install libmariadb3 libmariadb-dev

# 컨테이너 실행 전 수행할 쉘 명령어
RUN mkdir -p /home/predict
WORKDIR /home/predict
COPY . .
RUN pip3 install -r ./requirements.txt

# 컨테이너가 시작되었을 때 실행할 쉘 명렁어
# 도커파일 내 1회만 실행할 수 있음
EXPOSE 5000
CMD python -u app.py