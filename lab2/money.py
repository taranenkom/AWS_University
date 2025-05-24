import requests
import json
from datetime import datetime, timedelta
import boto3

s3 = boto3.client('s3')

def fetch_usd_eur_rates_for_2022():
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    delta = timedelta(days=1)
    result = []

    while start_date <= end_date:
        date_str = start_date.strftime("%Y%m%d")
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&date={date_str}&json"
        usd_resp = requests.get(url).json()

        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=EUR&date={date_str}&json"
        eur_resp = requests.get(url).json()

        try:
            usd_rate = usd_resp[0]['rate']
            eur_rate = eur_resp[0]['rate']
            result.append({
                'date': start_date.strftime('%Y-%m-%d'),
                'USD': usd_rate,
                'EUR': eur_rate
            })
        except Exception:
            pass 
        
        start_date += delta

    with open("exchange_2022.csv", "w") as f:
        f.write("date,USD,EUR\n")
        for row in result:
            f.write(f"{row['date']},{row['USD']},{row['EUR']}\n")

if __name__ == "__main__":
    fetch_usd_eur_rates_for_2022()

    s3.upload_file('exchange_2022.csv', 'lab2-inmyuni', 'exchange_2022.csv')
