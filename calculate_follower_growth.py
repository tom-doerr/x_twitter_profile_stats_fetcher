import csv
from datetime import datetime, timedelta

def calculate_growth_stats(csv_file):
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
        return None

    data.sort(key=lambda x: x[0], reverse=True)  # Sort by timestamp, most recent first

    current_time, current_followers = data[0]
    
    def calculate_stats(hours):
        target_time = current_time - timedelta(hours=hours)
        closest_past = min(data[1:], key=lambda x: abs(x[0] - target_time))
        past_time, past_followers = closest_past
        time_diff = (current_time - past_time).total_seconds() / 86400  # Convert to days
        follower_diff = current_followers - past_followers
        growth_rate = follower_diff / time_diff
        return int(follower_diff), growth_rate

    hourly_diff, hourly_rate = calculate_stats(1)
    six_hour_diff, six_hour_rate = calculate_stats(6)
    daily_diff, daily_rate = calculate_stats(24)
    weekly_diff, weekly_rate = calculate_stats(24 * 7)

    return {
        'current_time': current_time,
        'current_followers': current_followers,
        'hourly': {'diff': hourly_diff, 'rate': hourly_rate},
        'six_hour': {'diff': six_hour_diff, 'rate': six_hour_rate},
        'daily': {'diff': daily_diff, 'rate': daily_rate},
        'weekly': {'diff': weekly_diff, 'rate': weekly_rate}
    }

def main():
    csv_file = 'tom_doerr_stats.csv'
    try:
        stats = calculate_growth_stats(csv_file)

        if stats is None:
            print("Not enough data to calculate growth statistics.")
        else:
            print(f"Follower Growth Statistics for {csv_file}:")
            print(f"Timestamp: {stats['current_time']:%Y-%m-%d %H:%M:%S}")
            print(f"Current Followers: {stats['current_followers']}")
            print("\n1-hour Growth:")
            print(f"  New Followers: {stats['hourly']['diff']}")
            print(f"  Growth Rate: {stats['hourly']['rate']:.2f} followers/day")
            print("\n6-hour Growth:")
            print(f"  New Followers: {stats['six_hour']['diff']}")
            print(f"  Growth Rate: {stats['six_hour']['rate']:.2f} followers/day")
            print("\n24-hour Growth:")
            print(f"  New Followers: {stats['daily']['diff']}")
            print(f"  Growth Rate: {stats['daily']['rate']:.2f} followers/day")
            print("\n7-day Growth:")
            print(f"  New Followers: {stats['weekly']['diff']}")
            print(f"  Growth Rate: {stats['weekly']['rate']:.2f} followers/day")
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
