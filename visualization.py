#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import time
from datetime import datetime
from matplotlib.animation import FuncAnimation
from tqdm import tqdm

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
    print(f"Length of filtered_df['datetime']: {len(filtered_df['datetime'])}")
    print(f"Length of filtered_df: {len(filtered_df)}")
    print(f"Length of df: {len(df)}")
    
    followers_per_post_values = []  # Initialize as an empty list
    followers_gained_list = []  # Initialize as an empty list
    posts_made_list = []  # Initialize as an empty list
    
    # Calculate followers gained per post for each day within the window
#    for i in range(len(filtered_df) - 1):
#        current_date = filtered_df['datetime'].iloc[i]
#        print("current_date:", current_date)
#        # window_end_date = current_date + pd.Timedelta(days=args.window_size)
#        window_end_date = current_date + pd.Timedelta(days=args.window_size/2)
#        print("window_end_date:", window_end_date)
#        window_start_date = current_date - pd.Timedelta(days=args.window_size/2)
#        print("window_start_date:", window_start_date)
#        nearest_start_date = filtered_df['datetime'].iloc[(filtered_df['datetime']-current_date).abs().argsort()[:1]]
#        print("nearest_start_date:", nearest_start_date)
#        nearest_end_date = filtered_df['datetime'].iloc[(filtered_df['datetime']-window_end_date).abs().argsort()[:1]]
#        print("nearest_end_date:", nearest_end_date)
#
#        # window_df = filtered_df[(filtered_df['datetime'] > current_date) & (filtered_df['datetime'] <= window_end_date)]
#        
#        # if len(window_df) > 1:
#        # if nearest_start_date < nearest_end_date:
#        if True:
#            # followers_gained = window_df['followers'].iloc[-1] - window_df['followers'].iloc[0]
#            # followers_gained = filtered_df['followers'].iloc[filtered_df['datetime'] == nearest_end_date].values[0] - filtered_df['followers'].iloc[filtered_df['datetime'] == nearest_start_date].values[0]
#            # If nearest_start_date is a Series with a single value, get the first value
#            nearest_start_date = nearest_start_date.iloc[0]
#
## Then use it in your comparison
#            index_start = filtered_df.index[filtered_df['datetime'] == nearest_start_date].tolist()[0]
#            # really just index
#
#            # a = filtered_df.index[filtered_df['datetime'] == nearest_start_date].tolist()
#            # index_start = a[0]
#            # nearest_end_date = nearest_end_date.iloc[0]
#            index_end = filtered_df.index[filtered_df['datetime'] == nearest_end_date].tolist()[0]
#            # followers_start = filtered_df['followers'].iloc[filtered_df['datetime'] == nearest_start_date].values[0]
#            #check if index is in the list
#            # if index_start  in filtered_df.index:
#            print("len(filtered_df):", len(filtered_df))
#            print("index_start:", index_start)
#            if index_start + 1 < len(filtered_df):
#                #check for out of bounds
#                followers_start = filtered_df['followers'].iloc[index_start]
#                print("followers_start:", followers_start)
#                # followers_end = filtered_df['followers'].iloc[filtered_df['datetime'] == nearest_end_date].values[0]
#                # followers_end = filtered_df['followers'].iloc[filtered_df['datetime'] == nearest_end_date].values[0]
#                followers_end = filtered_df['followers'].iloc[index_end]
#                print("followers_end:", followers_end)
#                # posts_made = window_df['posts'].iloc[-1] - window_df['posts'].iloc[0]
#                # posts_made = filtered_df['posts'].iloc[index_end] - filtered_df['posts'].iloc[index_start]
#                posts_start = filtered_df['posts'].iloc[index_start]
#                print("posts_start:", posts_start)
#                posts_end = filtered_df['posts'].iloc[index_end]
#                print("posts_end:", posts_end)
#                posts_made = posts_end - posts_start
#                followers_gained = followers_end - followers_start
#                print("followers_gained:", followers_gained)
#            else:
#                followers_gained = 0
#                posts_made = 0.00001
#            
#            if posts_made > 0 and followers_gained >= 0:
#                followers_gained_list.append(followers_gained)
#                print("followers_gained:", followers_gained)
#                posts_made_list.append(posts_made)
#                print("posts_made:", posts_made)
    # Only calculate followers-per-post metrics if the flag is set
    if args.show_followers_per_post:
        followers_per_post_values = []  # Initialize as an empty list
        followers_gained_list = []  # Initialize as an empty list
        posts_made_list = []  # Initialize as an empty list
        
        # Calculate followers gained per post for each day within the window
        for i in tqdm(range(len(filtered_df) - 1), desc="Processing data"):
            current_date = filtered_df['datetime'].iloc[i]
            window_end_date = current_date + pd.Timedelta(days=args.window_size/2)
            window_start_date = current_date - pd.Timedelta(days=args.window_size/2)
            
            # Directly use the window boundaries to filter data
            window_df = filtered_df[
                (filtered_df['datetime'] >= window_start_date) & 
                (filtered_df['datetime'] <= window_end_date)
            ]
            
            if len(window_df) > 1:  # Make sure we have at least 2 points to calculate difference
                followers_gained = window_df['followers'].iloc[-1] - window_df['followers'].iloc[0]
                posts_made = window_df['posts'].iloc[-1] - window_df['posts'].iloc[0]
                
                if posts_made > 0 and followers_gained >= 0:
                    followers_gained_list.append(followers_gained)
                    posts_made_list.append(posts_made)
                    theoretical_followers_per_post = followers_gained / posts_made
                    print("theoretical_followers_per_post:", theoretical_followers_per_post)
                    print()
                else:
                    followers_gained_list.append(0)
                    posts_made_list.append(0)
            else:
                followers_gained_list.append(0)
                posts_made_list.append(0)
        
        # Calculate followers gained per post for each window
        for i in tqdm(range(len(followers_gained_list)), desc="Calculating followers per post"):
            if posts_made_list[i] > 0:
                followers_per_post = followers_gained_list[i] / posts_made_list[i]
                followers_per_post_values.append(followers_per_post)
            else:
                followers_per_post_values.append(0)
    else:
        followers_per_post_values = [0] * len(filtered_df)  # Initialize with zeros
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
    
    # Only calculate overall followers per post if the flag is set
    if args.show_followers_per_post:
        filtered_followers_gained = filtered_df['followers'].iloc[-1] - filtered_df['followers'].iloc[0]
        filtered_posts_made = filtered_df['posts'].iloc[-1] - filtered_df['posts'].iloc[0]
        
        if filtered_posts_made > 0 and filtered_followers_gained >= 0:
            followers_per_post = filtered_followers_gained / filtered_posts_made
            print(f"Followers gained per post: {followers_per_post:.1f}")
        else:
            print("Not enough data to calculate followers per post for this period")
    
    # Ensure the length of followers_per_post_values matches filtered_df
    while len(followers_per_post_values) < len(filtered_df):
        followers_per_post_values.append(0)  # Append zeros to match the length
    
    # Only plot followers gained per post if enabled
    if args.show_followers_per_post:
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
    else:
        # Add legends for primary and secondary axes only
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
    parser.add_argument('--history_days', type=float, default=7, help='Number of days of history to plot (default: 7)')
    parser.add_argument('--window_size', type=int, default=7, help='Window size in days for computing followers gained per post (default: 7)')
    parser.add_argument('--refresh_interval', type=int, default=0, help='Refresh interval in seconds (default: 0, no refresh)')
    parser.add_argument('--show-followers-per-post', action='store_true', 
                       help='Enable followers gained per post visualization (default: False)')
    args = parser.parse_args()
    
    # Create figure with primary and secondary y-axes
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    
    # Only create tertiary axis if followers-per-post visualization is enabled
    if args.show_followers_per_post:
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))

    def update(frame):
        plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
        
    if args.refresh_interval > 0:
        # Create animation that updates every refresh_interval milliseconds
        ani = FuncAnimation(fig, update, interval=args.refresh_interval * 1000)
        
    plot_followers_and_posts(args.file_path, args.history_days, fig, ax1, ax2)
    plt.show()
