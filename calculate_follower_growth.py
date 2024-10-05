import csv
from datetime import datetime, timedelta

def calculate_current_growth(csv_file):
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
        return None, None

    data.sort(key=lambda x: x[0], reverse=True)  # Sort by timestamp, most recent first

    current_time, current_followers = data[0]
    one_hour_ago = current_time - timedelta(hours=1)

    # Find the closest data point to one hour ago
    closest_past = min(data[1:], key=lambda x: abs(x[0] - one_hour_ago))
    past_time, past_followers = closest_past

    time_diff = (current_time - past_time).total_seconds() / 3600  # Convert to hours
    follower_diff = current_followers - past_followers
    hourly_growth_rate = follower_diff / time_diff

    return current_time, hourly_growth_rate

def main():
    csv_file = 'tom_doerr_stats.csv'
    try:
        current_time, growth_rate = calculate_current_growth(csv_file)

        if current_time is None or growth_rate is None:
            print("Not enough data to calculate growth rate.")
        else:
            print(f"Current Follower Growth Rate for {csv_file}:")
            print(f"Timestamp: {current_time:%Y-%m-%d %H:%M:%S}")
            print(f"Hourly Growth Rate: {growth_rate:.2f}")
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
