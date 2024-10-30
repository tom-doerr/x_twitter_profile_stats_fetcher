#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import time
from datetime import datetime
from matplotlib.animation import FuncAnimation

def plot_followers_and_posts(file_path, history_days, fig, ax1, ax2):
    # Clear the axes
    ax1.clear()
    ax2.clear()
    print(f"\nRefresh timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Calculate followers gained per post
    followers_gained = df['followers'].iloc[-1] - df['followers'].iloc[0]
    posts_made = df['posts'].iloc[-1] - df['posts'].iloc[0]
    followers_per_post = followers_gained / posts_made if posts_made > 0 else 0
    print(f"Followers gained per post: {followers_per_post:.2f}")
    
    # Convert datetime column to pandas datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Filter data to use only the specified history
    cutoff_date = df['datetime'].max() - pd.Timedelta(days=history_days)
    filtered_df = df[df['datetime'] >= cutoff_date]
    
    
    # Plot followers on primary y-axis
    color1 = '#1DA1F2'  # Twitter blue
    ax1.plot(filtered_df['datetime'], filtered_df['followers'], color=color1, linewidth=2, label='Followers')
    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('Followers', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # Format x-axis to show just the day number
    ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d\n%H:%M'))
    
    # Plot posts on secondary y-axis
    color2 = '#17BF63'  # Twitter green
    ax2.plot(filtered_df['datetime'], filtered_df['posts'], color=color2, linewidth=2, label='Posts')
    ax2.set_ylabel('Posts', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Add title
    plt.title('Followers and Posts Over Time')
    
    # Add legends for both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Update the plot
    plt.xticks(rotation=45)
    plt.tight_layout()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Plot followers and posts over time from a CSV file.')
    parser.add_argument('file_path', type=str, help='Path to the CSV file containing the data')
    parser.add_argument('--history_days', type=int, default=7, help='Number of days of history to plot (default: 7)')
    parser.add_argument('--refresh_interval', type=int, default=0, help='Refresh interval in seconds (default: 0, no refresh)')
    args = parser.parse_args()
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    def update(frame):
        plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
        
    if args.refresh_interval > 0:
        # Create animation that updates every refresh_interval milliseconds
        ani = FuncAnimation(fig, update, interval=args.refresh_interval * 1000)
        
    plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
    plt.show()
