#!/usr/bin/env python3

import re
import os
from colorama import Fore, Style, init

init()  # Initialize colorama

def extract_interaction(html_file, interaction_type="userInteractionCount", debug=False):
    """
    Extract interaction count from an HTML file.
    
    Args:
        html_file (str): Path to the HTML file to process
        interaction_type (str): Type of interaction to extract (userInteractionCount or statuses_count)
        
    Returns:
        int: The interaction count if found, None otherwise
    """
    try:
        if debug:
            print(f"\n{Fore.CYAN}=== Debug: extract_interaction() ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Input parameters:{Style.RESET_ALL}")
            print(f"- html_file: {html_file}")
            print(f"- interaction_type: {interaction_type}")
            print(f"- debug: {debug}")
            
        if debug:
            print(f"\n{Fore.CYAN}Step 1: Opening file{Style.RESET_ALL}")
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if debug:
            print(f"{Fore.GREEN}Success: Read {len(content):,} characters{Style.RESET_ALL}")
            
        # First look for the raw string without quotes
        index = content.find(interaction_type)
        if debug:
            print(f"\n{Fore.CYAN}Step 2: Initial string search{Style.RESET_ALL}")
            print(f"Searching for raw string: {interaction_type}")
            
        # Try multiple pattern variations
        patterns = [
            f'"{interaction_type}":(\d+)',  # Standard JSON format
            f'{interaction_type}":(\d+)',   # Possible HTML-escaped quotes
            f'{interaction_type}=(\d+)',    # Possible attribute format
        ]
        
        if debug:
            print(f"\n{Fore.CYAN}Step 3: Pattern matching{Style.RESET_ALL}")
            for p in patterns:
                print(f"Trying pattern: {p}")
        if index != -1:
            start = max(0, index - 100)  # Increased context to 100 chars
            end = min(len(content), index + 100)
            context = content[start:end]
            if debug:
                print(f"\n{Fore.CYAN}Step 3: Found search term in content{Style.RESET_ALL}")
                print(f"Position: {index}")
                print(f"Context: ...{context}...{Style.RESET_ALL}")
        else:
            if debug:
                print(f"\n{Fore.RED}Warning: Search term '{interaction_type}' not found in content{Style.RESET_ALL}")
            
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                result = int(match.group(1))
                if debug:
                    print(f"\n{Fore.GREEN}Success: Found match with pattern: {pattern}{Style.RESET_ALL}")
                    print(f"Value: {result:,}")
                return result
            elif debug:
                print(f"{Fore.YELLOW}No match for pattern: {pattern}{Style.RESET_ALL}")
        
        if debug:
            print(f"\n{Fore.RED}Error: No matches found with any pattern{Style.RESET_ALL}")
            print("Returning None")
        return None
    except Exception as e:
        print(f"Error processing {html_file}: {str(e)}")
        return None

def get_latest_profile_html(directory="html_sources"):
    """
    Get the most recent profile HTML file from the directory.
    
    Args:
        directory (str): Directory to search in
        
    Returns:
        str: Path to the most recent profile HTML file, or None if none found
    """
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
    latest_file = get_latest_profile_html()
    if latest_file:
        result = extract_interaction(latest_file)
        if result:
            print(result)
        else:
            print("userInteractionCount not found in file")
    else:
        print("No profile HTML files found")
