from .quick_sort import quick_sort
from .binary_search import binary_search

def find_obj(lst, key, target, start, lst_len):
    quick_sort(lst, key, start, lst_len - 1)

    found_obj = binary_search(lst, key, target, start, lst_len - 1)

    if found_obj > -1:
        return lst[found_obj]
    return None