import pandas as pd
import matplotlib.pyplot as plt
import boto3

s3 = boto3.client('s3')
s3.download_file('lab2-inmyuni', 'exchange_2022.csv', 'exchange_2022.csv')

df = pd.read_csv("exchange_2022.csv")
df['date'] = pd.to_datetime(df['date'])

plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['USD'], label='USD', color='blue')
plt.plot(df['date'], df['EUR'], label='EUR', color='green')
plt.title('Курс гривні до долара та євро (2022)')
plt.xlabel('Дата')
plt.ylabel('Курс')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('currency_graph.png')
plt.show()

s3.upload_file('lab2-inmyuni', 'currenvy_graph.png')
