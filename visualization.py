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
    
    # Convert datetime column to pandas datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Filter data to use only the specified history
    cutoff_date = df['datetime'].max() - pd.Timedelta(days=history_days)
    filtered_df = df[df['datetime'] >= cutoff_date]
    
    followers_per_post_values = []
    # Calculate followers gained per post for each day within the window
    for i in range(len(filtered_df) - 1):
        current_date = filtered_df['datetime'].iloc[i]
        window_end_date = current_date + pd.Timedelta(days=args.window_size)
        window_df = filtered_df[(filtered_df['datetime'] > current_date) & (filtered_df['datetime'] <= window_end_date)]
        
        if len(window_df) > 1:
            followers_gained = window_df['followers'].iloc[-1] - window_df['followers'].iloc[0]
            posts_made = window_df['posts'].iloc[-1] - window_df['posts'].iloc[0]
            
            if posts_made > 0 and followers_gained >= 0:
                followers_per_post = followers_gained / posts_made
                followers_per_post_values.append(followers_per_post)
            else:
                followers_per_post_values.append(0)
                while len(followers_per_post_values) < len(filtered_df):
                    followers_per_post_values.append(0)
                if len(followers_per_post_values) < len(filtered_df):
                    followers_per_post_values.append(0)
                if len(followers_per_post_values) < len(filtered_df):
                    followers_per_post_values.append(0)
        else:
            followers_per_post_values.append(0)
    
    
    # Plot followers on primary y-axis
    color1 = '#1DA1F2'  # Twitter blue
    ax1.plot(filtered_df['datetime'], filtered_df['followers'], color=color1, linewidth=2, label='Followers')
    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('Followers', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # Format x-axis to show only 00:00 and 12:00
    ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(byhour=[0, 12]))
    
    # Plot posts on secondary y-axis
    color2 = '#17BF63'  # Twitter green
    ax2.plot(filtered_df['datetime'], filtered_df['posts'], color=color2, linewidth=2, label='Posts')
    ax2.set_ylabel('Posts', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Calculate followers gained per post over visualization period
    filtered_followers_gained = filtered_df['followers'].iloc[-1] - filtered_df['followers'].iloc[0]
    filtered_posts_made = filtered_df['posts'].iloc[-1] - filtered_df['posts'].iloc[0]
    
    if filtered_posts_made > 0 and filtered_followers_gained >= 0:
        followers_per_post = filtered_followers_gained / filtered_posts_made
        print(f"Followers gained per post: {followers_per_post:.1f}")
    else:
        print("Not enough data to calculate followers per post for this period")
    
    # Plot followers gained per post on tertiary y-axis
    color3 = '#FF5733'  # Custom color for followers gained per post
    ax3.plot(filtered_df['datetime'], followers_per_post_values, color=color3, linewidth=2, label='Followers Gained per Post')
    ax3.set_ylabel('Followers Gained per Post', color=color3)
    ax3.tick_params(axis='y', labelcolor=color3)
    
    # Add legends for all axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')
    
    # Update the plot
    plt.xticks(rotation=45)
    plt.tight_layout()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Plot followers and posts over time from a CSV file.')
    parser.add_argument('file_path', type=str, help='Path to the CSV file containing the data')
    parser.add_argument('--history_days', type=float, default=7, help='Number of days of history to plot (default: 7)')
    parser.add_argument('--window_size', type=int, default=7, help='Window size in days for computing followers gained per post (default: 7)')
    parser.add_argument('--refresh_interval', type=int, default=0, help='Refresh interval in seconds (default: 0, no refresh)')
    args = parser.parse_args()
    
    # Create figure with three y-axes
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))

    def update(frame):
        plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
        
    if args.refresh_interval > 0:
        # Create animation that updates every refresh_interval milliseconds
        ani = FuncAnimation(fig, update, interval=args.refresh_interval * 1000)
        
    plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
    plt.show()
