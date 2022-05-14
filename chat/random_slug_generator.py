import string
import random
from core.find_object import find_obj

# Create random room slug of chatroom
def random_slug_generator(lst, key, size=20, chars=string.ascii_letters + string.digits):
    random_val = ''.join(random.choice(chars) for _ in range(size))

    found_obj = find_obj(lst, key, random_val, 0, len(lst))

    # If the found object already exists, make the function run again
    if found_obj is not None:
        return random_slug_generator(lst, key, size=20, chars=string.ascii_letters + string.digits)
    return random_val