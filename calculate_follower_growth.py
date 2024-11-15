#!/usr/bin/env python

import csv
import sys
import time
import argparse
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
        post_key = next(key for key in reader.fieldnames if 'post' in key.lower())
        for row in reader:
            timestamp = datetime.fromisoformat(row[timestamp_key].replace('Z', '+00:00'))
            fol = row[fol_key]
            posts = row[post_key]
            if fol != 'N/A':
                post_count = 0 if posts == '' or posts == 'N/A' else int(posts)
                data.append((timestamp, int(fol), post_count))

    if len(data) < 2:
        return None

    data.sort(key=lambda x: x[0], reverse=True)  # Sort by timestamp, most recent first

    current_time, current_fol, current_posts = data[0]
    
    def calculate_stats(hours):
        target_time = current_time - timedelta(hours=hours)
        closest_past = min(data[1:], key=lambda x: abs(x[0] - target_time))
        past_time, past_fol, past_posts = closest_past
        time_diff = (current_time - past_time).total_seconds() / 86400  # Convert to days
        fol_diff = current_fol - past_fol
        post_diff = current_posts - past_posts
        fol_growth_rate = fol_diff / time_diff
        post_growth_rate = post_diff / time_diff
        return int(fol_diff), fol_growth_rate, int(post_diff), post_growth_rate

    hourly_fol_diff, hourly_fol_rate, hourly_post_diff, hourly_post_rate = calculate_stats(1)
    six_hour_fol_diff, six_hour_fol_rate, six_hour_post_diff, six_hour_post_rate = calculate_stats(6)
    daily_fol_diff, daily_fol_rate, daily_post_diff, daily_post_rate = calculate_stats(24)
    weekly_fol_diff, weekly_fol_rate, weekly_post_diff, weekly_post_rate = calculate_stats(24 * 7)

    return {
        'current_time': current_time,
        'current_fol': current_fol,
        'current_posts': current_posts,
        'hourly': {
            'fol_diff': hourly_fol_diff, 'fol_rate': hourly_fol_rate,
            'post_diff': hourly_post_diff, 'post_rate': hourly_post_rate
        },
        'six_hour': {
            'fol_diff': six_hour_fol_diff, 'fol_rate': six_hour_fol_rate,
            'post_diff': six_hour_post_diff, 'post_rate': six_hour_post_rate
        },
        'daily': {
            'fol_diff': daily_fol_diff, 'fol_rate': daily_fol_rate,
            'post_diff': daily_post_diff, 'post_rate': daily_post_rate
        },
        'weekly': {
            'fol_diff': weekly_fol_diff, 'fol_rate': weekly_fol_rate,
            'post_diff': weekly_post_diff, 'post_rate': weekly_post_rate
        }
    }

def display_follower_stats(stats):
    print(f"{Fore.BLUE}Timestamp: {Style.BRIGHT}{stats['current_time']:%Y-%m-%d %H:%M:%S}")
    print(f"{Fore.GREEN}Current Fol: {Style.BRIGHT}{stats['current_fol']:,}")
    print()

    table_data = [
        ["Period", "NF", "   GR day", "   GR week"],
        ["1-hour", f"{Fore.YELLOW}{stats['hourly']['fol_diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['hourly']['fol_rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['hourly']['fol_rate'] * 7):>10,}{Fore.CYAN}"],
        ["6-hour", f"{Fore.YELLOW}{stats['six_hour']['fol_diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['six_hour']['fol_rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['six_hour']['fol_rate'] * 7):>10,}{Fore.CYAN}"],
        ["24-hour", f"{Fore.YELLOW}{stats['daily']['fol_diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['daily']['fol_rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['daily']['fol_rate'] * 7):>10,}{Fore.CYAN}"],
        ["7-day", f"{Fore.YELLOW}{stats['weekly']['fol_diff']:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['weekly']['fol_rate']):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['weekly']['fol_rate'] * 7):>10,}{Fore.CYAN}"]
    ]

    table = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
    print(f"{Fore.CYAN}{table}")

def display_post_stats(stats):
    print(f"\n{Fore.GREEN}Current Posts: {Style.BRIGHT}{stats['current_posts']:,}")
    print()

    table_data = [
        ["Period", "NP", "   GR day", "   GR week"],
        ["1-hour", f"{Fore.YELLOW}{stats['hourly']['post_diff'] or 0:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['hourly']['post_rate'] or 0):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int((stats['hourly']['post_rate'] or 0) * 7):>10,}{Fore.CYAN}"],
        ["6-hour", f"{Fore.YELLOW}{stats['six_hour']['post_diff'] or 0:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['six_hour']['post_rate'] or 0):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int((stats['six_hour']['post_rate'] or 0) * 7):>10,}{Fore.CYAN}"],
        ["24-hour", f"{Fore.YELLOW}{stats['daily']['post_diff'] or 0:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['daily']['post_rate'] or 0):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int((stats['daily']['post_rate'] or 0) * 7):>10,}{Fore.CYAN}"],
        ["7-day", f"{Fore.YELLOW}{stats['weekly']['post_diff'] or 0:,}{Fore.CYAN}", f"{Fore.YELLOW}{int(stats['weekly']['post_rate'] or 0):>10,}{Fore.CYAN}", f"{Fore.YELLOW}{int((stats['weekly']['post_rate'] or 0) * 7):>10,}{Fore.CYAN}"]
    ]

    table = tabulate(table_data, headers="firstrow", tablefmt="fancy_grid")
    print(f"{Fore.CYAN}{table}")

def parse_args():
    parser = argparse.ArgumentParser(description='Calculate and display follower growth statistics')
    parser.add_argument('account_name', help='Name of the account to analyze')
    parser.add_argument('--refresh', type=int, metavar='SECONDS', nargs='?', const=60,
                      help='Enable refresh mode with optional interval in seconds (default: 60)')
    parser.add_argument('--plot', action='store_true',
                      help='Enable plotting of daily gains')
    parser.add_argument('--posts', action='store_true',
                      help='Show post statistics')
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        while True:
            stats = calculate_growth_stats(args.account_name)

            if stats is None:
                print(f"{Fore.RED}Not enough data to calculate growth statistics.")
            else:
                # Clear the console (works for both Windows and Unix-like systems)
                print("\033[H\033[J", end="")
                display_follower_stats(stats)
                if args.posts:
                    display_post_stats(stats)

                if args.plot:
                    plot_daily_gains(args.account_name)

            if args.refresh is None:
                break

            time.sleep(args.refresh)

    try:
        while True:
            stats = calculate_growth_stats(account_name)

            if stats is None:
                print(f"{Fore.RED}Not enough data to calculate growth statistics.")
            else:
                # Clear the console (works for both Windows and Unix-like systems)
                print("\033[H\033[J", end="")
                display_follower_stats(stats)
                if show_posts:
                    display_post_stats(stats)

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
