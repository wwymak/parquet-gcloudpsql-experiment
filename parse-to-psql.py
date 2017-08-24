import s3fs
import fastparquet
import pandas as pd
from urllib.parse import urlparse
from sqlalchemy import create_engine
import psycopg2 as pg
import io
import boto3
import botocore
import sys
import config


bucket = 'dataen-interview-data-dev'
access_key= config.aws_access_key
secret_key= config.aws_secret_key

address='postgresql://' + config.psql_user + ':' + config.psql_password + '@localhost:3306/userlogs'
engine = create_engine(address)
connection = engine.raw_connection()

client = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)
paginator2 = client.get_paginator('list_objects_v2')

# Create a PageIterator from the Paginator
# page_iterator2 = paginator2.paginate(Bucket=bucket, Prefix='sample-data/2017-06-18/')
Prefix = sys.argv[1]
print(Prefix)
page_iterator2 = paginator2.paginate(Bucket=bucket, Prefix=Prefix)
keylist = []
for page in page_iterator2:
    keylist += page['Contents']
keys_to_parse = [x['Key'] for x in keylist if x['Size'] > 0]

def parse_file_to_df(object_key):
    s3 = s3fs.S3FileSystem(key=access_key, secret=secret_key)
    fs = s3fs.core.S3FileSystem(key=access_key, secret=secret_key)
    s3_path2 = bucket + '/' + object_key
    print(s3_path2)
    all_paths_from_s3 = fs.glob(path=s3_path2)
    myopen = s3.open
    #use s3fs as the filesystem
    fp_obj = fastparquet.ParquetFile(all_paths_from_s3,open_with=myopen)
    #convert to pandas dataframe
    df = fp_obj.to_pandas()
    print('df conversion')
    return df

def add_def_fields(df):
    def get_article_name(url):
        path_arr = urlparse(url).path.split('/')
        return path_arr[len(path_arr) -1]

    # add in the extra useful fields
    df['publicationSite'] = df['url'].apply(lambda x: urlparse(x).hostname)
    df['articleUrlName'] = df['url'].apply(lambda x: get_article_name(x))
    df['uniquePublicationId'] = df['platform'] + '-' + df['publicationId'].astype(str)
    df['uniqueArticleId'] = df['platform'] + '-' + df['articleId'].astype(str)
    print('df parsed')
    print(df.head())
    return df

def write_psql(df):
    output = io.StringIO()
    #ignore the index
    df.to_csv(output, sep='\t', header=False, index=False)
    print('to csv done')
    #jump to start of stream
    output.seek(0)
    contents = output.getvalue()

    cur = connection.cursor()
    #null values become ''
    print(cur)
    cur.copy_from(output, 'publication_logs', null="")
    connection.commit()
    cur.close()
    print('done')

print(len(keys_to_parse))
for i in range(len(keys_to_parse)):
    key = keys_to_parse[i]
    df = parse_file_to_df(key)
    df = add_def_fields(df)
    write_psql(df)
    print('done ', i)








# write to postgres on gcloud
# first open a connect to gcloud psql using ./cloud_sql_proxy -instances="data4democracy-wwymak-explore:us-central1:publications-experiment"=tcp:3306"
