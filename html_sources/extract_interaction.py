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
            
        pattern = f'"{interaction_type}":(\d+)'
        if debug:
            print(f"\n{Fore.CYAN}Step 2: Pattern matching{Style.RESET_ALL}")
            print(f"Using pattern: {pattern}")
        
        # Print context around any potential match
        index = content.find(interaction_type)
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
            
        match = re.search(pattern, content)
        if match:
            result = int(match.group(1))
            if debug:
                print(f"\n{Fore.GREEN}Success: Found match!{Style.RESET_ALL}")
                print(f"Value: {result:,}")
            return result
            
        if debug:
            print(f"\n{Fore.RED}Error: No match found for pattern: {pattern}{Style.RESET_ALL}")
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
