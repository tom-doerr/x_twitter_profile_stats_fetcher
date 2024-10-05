# X (Twitter) Profile Stats Fetcher and Growth Calculator

This project contains Python scripts for fetching profile statistics from X (formerly Twitter) and calculating follower growth.

## Requirements

- Python 3.6+
- Chrome browser
- ChromeDriver (automatically managed by webdriver_manager)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/x-profile-stats-fetcher.git
   cd x-profile-stats-fetcher
   ```

2. Install the required Python packages:
   ```
   pip install selenium webdriver_manager colorama tabulate
   ```

## Usage

### 1. Fetching Profile Stats

The `get_profile_stats.py` script fetches the number of posts, following, and followers for a given X profile.

```
python get_profile_stats.py <account_name> [-i INTERVAL]
```

- `<account_name>`: The X account name (without @)
- `-i INTERVAL`: (Optional) Interval in seconds between fetches. Use 0 for a single fetch (default).

Example:
```
python get_profile_stats.py elonmusk -i 3600
```

This will fetch stats for @elonmusk every hour.

### 2. Calculating Follower Growth

The `calculate_follower_growth.py` script analyzes the growth statistics based on the data collected by `get_profile_stats.py`.

```
python calculate_follower_growth.py <account_name> [--refresh] [interval_seconds] [--plot]
```

- `<account_name>`: The X account name (without @)
- `--refresh`: (Optional) Enables refresh mode, which updates the statistics periodically.
- `interval_seconds`: (Optional) Specifies the refresh interval in seconds when using refresh mode. Default is 60 seconds.
- `--plot`: (Optional) Displays an ASCII bar chart of daily follower gains for the last 7 days.

Examples:
- Run once: `python calculate_follower_growth.py elonmusk`
- Run in refresh mode (60-second interval): `python calculate_follower_growth.py elonmusk --refresh`
- Run in refresh mode with custom interval: `python calculate_follower_growth.py elonmusk --refresh 30`
- Run with plot: `python calculate_follower_growth.py elonmusk --plot`
- Run in refresh mode with plot: `python calculate_follower_growth.py elonmusk --refresh 60 --plot`

## Features

- Multiple methods to find profile stats
- Retry mechanism for improved reliability
- CSV output for data storage
- Colorful console output
- Follower growth calculation for various time periods
- ASCII bar chart for visualizing daily follower gains

## Notes

- These scripts use web scraping techniques and may break if X changes its website structure.
- Excessive use may lead to rate limiting or IP blocking by X.
- Respect X's terms of service and rate limits when using these scripts.
- Run `get_profile_stats.py` regularly to collect data points for accurate growth analysis.

## License

This project is open-source and available under the MIT License.
