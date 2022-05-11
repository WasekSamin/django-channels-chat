def binary_search(lst, key, target, start, end):
    if start > end:
        return -1

    mid = (start + end) // 2

    if lst[mid][key] == target:
        return mid

    if lst[mid][key] > target:
        return binary_search(lst, key, target, start, mid - 1)

    if lst[mid][key] < target:
        return binary_search(lst, key, target, mid + 1, end)