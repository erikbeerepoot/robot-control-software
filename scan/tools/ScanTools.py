from matplotlib.pyplot import figure, show

def plot_scan(scan):
    if scan is None:
        return

    # force square figure and square axes looks better for polar, IMO
    fig = figure(figsize=(8, 8))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection='polar')

    N = len(scan.payload)

    ranges = []
    angles = []
    for step in range(0, N):
        r = scan.payload[step]
        angle = scan.get_scan_angle(step)
        ranges.append(r)
        angles.append(angle)

    bars = ax.bar(angles, ranges, width=0.01, bottom=0.0)
    for bar in bars:
        bar.set_facecolor('b')
        bar.set_alpha(0.5)

    show()
