import csv
from datetime import datetime, timedelta

def calculate_growth_rates(csv_file):
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        timestamp_key = next(key for key in reader.fieldnames if 'time' in key.lower())
        followers_key = next(key for key in reader.fieldnames if 'follower' in key.lower())
        for row in reader:
            timestamp = datetime.fromisoformat(row[timestamp_key].replace('Z', '+00:00'))
            followers = row[followers_key]
            if followers != 'N/A':
                data.append((timestamp, int(followers)))

    if len(data) < 2:
        return None, None, None, None

    data.sort(key=lambda x: x[0], reverse=True)  # Sort by timestamp, most recent first

    current_time, current_followers = data[0]
    
    def calculate_rate(hours):
        target_time = current_time - timedelta(hours=hours)
        closest_past = min(data[1:], key=lambda x: abs(x[0] - target_time))
        past_time, past_followers = closest_past
        time_diff = (current_time - past_time).total_seconds() / 3600  # Convert to hours
        follower_diff = current_followers - past_followers
        return follower_diff / time_diff

    hourly_rate = calculate_rate(1)
    six_hour_rate = calculate_rate(6)
    daily_rate = calculate_rate(24)

    return current_time, hourly_rate, six_hour_rate, daily_rate

def main():
    csv_file = 'tom_doerr_stats.csv'
    try:
        current_time, hourly_rate, six_hour_rate, daily_rate = calculate_growth_rates(csv_file)

        if current_time is None:
            print("Not enough data to calculate growth rates.")
        else:
            print(f"Follower Growth Rates for {csv_file}:")
            print(f"Timestamp: {current_time:%Y-%m-%d %H:%M:%S}")
            print(f"1-hour Growth Rate: {hourly_rate:.2f}")
            print(f"6-hour Growth Rate: {six_hour_rate:.2f}")
            print(f"24-hour Growth Rate: {daily_rate:.2f}")
            print(f"Projected 24-hour growth at current rate: {hourly_rate * 24:.2f}")
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
