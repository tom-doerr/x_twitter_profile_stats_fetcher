#!/usr/bin/env python3

import re
import os

def extract_interaction(html_file, interaction_type="userInteractionCount"):
    """
    Extract interaction count from an HTML file.
    
    Args:
        html_file (str): Path to the HTML file to process
        interaction_type (str): Type of interaction to extract (userInteractionCount or statuses_count)
        
    Returns:
        int: The interaction count if found, None otherwise
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pattern = f'"{interaction_type}":(\d+)'
        match = re.search(pattern, content)
        if match:
            return int(match.group(1))
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
