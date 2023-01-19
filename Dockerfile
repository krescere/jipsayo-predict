# 베이스 이미지
FROM python:3.9

# mariadb
RUN apt-get update
RUN apt install -y python3-pip
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
RUN apt-get install -y apt-transport-https
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get -y install libmariadb3
RUN apt-get -y install libmariadb-dev
RUN pip3 install mariadb

# 컨테이너 실행 전 수행할 쉘 명령어
RUN mkdir -p /home/predict
WORKDIR /home/predict
COPY . .
RUN pip install -r ./requirements.txt

# 컨테이너가 시작되었을 때 실행할 쉘 명렁어
# 도커파일 내 1회만 실행할 수 있음
EXPOSE 5000
CMD python -u app.py