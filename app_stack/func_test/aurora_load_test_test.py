  
import boto3
from botocore.exceptions import ClientError
import pymysql

import json
import os

def test(event, context):

    DB_SECRET_NAME = os.environ.get('db_secret')
    S3_BUCKET_NAME = os.environ.get('s3_bucket_name')

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        secret_response = client.get_secret_value(SecretId=DB_SECRET_NAME)
    except ClientError as e:
        print(e.response)
        print(e.response['Error']['Code'])
    else:
        if 'SecretString' in secret_response:
            secret_data = json.loads(secret_response['SecretString'])
            print("connecting aurora-mysql...")
            print("host: %s"%secret_data['host'])
            print("user: %s"%secret_data['username'])

            conn = pymysql.connect(
                user=secret_data['username'],
                passwd=secret_data['password'],
                host=secret_data['host'],
                db='mysql',
                charset='utf8'
            )

            cursor = conn.cursor()

            cursor.execute("""
                drop table if exists `test`.`test_load`;
            """)

            cursor.execute("""
                create table `test`.`test_load`(
                    `c1` varchar(255) default null,
                    `c2` varchar(255) default null,
                    `c3` varchar(255) default null,
                    key `k1`(`c1`),
                    key `k2`(`c2`)
                );
            """)

            result =cursor.execute(f"""
                LOAD DATA FROM S3 's3://{S3_BUCKET_NAME}/dummy-data.part_00000'
                INTO TABLE `test`.`test_load`
                FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'
                (c1, c2, c3);;
            """)
            print(f"OK, {result} rows affected")

            cursor.close()