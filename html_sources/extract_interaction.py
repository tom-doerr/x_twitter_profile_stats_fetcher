#!/usr/bin/env python3

import re

def extract_interaction_count(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    match = re.search(r'"userInteractionCount":(\d+)', content)
    if match:
        count = match.group(1)
        return count
    return None

if __name__ == "__main__":
    result = extract_interaction_count("html_sources/tom_doerr_profile.html")
    if result:
        print(result)
    else:
        print("userInteractionCount not found in file")
