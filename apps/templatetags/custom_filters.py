from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    return str(value).startswith(arg)






# apps/templatetags/custom_filters.py
from django import template
import re
import json
import ast

register = template.Library()

@register.filter
def clean_display(value):
    if isinstance(value, str):
        try:
            # Try to parse JSON if value looks like JSON
            parsed = json.loads(value)
            if isinstance(parsed, (list, dict)):
                return format_parsed_data(parsed)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try to parse Python literals
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, (list, dict, tuple)):
                return format_parsed_data(parsed)
        except (ValueError, SyntaxError):
            pass
        
        # Clean regular strings
        return clean_string(value)
    elif isinstance(value, (list, dict, tuple)):
        return format_parsed_data(value)
    return str(value)

def format_parsed_data(data):
    if isinstance(data, dict):
        return ', '.join(f"{k}: {clean_string(str(v))}" for k, v in data.items())
    elif isinstance(data, (list, tuple)):
        return ', '.join(clean_string(str(item)) for item in data)
    return clean_string(str(data))

def clean_string(s):
    # Remove JSON artifacts and money symbols
    s = re.sub(r'[\{\}\[\]"]', '', s)
    s = re.sub(r'(TZS|USD|\$)\s*\d+[\d,]*\.?\d*', '', s)
    s = re.sub(r'\d+[\d,]*\.?\d*\s*(TZS|USD|\$)', '', s)
    return s.strip()

@register.filter
def calculate_total(requirements):
    total = 0.0
    for value in requirements.values():
        if isinstance(value, (list, tuple)):
            for item in value:
                total += extract_money(item)
        else:
            total += extract_money(value)
    return total

def extract_money(value):
    if isinstance(value, (int, float)):
        return float(value)
    
    str_value = str(value)
    # Find all money values in the string
    matches = re.findall(r'(\d[\d,]*\.?\d*)', str_value)
    if matches:
        return sum(float(match.replace(',', '')) for match in matches)
    return 0.0




register = template.Library()

@register.filter
def split_first(value, delimiter='|'):
    """Split string and return first part"""
    return value.split(delimiter)[0].strip()

@register.filter
def split_last(value, delimiter='|'):
    """Split string and return last part"""
    return value.split(delimiter)[-1].strip()

@register.filter
def has_delimiter(value, delimiter='|'):
    """Check if string contains delimiter"""
    return delimiter in value