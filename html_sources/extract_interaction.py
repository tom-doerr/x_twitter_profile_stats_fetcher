#!/usr/bin/env python3

import re

def extract_interaction_count(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    match = re.search(r'userInteractionCount[^"\']*?([^"\']{10})', content)
    if match:
        return match.group(1)
    return None

if __name__ == "__main__":
    result = extract_interaction_count("html_sources/tom_doerr_profile.html")
    if result:
        print(f"10 chars after userInteractionCount: {result}")
    else:
        print("userInteractionCount not found in file")
