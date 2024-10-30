#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import time

def plot_followers_and_posts(file_path, history_days):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Convert datetime column to pandas datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Filter data to use only the specified history
    cutoff_date = df['datetime'].max() - pd.Timedelta(days=history_days)
    filtered_df = df[df['datetime'] >= cutoff_date]
    
    # Plotting the followers and posts over time
    plt.figure(figsize=(10, 5))
    
    # Plot followers
    plt.plot(filtered_df['datetime'], filtered_df['followers'], label='Followers', linewidth=2)
    
    # Plot posts
    plt.plot(filtered_df['datetime'], filtered_df['posts'], label='Posts', linewidth=2)
    
    # Adding labels and legend
    plt.xlabel('Datetime')
    plt.ylabel('Count')
    plt.title('Number of Followers and Posts Over Time')
    plt.legend()
    
    # Display the plot
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Plot followers and posts over time from a CSV file.')
    parser.add_argument('file_path', type=str, help='Path to the CSV file containing the data')
    parser.add_argument('--history_days', type=int, default=7, help='Number of days of history to plot (default: 7)')
    parser.add_argument('--refresh_interval', type=int, default=0, help='Refresh interval in seconds (default: 0, no refresh)')
    args = parser.parse_args()
    
    # Continuously plot with specified refresh interval
    while True:
        plot_followers_and_posts(args.file_path, args.history_days)
        if args.refresh_interval <= 0:
            break
        time.sleep(args.refresh_interval)
