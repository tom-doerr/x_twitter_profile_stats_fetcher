#!/usr/bin/env python3

import re
import os
from colorama import Fore, Style, init

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

if __name__ == "__main__":
    # Try to get latest profile HTML file
    html_file = get_latest_profile_html()
    if html_file:
        print(f"\n{Fore.CYAN}Processing latest profile HTML:{Style.RESET_ALL} {html_file}")
        count = extract_post_count(html_file, debug=True)
        if count is not None:
            print(f"\n{Fore.GREEN}Post count:{Style.RESET_ALL} {count:,}")
        else:
            print(f"\n{Fore.RED}Could not extract post count{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}No profile HTML files found{Style.RESET_ALL}")
