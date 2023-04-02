# convert the bin interval column to a string label
def bin_label(bin_interval):
    left, right = bin_interval.left, bin_interval.right
    return f'{left:.0f}-{right:.0f}'