import os
from dateutil.parser import parse
import urllib

import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError


def lambda_handler(event=None, context=None):

    def query_usi(start_date: str, end_date: str, freq_days: str):
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
        # df = df.rename({"Longitude": "lon", "Latitude": "lat"}, axis=1)
        df.columns = [x.lower() for x in df.columns]
        df = df.dropna(subset=['iceberg', 'longitude', 'latitude', 'date'])

        # Drops problematic icebergs marked with a star
        df = df[~df["iceberg"].str.contains("*", regex=False, na=False)]

        # gdf = gpd.GeoDataFrame(
        #     df, geometry=gpd.points_from_xy(df["lon"], df["lat"], crs="EPSG:4326")
        # )
        return df

    def upload_to_aws(local_file, s3_file):
        s3 = boto3.client('s3')

        try:
            s3.upload_file(local_file, os.environ['BUCKET_NAME'], s3_file, ExtraArgs={'ACL':'public-read'}) #
            # requires acl for bucket enabled.
            # and ima role required s3 > s3:PutObject, GetObjectAcl, PutObjectAcl

            # url = s3.generate_presigned_url(
            #     ClientMethod='get_object',
            #     Params={
            #         'Bucket': os.environ['BUCKET_NAME'],
            #         'Key': s3_file
            #     },
            #     ExpiresIn=24 * 3600
            # )
            url = None
            print("Upload Successful", url)
            return url
        except FileNotFoundError:
            print("The file was not found")
            return None
        except NoCredentialsError:
            print("Credentials not available")
            return None

    def is_aws_env():
        return os.environ.get('AWS_LAMBDA_FUNCTION_NAME')

    # def most_recent_date_on_s3():
    #     s3_file = "https://usi-icebergs.s3.eu-central-1.amazonaws.com/icebergs_locations_usi.csv"
    #     most_recent_date = pd.read_csv(s3_file).iloc[-1]["date"]

    start_date = "2014-10-01"
    end_date = "2022-12-10"
    fname = f"icebergs_locations_usi.csv"#f"usi_{start_date}_{end_date}.csv"

    df = query_usi(start_date, end_date, "1d")
    df = format_usi(df)

    if is_aws_env():
        df.to_csv("/tmp/" + fname)
        url = upload_to_aws(local_file="/tmp/" + fname, s3_file=fname)
    else:
        url = "local"
        df.to_csv(fname)

    print("shape df", df.shape[0])

    return {
        'statusCode': 200,
        'body': {"url": url, "df_len": df.shape[0]}
    }


if __name__ == "__main__":
    lambda_handler()