from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from html_sources.extract_interaction import extract_interaction
import logging
import traceback
import time
import re
import csv
from datetime import datetime
import os
import argparse
from colorama import init, Fore, Style

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_with_limit(message, limit=1000):
    """Log message with a character limit."""
    if len(message) > limit:
        message = message[:limit] + "... (truncated)"
    logger.info(message)

def write_to_csv(username, stats):
    filename = f"{username}_stats.csv"
    current_time = datetime.now().isoformat()
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['datetime', 'posts', 'following', 'followers']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'datetime': current_time,
            'posts': stats.get('posts', ''),
            'following': stats.get('following', ''),
            'followers': stats.get('followers', '')
        })
    
    log_with_limit(f"Data written to {filename}")

def initialize_browser(no_headless=False):
    """Initialize and return a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if not no_headless:
        options.add_argument('--headless')

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        return None

def get_profile_stats(driver, url):
    """Fetch profile stats from X/Twitter profile."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2)  # Wait for dynamic content

        if "This account doesn't exist" in driver.page_source:
            logger.error("Profile not accessible: Account doesn't exist")
            return None

        if "These tweets are protected" in driver.page_source:
            logger.error("Profile not accessible: Protected tweets")
            return None

        # Save profile HTML first to get accurate counts
        html_file = save_profile_html(driver, driver.current_url.split('/')[-1])
        
        # Try to get stats from JSON in page source first
        stats = find_stats_by_js(driver) or {}
        
        # Get additional stats from visible elements
        xpath_stats = find_stats_by_xpath(driver)
        if xpath_stats:
            # Only use xpath stats for values we don't already have
            for key, value in xpath_stats.items():
                if key not in stats or not stats[key]:
                    stats[key] = value
        
        # Update followers count if we can get it from userInteractionCount
        followers_count = extract_interaction(html_file)
        if followers_count:
            stats['followers'] = followers_count
            log_with_limit(f"Updated followers count from userInteractionCount: {followers_count}")

        if stats and ('followers' in stats):  # As long as we have followers, return what we found
            return stats

        return None
    except Exception as e:
        logger.error(f"Error fetching profile stats: {e}")
        return None

def get_hover_text(driver, element):
    """Get the title attribute or hover text from an element."""
    try:
        # First try getting the title attribute
        title = element.get_attribute('title')
        if title:
            return title

        # If no title, try hovering to get aria-label
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(0.5)  # Small delay to let hover text appear
        aria_label = element.get_attribute('aria-label')
        if aria_label:
            return aria_label
    except Exception as e:
        log_with_limit(f"Error getting hover text: {e}")
    return None

def find_stats_by_xpath(driver):
    """Find stats using specific XPaths and search for posts, following, and followers."""
    stats = {}
    xpaths = {
        'following': '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/div[1]/a/span[1]/span',
        'followers': '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/div[2]/a/span[1]/span'
    }
    
    for stat_name, xpath in xpaths.items():
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            log_with_limit(f"Found {len(elements)} elements for {stat_name}")
            if elements:
                for element in elements:
                    # Try getting hover text first for followers
                    if stat_name == 'followers':
                        hover_text = get_hover_text(driver, element)
                        if hover_text:
                            log_with_limit(f"Hover text found for {stat_name}: '{hover_text}'")
                            stats[stat_name] = parse_count(hover_text)
                            log_with_limit(f"{stat_name.capitalize()} found by hover: {stats[stat_name]}")
                            break

                    # Fall back to visible text if no hover text or for other stats
                    text = element.text.strip()
                    log_with_limit(f"Text found for {stat_name}: '{text}'")
                    if text:
                        stats[stat_name] = parse_count(text)
                        log_with_limit(f"{stat_name.capitalize()} found by XPath: {stats[stat_name]}")
                        break
                else:
                    log_with_limit(f"No valid text found for {stat_name}")
                    stats[stat_name] = 'N/A'
            else:
                log_with_limit(f"No element found for {stat_name}")
                stats[stat_name] = 'N/A'
        except Exception as e:
            log_with_limit(f"Failed to find {stat_name} by XPath: {str(e)}")
            stats[stat_name] = 'N/A'
    
    return stats

def find_stats_by_aria_label(driver):
    """Find stats using aria-label attributes."""
    stats = {}
    try:
        elements = driver.find_elements(By.XPATH, "//a[@aria-label and (contains(@href, '/following') or contains(@href, '/followers'))]")
        for element in elements:
            aria_label = element.get_attribute("aria-label")
            if "following" in aria_label.lower():
                match = re.search(r"(\d+(?:,\d+)*) Following", aria_label)
                if match:
                    stats['following'] = parse_count(match.group(1))
            elif "followers" in aria_label.lower():
                match = re.search(r"(\d+(?:,\d+)*) Followers", aria_label)
                if match:
                    stats['followers'] = parse_count(match.group(1))
        log_with_limit(f"Stats found by aria-label: {stats}")
    except Exception as e:
        log_with_limit(f"Failed to find stats by aria-label: {str(e)}")
    return stats if all(stats.values()) else None

def find_stats_by_href(driver):
    """Find stats by searching for text content near hrefs."""
    stats = {}
    try:
        page_source = driver.page_source
        patterns = {
            'following': r'href="[^"]*?/following[^"]*?"[^>]*>.*?(\d+(?:,\d+)*(?:\.\d+)?[KMB]?).*?</a>',
            'followers': r'href="[^"]*?/followers[^"]*?"[^>]*>.*?(\d+(?:,\d+)*(?:\.\d+)?[KMB]?).*?</a>'
        }
        for stat_name, pattern in patterns.items():
            match = re.search(pattern, page_source, re.IGNORECASE | re.DOTALL)
            if match:
                stats[stat_name] = parse_count(match.group(1))
                log_with_limit(f"{stat_name.capitalize()} found by href: {stats[stat_name]}")
    except Exception as e:
        log_with_limit(f"Failed to find stats by href: {str(e)}")
    return stats if all(stats.values()) else None

def save_page_source(driver, username):
    """Save the raw page source (like browser's View Source) to a local file."""
    html_dir = "html_sources"
    os.makedirs(html_dir, exist_ok=True)
    
    # Get the raw response content using CDP
    raw_html = driver.execute_cdp_cmd('Network.getResponseBody', 
        {'requestId': driver.execute_cdp_cmd('Network.enable', {})['requestId']})['body']
    
    filename = os.path.join(html_dir, f"{username}_page.html")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(raw_html)
    log_with_limit(f"Saved raw HTML source to {filename}")
    return filename

def find_stats_by_js(driver):
    """Find stats using JavaScript execution and page source parsing."""
    stats = {}
    try:
        # Save page source locally
        username = driver.current_url.split('/')[-1]
        html_file = save_page_source(driver, username)
        log_with_limit(f"Saved page source to {html_file}")

        # Read and analyze the page source first
        with open(html_file, 'r', encoding='utf-8') as f:
            page_source = f.read()
            
        log_with_limit("\n=== Starting page source parsing ===")
        log_with_limit(f"Page source length: {len(page_source)} characters")
        
        # Look for userInteractionCount in the page source and display 10 chars after it
        if 'userInteractionCount' in page_source:
            interaction_part = page_source.split('userInteractionCount')[1]
            next_ten_chars = interaction_part[:10]
            log_with_limit(f"10 chars after userInteractionCount: {next_ten_chars}")
            print(f"\n{Fore.YELLOW}10 chars after userInteractionCount:{Style.RESET_ALL} {next_ten_chars}")
            stats['interaction_context'] = next_ten_chars
            
        # Look for following and posts counts
        if 'followers' in stats:
            # Look for following count
            following_pattern = r'"friends_count":(\d+)'
            following_match = re.search(following_pattern, page_source)
            if following_match:
                stats['following'] = int(following_match.group(1))
                log_with_limit(f"Found following count: {stats['following']}")
            
            # Look for posts count (statuses)
            posts_pattern = r'"statuses_count":(\d+)'
            posts_match = re.search(posts_pattern, page_source)
            if posts_match:
                stats['posts'] = int(posts_match.group(1))
                log_with_limit(f"Found posts count (statuses): {stats['posts']}")

        # Return stats if we found at least followers and one other stat
        if len(stats) >= 2:
            log_with_limit(f"Successfully found stats in JSON: {stats}")
            return stats

        # Fall back to the original JS method if JSON parsing failed
        js_result = driver.execute_script("""
            var stats = {};
            var elements = document.querySelectorAll('a[href$="/following"] span, a[href$="/followers"] span');
            for (var i = 0; i < elements.length; i++) {
                var text = elements[i].textContent.trim();
                if (/^[0-9,.]+[KMB]?$/.test(text)) {
                    if (elements[i].closest('a').href.endsWith('/following')) {
                        stats.following = text;
                    } else if (elements[i].closest('a').href.endsWith('/followers')) {
                        stats.followers = text;
                    }
                }
            }
            return stats;
        """)
        if js_result:
            stats = {k: parse_count(v) for k, v in js_result.items()}
            log_with_limit(f"Stats found by JavaScript: {stats}")
            if all(stats.values()):
                return stats

        # Read the saved page source
        with open(html_file, 'r', encoding='utf-8') as f:
            page_source = f.read()
            
        log_with_limit("\n=== Starting page source parsing ===")
        log_with_limit(f"Page source length: {len(page_source)} characters")
        
        # Use extract_interaction to get followers count
        followers_count = extract_interaction(html_file)
        if followers_count:
            stats['followers'] = int(followers_count)
            log_with_limit(f"Found followers count from interaction: {stats['followers']}")
            print(f"\n{Fore.GREEN}Followers from userInteractionCount:{Style.RESET_ALL} {followers_count:,}")
            # Override any previously found followers count since this is more accurate
            return {'followers': stats['followers'], 'following': stats.get('following')}
        else:
            log_with_limit("No userInteractionCount found in HTML")
                    
        following_match = re.search(r'"friends_count":(\d+)', page_source)
        if following_match:
            stats['following'] = int(following_match.group(1))
            
        if stats:
            log_with_limit(f"Stats found in page source JSON: {stats}")
            
    except Exception as e:
        log_with_limit(f"Failed to find stats by JavaScript and JSON parsing: {str(e)}")
    return stats if stats else None

def parse_count(count_text):
    """Parse the count from text and return as an integer."""
    if not count_text:
        return None
    count_text = count_text.strip()
    
    # Handle K/M/B suffixes
    multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    
    # Try to extract number and potential suffix
    match = re.search(r'([\d,.]+)\s*([KMB])?', count_text, re.IGNORECASE)
    if not match:
        return None
        
    number_str = match.group(1)
    suffix = match.group(2).upper() if match.group(2) else ''
    
    try:
        # Convert the number part
        base_number = float(number_str.replace(',', ''))
        
        # Apply multiplier if suffix exists
        if suffix in multipliers:
            return int(base_number * multipliers[suffix])
        return int(base_number)
        
    except (ValueError, AttributeError) as e:
        log_with_limit(f"Failed to parse count: {count_text} - Error: {e}")
        return None

def get_text_by_xpath(driver, xpath):
    """Get text from an element using XPath."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except Exception as e:
        return f"Error finding element: {str(e)}"

def print_pretty_stats(profile_stats):
    print(f"\n{Fore.CYAN}=== Profile Stats ==={Style.RESET_ALL}")
    posts = profile_stats.get('posts', 'N/A')
    if posts != 'N/A':
        posts = f"{posts:,}"  # Add thousands separator
    print(f"{Fore.GREEN}Posts (Statuses):{Style.RESET_ALL} {posts}")
    print(f"{Fore.GREEN}Following:{Style.RESET_ALL} {profile_stats.get('following', 'N/A')}")
    print(f"{Fore.GREEN}Followers:{Style.RESET_ALL} {profile_stats.get('followers', 'N/A')}")
    if profile_stats.get('interaction_context'):
        print(f"{Fore.YELLOW}Interaction Context:{Style.RESET_ALL} {profile_stats['interaction_context']}")
    
    # Highlight follower count and character count separately
    print(f"\n{Fore.CYAN}=== Current Follower Count ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Followers:{Style.RESET_ALL} {profile_stats.get('followers', 'N/A'):,}")
    print(f"\n{Fore.CYAN}=== HTML Source Stats ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Character Count:{Style.RESET_ALL} {len(profile_stats.get('html_source', '')):,}")

def create_test_html():
    """Create a test HTML file with sample profile data."""
    html_dir = "html_sources"
    os.makedirs(html_dir, exist_ok=True)
    
    test_content = '''
    <!DOCTYPE html>
    <html>
    <head><title>Test Profile Page</title></head>
    <body>
        <script type="application/json">
        {
            "followers_count": 12345,
            "friends_count": 678,
            "statuses_count": 910
        }
        </script>
        <div class="profile-stats">
            <a href="/following">678 Following</a>
            <a href="/followers">12.3K Followers</a>
        </div>
    </body>
    </html>
    '''
    
    filepath = os.path.join(html_dir, "test2.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(test_content)
    log_with_limit(f"Created test HTML file at {filepath}")

def save_profile_html(driver, account):
    """Save the complete page source including dynamic content."""
    html_dir = "html_sources"
    os.makedirs(html_dir, exist_ok=True)
    
    # Wait for dynamic content to load
    time.sleep(2)
    
    # Get the complete page source including dynamic content
    complete_html = driver.execute_script("return document.documentElement.outerHTML;")
    
    filename = os.path.join(html_dir, f"{account}_profile.html")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(complete_html)
    log_with_limit(f"Saved complete HTML source to {filename} ({len(complete_html)} characters)")
    return filename

def main(account, interval, no_headless):
    profile_stats = None
    init()  # Initialize colorama
    url = f"https://x.com/{account}"
    while True:
        driver = initialize_browser(no_headless)
        if driver:
            try:
                print(f"\n{Fore.YELLOW}Fetching profile stats for {account}...{Style.RESET_ALL}")
                profile_stats = get_profile_stats(driver, url)
                
                # Save the profile page HTML after loading and add to stats
                html_file = save_profile_html(driver, account)
                with open(html_file, 'r', encoding='utf-8') as f:
                    profile_stats['html_source'] = f.read()
                if profile_stats:
                    print_pretty_stats(profile_stats)
                    
                    # Write stats to CSV
                    write_to_csv(account, profile_stats)
                    print(f"\n{Fore.CYAN}Stats written to {account}_stats.csv{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Could not fetch the profile stats.{Style.RESET_ALL}")
                
                print(f"\n{Fore.MAGENTA}Page Title:{Style.RESET_ALL} {driver.title}")
                print(f"\n{Fore.MAGENTA}Current URL:{Style.RESET_ALL} {driver.current_url}")
                
                # Get text from the specified XPath
                xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div'
                text_at_xpath = get_text_by_xpath(driver, xpath)
                print(f"\n{Fore.BLUE}Text found at specified XPath:{Style.RESET_ALL} {text_at_xpath}")
            except Exception as e:
                print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
                logger.error(f"An error occurred: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                driver.quit()
                log_with_limit("WebDriver closed")
        else:
            print(f"{Fore.RED}Failed to initialize the browser.{Style.RESET_ALL}")
        
        if interval <= 0:
            return profile_stats
        
        print(f"\n{Fore.YELLOW}Waiting for {interval} seconds before next fetch...{Style.RESET_ALL}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch X (Twitter) profile stats at specified intervals.")
    parser.add_argument("account", type=str, help="X (Twitter) account name (without @)")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="Interval in seconds between fetches. Use 0 for a single fetch.")
    parser.add_argument("--no-headless", action="store_true", help="Run Chrome in non-headless mode")
    args = parser.parse_args()

    profile_stats = main(args.account, args.interval, args.no_headless)
    if profile_stats:
        print(f"\n{Fore.GREEN}Follower count:{Style.RESET_ALL} {profile_stats.get('followers', 'N/A')}")
