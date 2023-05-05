import os
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import re
import logging
import argparse

"""
Data download script for YFinance tickers.
Usage: Change directory to E:\ak_mlops-az-gh>cd jobs and then execute the following commands   
python data_download.py --ticker WIPRO.NS --start 366 --end 1
"""

DATA_DIR = "../data"
JOBS_DIR = "../jobs"
LOGS_DIR = "../logs" 

#create data, jobs, and log directory 
for dir in [DATA_DIR, JOBS_DIR, LOGS_DIR]:
    os.makedirs(dir, exist_ok=True)


logging.basicConfig(
    filename= f"{LOGS_DIR}/data_download.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

def to_date(days: int)->str:
    return str(datetime.today().date()-timedelta(days=days))


if __name__ == "__main__":
    ap =argparse.ArgumentParser()
    ap.add_argument("-t", "--ticker", required=True, help="Ticker Name")
    ap.add_argument("-s", "--start", required=True, type=int,  help="Number of days of data to download 366, 200, etc")
    ap.add_argument("-e", "--end", required=True, type=int, help="how many days back you need to download the data e.g. 1,2,3 ")
    args = vars(ap.parse_args())

    ticker = args['ticker']
    start = to_date(args['start'])
    end= to_date(args['end'])

    logging.info('Downloading data...')
    data = yf.download(ticker, start=start, end=end, period = '1d')
    logging.info("Downloaded the data...")

    data["Date"] = [str(x)[:10] for x in data.index]
    data = data["Close"]
    logging.debug(f"Total rows: {data.shape[0]}")

    path = f'{DATA_DIR}/{ticker}.csv'
    data.to_csv(path, index = True)

    tags={
        'Length':   len(data),
        'Start':    str(data.index[0].date()),
        'End':      str(data.index[-1].date()),
        'Median':   np.round(data.median(), 2),
        'SD':       np.round(data.std(), 2)
    }
    logging.debug(f"Tags: {tags}")
    name=ticker[:ticker.index('.')]
    version=re.sub('-', '', str(datetime.today().date()))
    description=f"Stock data for {ticker} during {tags['Start']}:{tags['End']} in 1d interval."
    path=path
    tags=tags

    with open(f"{JOBS_DIR}/data_upload.yml", "w") as f:
        f.write(
        f"""
            $schema: https://azuremlschemas.azureedge.net/latest/data.schema.json
            type: uri_file
            name: '{name}'
            description: {description}
            path: '{path}'
            tags: {tags}
            version: {version}
        """)
        print("completed")
        logging.info(f"YAML file saved to {JOBS_DIR}/data_upload.yml") 