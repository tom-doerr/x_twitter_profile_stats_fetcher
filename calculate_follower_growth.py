import csv
from datetime import datetime, timedelta

def calculate_follower_growth(csv_file):
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            followers = int(row['followers'])
            data.append((timestamp, followers))

    data.sort(key=lambda x: x[0])  # Sort by timestamp

    growth_rates = []
    for i in range(len(data)):
        start_time, start_followers = data[i]
        end_time = start_time + timedelta(hours=1)

        # Find the closest data point to one hour later
        closest_end = min((t for t in data if t[0] > start_time), key=lambda x: abs(x[0] - end_time))
        end_time, end_followers = closest_end

        time_diff = (end_time - start_time).total_seconds() / 3600  # Convert to hours
        follower_diff = end_followers - start_followers
        hourly_growth_rate = follower_diff / time_diff

        growth_rates.append((start_time, hourly_growth_rate))

    return growth_rates

def main():
    csv_file = 'tom_doerr_stats.csv'
    growth_rates = calculate_follower_growth(csv_file)

    print(f"Follower Growth Rates for {csv_file}:")
    print("Timestamp               | Hourly Growth Rate")
    print("-" * 45)
    for timestamp, rate in growth_rates:
        print(f"{timestamp:%Y-%m-%d %H:%M:%S} | {rate:.2f}")

if __name__ == "__main__":
    main()
