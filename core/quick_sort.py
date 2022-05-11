def quick_sort(lst, key, start, end):
    if start >= end:
        return

    get_index = partition(lst, key, start, end)

    quick_sort(lst, key, start, get_index - 1)
    quick_sort(lst, key, get_index + 1, end)


def partition(lst, key, start, end):
    pivot_index = start
    pivot_val = lst[end][key]

    for i in range(start, end):
        if lst[i][key] < pivot_val:
            lst[i], lst[pivot_index] = lst[pivot_index], lst[i]

    lst[pivot_index], lst[end] = lst[end], lst[pivot_index]

    return pivot_index