from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import traceback
import time
import re
import csv
from datetime import datetime
import os
import argparse
from colorama import init, Fore, Style
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_with_limit(message, limit=1000):
    """Log message with a character limit."""
    if len(message) > limit:
        message = message[:limit] + "... (truncated)"
    logger.info(message)

def get_username_from_url(url):
    return url.split('/')[-1]

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
    options.add_argument('--window-size=1920,1080')  # Set a larger window size
    if not no_headless:
        options.add_argument('--headless')  # Headless mode by default

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1920, 1080)  # Ensure the window size is set
        log_with_limit("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        return None

def get_profile_stats(driver, url, timeout=20, max_html_length=1000, max_retries=3, retry_delay=5):
    """
    Fetch the number of posts, following, and followers for a given X (formerly Twitter) profile.

    Args:
    driver (webdriver.Chrome): The Chrome WebDriver instance.
    url (str): The URL of the X profile. Defaults to DEFAULT_URL.
    timeout (int): Maximum time to wait for page elements, in seconds. Defaults to 20.
    max_html_length (int): Maximum length of HTML to log. Defaults to 1000 characters.
    max_retries (int): Maximum number of retry attempts. Defaults to 3.
    retry_delay (int): Delay between retry attempts in seconds. Defaults to 5.

    Returns:
    dict: A dictionary containing 'posts', 'following', and 'followers' counts, or None if unable to fetch.
    """
    for attempt in range(max_retries):
        try:
            log_with_limit(f"Loading URL: {url} (Attempt {attempt + 1}/{max_retries})")
            driver.get(url)
            
            # Wait for the page to load completely
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            log_with_limit("Page loaded completely")
            
            # Wait for main content with a shorter timeout
            try:
                main_content = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'main[role="main"]'))
                )
            except TimeoutException:
                log_with_limit("Timeout waiting for main content, continuing anyway...")
            
            # Give the page a moment to load dynamic content
            time.sleep(2)
            
            # Remove scrolling as it's not necessary
            
            # Check if the profile is accessible
            if "This account doesn't exist" in driver.page_source:
                logger.error("Profile not accessible: This account doesn't exist")
                return None
            
            if "These tweets are protected" in driver.page_source:
                logger.error("Profile not accessible: Tweets are protected")
                return None
                
            # Try multiple methods to find the stats
            methods = [
                lambda: find_stats_by_xpath(driver),
                lambda: find_stats_by_aria_label(driver),
                lambda: find_stats_by_href(driver),
                lambda: find_stats_by_js(driver),
            ]
            
            for method in methods:
                try:
                    stats = method()
                    if stats and all(stats.values()):
                        return stats
                except Exception as e:
                    log_with_limit(f"Method failed: {str(e)}")
            
            # If we've reached this point, we couldn't find the profile stats
            log_with_limit("Couldn't find profile stats.")
            log_with_limit(f"Page source: {driver.page_source[:max_html_length]}")
            
        except Exception as e:
            log_with_limit(f"Unexpected error occurred: {e}")
            log_with_limit(traceback.format_exc())
        
        if attempt < max_retries - 1:
            log_with_limit(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logger.error("Failed to fetch profile stats after all retry attempts.")
    
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
        'posts': '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div',
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

def find_stats_by_js(driver):
    """Find stats using JavaScript execution and page source parsing."""
    stats = {}
    try:
        # First try the original JS method
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

        # Fallback: Parse the page source for JSON data
        page_source = driver.page_source
        log_with_limit("\n=== Starting page source parsing ===")
        log_with_limit(f"Page source length: {len(page_source)} characters")
        
        # Try multiple patterns for follower count
        follower_patterns = [
            r'"normal_followers_count":(\d+)',
            r'"followers_count":(\d+)',
            r'title="(\d+(?:,\d+)*) Followers"',
            r'<span>[^<]*?(\d+(?:,\d+)*(?:\.\d+)?[KMB]?) Followers'
        ]
        
        log_with_limit("\nSearching for follower count patterns:")
        for pattern in follower_patterns:
            log_with_limit(f"\nTrying pattern: {pattern}")
            
            # First check if the pattern exists at all
            if pattern in page_source:
                log_with_limit("Pattern string found in page source")
            else:
                log_with_limit("Pattern string NOT found in page source")
                continue
                
            followers_match = re.search(pattern, page_source)
            if followers_match:
                follower_text = followers_match.group(1)
                log_with_limit(f"Found match! Full match: {followers_match.group(0)}")
                log_with_limit(f"Extracted text: {follower_text}")
                
                # Show surrounding context
                start = max(0, followers_match.start() - 50)
                end = min(len(page_source), followers_match.end() + 50)
                context = page_source[start:end]
                log_with_limit(f"Match context: ...{context}...")
                
                stats['followers'] = parse_count(follower_text)
                log_with_limit(f"Parsed count: {stats['followers']}")
                
                if stats['followers']:
                    log_with_limit(f"Successfully parsed follower count: {stats['followers']}")
                    break
                else:
                    log_with_limit("Failed to parse number from match")
            else:
                log_with_limit("No regex match found")
                    
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
    print(f"{Fore.CYAN}Profile Stats:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Posts:{Style.RESET_ALL} {profile_stats.get('posts', 'N/A')}")
    print(f"{Fore.GREEN}Following:{Style.RESET_ALL} {profile_stats.get('following', 'N/A')}")
    print(f"{Fore.GREEN}Followers:{Style.RESET_ALL} {profile_stats.get('followers', 'N/A')}")

def main(account, interval, no_headless):
    init()  # Initialize colorama
    url = f"https://x.com/{account}"
    while True:
        driver = initialize_browser(no_headless)
        if driver:
            try:
                print(f"\n{Fore.YELLOW}Fetching profile stats for {account}...{Style.RESET_ALL}")
                profile_stats = get_profile_stats(driver, url)
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
            break
        
        print(f"\n{Fore.YELLOW}Waiting for {interval} seconds before next fetch...{Style.RESET_ALL}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch X (Twitter) profile stats at specified intervals.")
    parser.add_argument("account", type=str, help="X (Twitter) account name (without @)")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="Interval in seconds between fetches. Use 0 for a single fetch.")
    parser.add_argument("--no-headless", action="store_true", help="Run Chrome in non-headless mode")
    args = parser.parse_args()

    main(args.account, args.interval, args.no_headless)
