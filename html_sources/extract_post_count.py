#!/usr/bin/env python3

import re
from colorama import Fore, Style, init

init()  # Initialize colorama

def extract_post_count_from_text(text, debug=False):
    """
    Extract post count from text like "10K posts" or "1,234 posts"
    
    Args:
        text (str): Text containing post count
        debug (bool): Enable debug output
        
    Returns:
        int: The post count if found, None otherwise
    """
    if debug:
        print(f"\n{Fore.CYAN}=== Debug: extract_post_count_from_text() ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Input text:{Style.RESET_ALL} {text}")

    if not text:
        if debug:
            print(f"{Fore.RED}Error: Input text is empty{Style.RESET_ALL}")
        return None

    # Pattern matches numbers with optional comma and K/M/B suffix followed by "posts"
    pattern = r'([\d,]+(?:\.\d+)?[KMB]?)\s*posts'
    
    if debug:
        print(f"{Fore.YELLOW}Using pattern:{Style.RESET_ALL} {pattern}")
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        count_text = match.group(1)
        if debug:
            print(f"{Fore.GREEN}Found match:{Style.RESET_ALL} {count_text}")
        
        # Handle K/M/B suffixes
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        # Remove commas and convert to number
        base_number = count_text.replace(',', '')
        
        # Check for suffix
        for suffix, multiplier in multipliers.items():
            if suffix in base_number.upper():
                try:
                    number = float(base_number.upper().replace(suffix, '')) * multiplier
                    if debug:
                        print(f"{Fore.GREEN}Converted {count_text} to {int(number):,}{Style.RESET_ALL}")
                    return int(number)
                except ValueError:
                    if debug:
                        print(f"{Fore.RED}Error converting number with suffix{Style.RESET_ALL}")
                    return None
        
        # No suffix, just convert the number
        try:
            number = int(float(base_number))
            if debug:
                print(f"{Fore.GREEN}Converted {count_text} to {number:,}{Style.RESET_ALL}")
            return number
        except ValueError:
            if debug:
                print(f"{Fore.RED}Error converting number without suffix{Style.RESET_ALL}")
            return None
    
    if debug:
        print(f"{Fore.RED}No match found in text{Style.RESET_ALL}")
    return None

if __name__ == "__main__":
    # Test cases
    test_texts = [
        "10K posts",
        "1,234 posts",
        "1.5M posts",
        "500 posts",
        "Invalid text",
        None
    ]
    
    for text in test_texts:
        result = extract_post_count_from_text(text, debug=True)
        print(f"\nTest result for '{text}': {result:,}" if result else f"\nTest result for '{text}': None")
