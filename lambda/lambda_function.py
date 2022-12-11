import os
from dateutil.parser import parse
import urllib

import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError


def lambda_handler(event=None, context=None):

    def is_aws_env():
        return os.environ.get('AWS_LAMBDA_FUNCTION_NAME')

    def upload_to_s3(local_file, s3_file):
        s3 = boto3.client('s3')
        s3.upload_file(local_file, os.environ['BUCKET_NAME'], s3_file, ExtraArgs={'ACL':'public-read'})

    def query_icebergs_usi(start_date: str, end_date: str, freq_days: str):
        """
        Query US national ice center - Antarctic Iceberg Data - Archive
        https://usicecenter.gov/Products/AntarcIcebergs
        """
        usi_url = "https://usicecenter.gov/File/DownloadProduct?products=%2Ficeberg%2F{}&fName=AntarcticIcebergs_{}.csv"

        datelist = pd.date_range(
            start=parse(start_date), end=parse(end_date), freq=freq_days
        ).tolist()

        df_all = []
        for date in datelist:
            csv_link = usi_url.format(date.strftime("%Y"), date.strftime("%Y%m%d"))
            try:
                df = pd.read_csv(csv_link)
                df["date"] = date
            except (urllib.error.HTTPError, TimeoutError, urllib.error.URLError):
                continue
            except pd.errors.ParserError:
                print("ParserError", date)
                continue
            df_all.append(df)

        df_all = pd.concat(df_all, ignore_index=True)
        return df_all

    def format_usi(df):
        df = df.drop(["Remarks", "Last Update"], axis=1)
        df.columns = [x.lower() for x in df.columns]
        df = df.dropna(subset=['iceberg', 'longitude', 'latitude', 'date'])

        # Drops problematic icebergs marked with a star
        df = df[~df["iceberg"].str.contains("*", regex=False, na=False)]
        return df

    # def most_recent_date_on_s3():
    #     s3_file = "https://usi-icebergs.s3.eu-central-1.amazonaws.com/icebergs_locations_usi.csv"
    #     most_recent_date = pd.read_csv(s3_file).iloc[-1]["date"]

    start_date = "2014-10-01"
    end_date = "2022-12-10"
    fname = f"icebergs_locations_usi.csv"

    df = query_icebergs_usi(start_date, end_date, "1d")
    df = format_usi(df)

    if is_aws_env():
        df.to_csv("/tmp/" + fname)
        upload_to_s3(local_file="/tmp/" + fname, s3_file=fname)
    else:
        df.to_csv(fname)
    print("shape df", df.shape[0])

    return {
        'statusCode': 200,
        'body': {"df_len": df.shape[0]}
    }


if __name__ == "__main__":
    lambda_handler()