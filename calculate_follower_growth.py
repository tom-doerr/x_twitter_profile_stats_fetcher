import csv
from datetime import datetime, timedelta

def calculate_follower_growth(csv_file):
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        timestamp_key = next(key for key in reader.fieldnames if 'time' in key.lower())
        followers_key = next(key for key in reader.fieldnames if 'follower' in key.lower())
        for row in reader:
            timestamp = datetime.strptime(row[timestamp_key], '%Y-%m-%d %H:%M:%S')
            followers = int(row[followers_key])
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
    try:
        growth_rates = calculate_follower_growth(csv_file)

        print(f"Follower Growth Rates for {csv_file}:")
        print("Timestamp               | Hourly Growth Rate")
        print("-" * 45)
        for timestamp, rate in growth_rates:
            print(f"{timestamp:%Y-%m-%d %H:%M:%S} | {rate:.2f}")
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
