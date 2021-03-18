  
import boto3
from botocore.exceptions import ClientError
import pymysql

import json
import os

def init(event, context):

    db_secret_name = os.environ.get('db_secret')
    S3_BUCKET_NAME = os.environ.get('s3_bucket_name')

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        secret_response = client.get_secret_value(SecretId=db_secret_name)
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
            cursor.execute("drop database if exists test;")
            cursor.execute("create database if not exists test;")
            cursor.execute("""
                create table `test`.`test`(
                    `c1` varchar(255) default null,
                    `c2` varchar(255) default null,
                    `c3` varchar(255) default null,
                    key `k1`(`c1`),
                    key `k2`(`c2`)
                );
            """)
            conn.commit()

            rows_affected = cursor.execute("insert into `test`.`test` values(uuid(),uuid(),uuid());")
            conn.commit()
            print(f"OK, {rows_affected} rows affected")

            NUM_OF_TEST = 23
            while NUM_OF_TEST:
                rows_affected = cursor.execute("insert into `test`.`test` select * from `test`.`test`;")
                conn.commit()
                print(f"OK, {rows_affected} rows affected")

                NUM_OF_TEST = NUM_OF_TEST -1

            cursor.execute(f"""
                SELECT * FROM test.test limit 9868950 INTO OUTFILE S3 's3://{S3_BUCKET_NAME}/dummy-data'
                FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' OVERWRITE ON;
            """)
            print("Complete load dummy data")
            
            cursor.close()