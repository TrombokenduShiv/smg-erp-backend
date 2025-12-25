import string

# The alphabet for Base 36: 0-9 then A-Z
BASE36_ALPHABET = string.digits + string.ascii_uppercase

def base36_encode(number):
    """Converts an integer to a Base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')

    if number == 0:
        return '0'

    base36 = ''
    while number != 0:
        number, i = divmod(number, 36)
        base36 = BASE36_ALPHABET[i] + base36

    return base36

def increment_seq(last_seq_str):
    """
    Takes a 3-char string like '001', 'A1Z' and increments it.
    Example: '009' -> '00A', 'ZZY' -> 'ZZZ'
    """
    if not last_seq_str:
        return "001"
    
    # Convert Base36 string back to Integer
    value = int(last_seq_str, 36)
    
    # Increment
    new_value = value + 1
    
    # Convert back to Base36
    new_seq = base36_encode(new_value)
    
    # Pad with zeros to ensure length of 3 (e.g., "A" -> "00A")
    return new_seq.zfill(3)