aws_db = {
    "user": "jipsayo",
    "password": "12345678",
    "host": "jipsayo-database.cz5bmx4ermfu.ap-northeast-2.rds.amazonaws.com",
    "port": "3306", # Maria DB의 포트
    "database": "jipsayo",
}

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = f"mariadb+mariadbconnector://{aws_db['user']}:{aws_db['password']}@{aws_db['host']}:{aws_db['port']}/{aws_db['database']}?charset=utf8"