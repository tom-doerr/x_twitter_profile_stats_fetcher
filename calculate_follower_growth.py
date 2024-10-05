import csv
import sys
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from tabulate import tabulate

init(autoreset=True)  # Initialize colorama

def calculate_growth_stats(account_name):
    csv_file = f'{account_name}_stats.csv'
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        timestamp_key = next(key for key in reader.fieldnames if 'time' in key.lower())
        fol_key = next(key for key in reader.fieldnames if 'follower' in key.lower())
        for row in reader:
            timestamp = datetime.fromisoformat(row[timestamp_key].replace('Z', '+00:00'))
            fol = row[fol_key]
            if fol != 'N/A':
                data.append((timestamp, int(fol)))

    if len(data) < 2:
        return None

    data.sort(key=lambda x: x[0], reverse=True)  # Sort by timestamp, most recent first

    current_time, current_fol = data[0]
    
    def calculate_stats(hours):
        target_time = current_time - timedelta(hours=hours)
        closest_past = min(data[1:], key=lambda x: abs(x[0] - target_time))
        past_time, past_fol = closest_past
        time_diff = (current_time - past_time).total_seconds() / 86400  # Convert to days
        fol_diff = current_fol - past_fol
        growth_rate = fol_diff / time_diff
        return int(fol_diff), growth_rate

    hourly_diff, hourly_rate = calculate_stats(1)
    six_hour_diff, six_hour_rate = calculate_stats(6)
    daily_diff, daily_rate = calculate_stats(24)
    weekly_diff, weekly_rate = calculate_stats(24 * 7)

    return {
        'current_time': current_time,
        'current_fol': current_fol,
        'hourly': {'diff': hourly_diff, 'rate': hourly_rate},
        'six_hour': {'diff': six_hour_diff, 'rate': six_hour_rate},
        'daily': {'diff': daily_diff, 'rate': daily_rate},
        'weekly': {'diff': weekly_diff, 'rate': weekly_rate}
    }

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <account_name>")
        sys.exit(1)

    account_name = sys.argv[1]
    try:
        stats = calculate_growth_stats(account_name)

        if stats is None:
            print(f"{Fore.RED}Not enough data to calculate growth statistics.")
        else:
            print(f"{Fore.MAGENTA}{Style.BRIGHT}Follower Growth Statistics for {account_name}")
            print(f"{Fore.BLUE}Timestamp: {Style.BRIGHT}{stats['current_time']:%Y-%m-%d %H:%M:%S}")
            print(f"{Fore.GREEN}Current Fol: {Style.BRIGHT}{stats['current_fol']}")
            print()

            table_data = [
                ["Period", "NF", "GR (fol/day)", "GR (fol/week)"],
                ["1-hour", stats['hourly']['diff'], f"{int(stats['hourly']['rate'])}", f"{int(stats['hourly']['rate'] * 7)}"],
                ["6-hour", stats['six_hour']['diff'], f"{int(stats['six_hour']['rate'])}", f"{int(stats['six_hour']['rate'] * 7)}"],
                ["24-hour", stats['daily']['diff'], f"{int(stats['daily']['rate'])}", f"{int(stats['daily']['rate'] * 7)}"],
                ["7-day", stats['weekly']['diff'], f"{int(stats['weekly']['rate'])}", f"{int(stats['weekly']['rate'] * 7)}"]
            ]

            table = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
            print(Fore.CYAN + table)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: The file '{account_name}_stats.csv' was not found.")
    except ValueError as e:
        print(f"{Fore.RED}Error: {str(e)}")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
