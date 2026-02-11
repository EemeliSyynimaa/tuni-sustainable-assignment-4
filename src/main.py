import requests
import api
import matplotlib.pyplot as plt

from matplotlib.dates import ConciseDateFormatter
from datetime import date, datetime
from argparse import ArgumentParser

def fetch_data(start, end):
    headers = {'x-api-key': api.key}
    response = requests.get(f'https://data.fingrid.fi/api/data?datasets=74,124,396&startTime={start}&endTime={end}&pageSize=20000&oneRowPerTimePeriod=true&locale=fi', headers)

    response.raise_for_status()

    return response.json()['data']

def process_data(data):
    result = {}

    for item in data:
        production = item['Sähköntuotanto Suomessa']
        consumption = item['Sähkönkulutus Suomessa']
        emission = item['Suomessa kulutetun sähkön päästökerroin - päivitys 15 minuutin välein']
        date = item['startTime'][:10]

        temp = result.setdefault(date, {})
        temp.setdefault('production', []).append(production)
        temp.setdefault('consumption', []).append(consumption)
        temp.setdefault('emission', []).append(emission)

    return result

def average(data):
    total = 0
    count = len(data)
    for value in data:
        if value != None:
            total += value

    return total / count

def calculate_averages(data):
    result = {}

    for date in data:
        result.setdefault('date', []).append(datetime(int(date[:4]), int(date[5:7]), int(date[8:10])))

        for meter in data[date]:
            result.setdefault(meter, []).append(average(data[date][meter]))

    return result

def plot(data):
    fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(10, 10))
    ax1.set_xlabel('Date')
    ax1.set_ylabel('MWh/h')
    ax1.set_title('Electricity production and consumption in Finland')
    ax1.plot(result['date'], result['production'], label='production')
    ax1.plot(result['date'], result['consumption'], label='consumption'),
    ax1.xaxis.set_major_formatter(ConciseDateFormatter(ax1.xaxis.get_major_locator()))
    ax1.legend()

    ax2.set_xlabel('Date')
    ax2.set_ylabel('gCO2/kWh')
    ax2.set_title('Emission factor for electricity consumed in Finland')
    ax2.plot(result['date'], result['emission'], label='emission')
    ax2.xaxis.set_major_formatter(ConciseDateFormatter(ax2.xaxis.get_major_locator()))
    ax2.legend()

    plt.show()


def is_valid_date(date):
    bool(datetime.strptime(date, '%Y-%m-%d'))

try:
    parser = ArgumentParser()
    parser.add_argument('start', help='Start date in the format YYYY-MM-DD')
    parser.add_argument('end', help='End date in the format YYYY-MM-DD')

    args = parser.parse_args()

    is_valid_date(args.start)
    is_valid_date(args.end)

    data = fetch_data(args.start, args.end)
    processed = process_data(data)
    result = calculate_averages(processed)
    plot(result)

except requests.HTTPError:
    print(f'Error {response.status_code}: {response.reason}')
except ValueError:
    print('Incorrect time format')
