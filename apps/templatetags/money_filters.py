from django import template
import re

register = template.Library()

@register.filter
def remove_money(value):
    if isinstance(value, str):
        # Remove all currency values and symbols
        return re.sub(r'[\d,]+(?:\.\d+)?\s*(?:TZS|USD|\$)?', '', value).strip()
    return str(value)

@register.filter
def calculate_total(requirements):
    total = 0
    for value in requirements.values():
        if isinstance(value, (list, tuple)):
            for item in value:
                total += extract_money_from_string(str(item))
        else:
            total += extract_money_from_string(str(value))
    return total

def extract_money_from_string(text):
    matches = re.findall(r'(\d[\d,]*\.?\d*)', text)
    return sum(float(match.replace(',', '')) for match in matches) if matches else 0