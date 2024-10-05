import csv
import sys
import time
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from tabulate import tabulate

init(autoreset=True)  # Initialize colorama

def calculate_daily_gains(data, days=7):
    daily_gains = []
    for i in range(days):
        end_date = datetime.now().date() - timedelta(days=i)
        start_date = end_date - timedelta(days=1)
        
        end_followers = next((fol for date, fol in data if date.date() == end_date), None)
        start_followers = next((fol for date, fol in data if date.date() == start_date), None)
        
        if end_followers is not None and start_followers is not None:
            daily_gains.append((end_date, end_followers - start_followers))
        else:
            daily_gains.append((end_date, 0))
    
    return daily_gains[::-1]  # Reverse the list to have oldest date first

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

def display_stats(stats):
    print(f"{Fore.BLUE}Timestamp: {Style.BRIGHT}{stats['current_time']:%Y-%m-%d %H:%M:%S}")
    print(f"{Fore.GREEN}Current Fol: {Style.BRIGHT}{stats['current_fol']:,}")
    print()

    table_data = [
        ["Period", "NF", "GR day", "GR week"],
        ["1-hour", f"{Fore.YELLOW}{stats['hourly']['diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['hourly']['rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['hourly']['rate'] * 7):>15,}{Fore.CYAN}"],
        ["6-hour", f"{Fore.YELLOW}{stats['six_hour']['diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['six_hour']['rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['six_hour']['rate'] * 7):>15,}{Fore.CYAN}"],
        ["24-hour", f"{Fore.YELLOW}{stats['daily']['diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['daily']['rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['daily']['rate'] * 7):>15,}{Fore.CYAN}"],
        ["7-day", f"{Fore.YELLOW}{stats['weekly']['diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['weekly']['rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['weekly']['rate'] * 7):>15,}{Fore.CYAN}"]
    ]

    table = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
    print(f"{Fore.CYAN}{table}")

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        print(f"Usage: python {sys.argv[0]} <account_name> [--refresh] [interval_seconds] [--plot]")
        sys.exit(1)

    account_name = sys.argv[1]
    refresh_mode = "--refresh" in sys.argv
    plot_mode = "--plot" in sys.argv
    interval = 60  # Default interval

    if refresh_mode and len(sys.argv) >= 4:
        try:
            interval = int(sys.argv[sys.argv.index("--refresh") + 1])
        except (ValueError, IndexError):
            print(f"{Fore.RED}Error: Invalid interval. Using default of 60 seconds.")

    try:
        while True:
            stats = calculate_growth_stats(account_name)

            if stats is None:
                print(f"{Fore.RED}Not enough data to calculate growth statistics.")
            else:
                # Clear the console (works for both Windows and Unix-like systems)
                print("\033[H\033[J", end="")
                display_stats(stats)

                if plot_mode:
                    plot_daily_gains(account_name)

            if not refresh_mode:
                break

            time.sleep(interval)

    except FileNotFoundError:
        print(f"{Fore.RED}Error: The file '{account_name}_stats.csv' was not found.")
    except ValueError as e:
        print(f"{Fore.RED}Error: {str(e)}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Refresh mode stopped.")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {str(e)}")

def plot_daily_gains(account_name):
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

    daily_gains = calculate_daily_gains(data)

    print(f"\n{Fore.CYAN}Daily Follower Gains for {account_name}:")
    print(f"{Fore.CYAN}{'Date':<12} {'Gain':<8} {'Chart'}")
    print(f"{Fore.CYAN}{'-'*40}")

    max_gain = max(gain for _, gain in daily_gains)
    scale_factor = 20 / max_gain if max_gain > 0 else 1

    for date, gain in daily_gains:
        bar_length = int(gain * scale_factor)
        bar = '█' * bar_length
        print(f"{Fore.YELLOW}{date.strftime('%Y-%m-%d'):<12} {Fore.GREEN}{gain:<8} {Fore.BLUE}{bar}")

    print()

if __name__ == "__main__":
    main()
