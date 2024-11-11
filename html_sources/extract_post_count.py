#!/usr/bin/env python3

import re
import os
import argparse
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

init()  # Initialize colorama

def extract_post_count(html_file, debug=False):
    """
    Extract post count from HTML file using statuses_count
    
    Args:
        html_file (str): Path to the HTML file
        debug (bool): Enable debug output
        
    Returns:
        int: The post count if found, None otherwise
    """
    try:
        if debug:
            print(f"\n{Fore.CYAN}=== Debug: extract_post_count() ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Input file:{Style.RESET_ALL} {html_file}")

        if not os.path.exists(html_file):
            if debug:
                print(f"{Fore.RED}Error: File does not exist{Style.RESET_ALL}")
            return None

        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if debug:
                print(f"{Fore.GREEN}Successfully read {len(content):,} characters{Style.RESET_ALL}")

        # Pattern matches "statuses_count":number
        pattern = r'"statuses_count":(\d+)'
        if debug:
            print(f"{Fore.YELLOW}Using pattern:{Style.RESET_ALL} {pattern}")

        # Show context around statuses_count if found
        index = content.find('statuses_count')
        if index != -1 and debug:
            start = max(0, index - 50)
            end = min(len(content), index + 50)
            context = content[start:end]
            print(f"\n{Fore.CYAN}Found 'statuses_count' at position {index}{Style.RESET_ALL}")
            print(f"Context: ...{context}...")

        match = re.search(pattern, content)
        if match:
            count = int(match.group(1))
            if debug:
                print(f"\n{Fore.GREEN}Found post count:{Style.RESET_ALL} {count:,}")
            return count

        if debug:
            print(f"\n{Fore.RED}No post count found in file{Style.RESET_ALL}")
        return None

    except Exception as e:
        if debug:
            print(f"\n{Fore.RED}Error processing file:{Style.RESET_ALL} {str(e)}")
        return None

def get_latest_profile_html(directory="html_sources"):
    """Get the most recent profile HTML file from the directory."""
    try:
        files = [f for f in os.listdir(directory) if f.endswith('_profile.html')]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        return os.path.join(directory, files[0])
    except Exception as e:
        print(f"Error finding latest profile HTML: {str(e)}")
        return None

def initialize_browser():
    """Initialize and return a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize Chrome WebDriver: {e}{Style.RESET_ALL}")
        return None

def download_profile_html(username):
    """Download profile HTML for given username."""
    driver = initialize_browser()
    if not driver:
        return None
        
    try:
        url = f"https://x.com/{username}"
        print(f"\n{Fore.CYAN}Downloading profile from:{Style.RESET_ALL} {url}")
        
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        os.makedirs("html_sources", exist_ok=True)
        html_file = f"html_sources/{username}_profile.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
            
        print(f"{Fore.GREEN}Profile HTML saved to:{Style.RESET_ALL} {html_file}")
        return html_file
        
    except Exception as e:
        print(f"{Fore.RED}Error downloading profile: {e}{Style.RESET_ALL}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract post count from X/Twitter profile")
    parser.add_argument("username", nargs="?", help="X/Twitter username (without @)")
    args = parser.parse_args()
    
    if args.username:
        html_file = download_profile_html(args.username)
    else:
        html_file = get_latest_profile_html()
        
    if html_file:
        print(f"\n{Fore.CYAN}Processing profile HTML:{Style.RESET_ALL} {html_file}")
        count = extract_post_count(html_file, debug=True)
        if count is not None:
            print(f"\n{Fore.GREEN}Post count:{Style.RESET_ALL} {count:,}")
        else:
            print(f"\n{Fore.RED}Could not extract post count{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}No profile HTML found/downloaded{Style.RESET_ALL}")
