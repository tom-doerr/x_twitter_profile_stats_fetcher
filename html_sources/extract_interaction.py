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
            print(f"\n{Fore.CYAN}DEBUG: Opening file {html_file}{Style.RESET_ALL}")
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if debug:
            print(f"{Fore.CYAN}DEBUG: Read {len(content):,} characters{Style.RESET_ALL}")
            
        pattern = f'"{interaction_type}":(\d+)'
        if debug:
            print(f"{Fore.CYAN}DEBUG: Searching for pattern: {pattern}{Style.RESET_ALL}")
        
        # Print 100 chars around any potential match
        index = content.find(interaction_type)
        if index != -1:
            start = max(0, index - 50)
            end = min(len(content), index + 50)
            context = content[start:end]
            if debug:
                print(f"{Fore.CYAN}DEBUG: Found {interaction_type} context: ...{context}...{Style.RESET_ALL}")
        else:
            if debug:
                print(f"{Fore.RED}DEBUG: {interaction_type} not found in content{Style.RESET_ALL}")
            
        match = re.search(pattern, content)
        if match:
            result = int(match.group(1))
            if debug:
                print(f"{Fore.GREEN}DEBUG: Found match: {result:,}{Style.RESET_ALL}")
            return result
            
        if debug:
            print(f"{Fore.RED}DEBUG: No match found for {interaction_type}{Style.RESET_ALL}")
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
