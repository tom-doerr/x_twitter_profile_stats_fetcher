# X (Twitter) Profile Stats Fetcher

This project contains a Python script for fetching profile statistics from X (formerly Twitter).

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
   pip install selenium webdriver_manager colorama
   ```

## Usage

The script fetches the number of posts, following, and followers for a given X profile.

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

## Features

- Multiple methods to find profile stats
- Retry mechanism for improved reliability
- CSV output for data storage
- Colorful console output

## Notes

- This script uses web scraping techniques and may break if X changes its website structure.
- Excessive use may lead to rate limiting or IP blocking by X.
- Respect X's terms of service and rate limits when using this script.

## License

This project is open-source and available under the MIT License.
