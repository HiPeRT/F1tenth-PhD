import math



def mean_filter(ranges, n=10):
    """Apply a mean filter to smooth the ranges.
    
    Args:
        ranges: List of range measurements
        n: Window size for mean filter (default: 10)
    
    Returns:
        Filtered ranges list
    """
    filtered_ranges = list(ranges)
    for i in range(len(filtered_ranges)):
        if i > n and i < len(filtered_ranges) - n and filtered_ranges[i] != 0.0:
            tot = 0
            for k in range(i - n, i + n + 1):
                tot += filtered_ranges[k]
            filtered_ranges[i] = tot / ((2 * n) + 1)
    
    return filtered_ranges


def restrict_fov(ranges, data, fov_deg=120.0):
    restricted_ranges = list(ranges)
    half = math.radians(fov_deg / 2.0)
    start = max(0, int((-half - data.angle_min) / data.angle_increment))
    end = min(len(restricted_ranges), int((half - data.angle_min) / data.angle_increment))
    
    for i in range(0, start):
        restricted_ranges[i] = 0.0
    for i in range(end, len(restricted_ranges)):
        restricted_ranges[i] = 0.0
    
    return restricted_ranges, start, end

def add_margin(ranges, margin=0.1):
    adjusted_ranges = list(ranges)
    for i in range(len(adjusted_ranges)):
        if adjusted_ranges[i] > 0.0:
            adjusted_ranges[i] -= margin
            if adjusted_ranges[i] < 0.0:
                adjusted_ranges[i] = 0.0
    return adjusted_ranges

def propagate_corners(ranges, angle_increment,
                      car_half_width=0.15, margin=0.10,
                      disp_thresh=0.3, min_near=0.5):
    """Extend wall corners by the car half-width. After a forward extension,
    resume past the flattened region so it can't re-trigger a chain."""
    safety = car_half_width + margin
    r = list(ranges)
    n = len(r)

    i = 0
    while i < n - 1:
        a, b = r[i], r[i + 1]
        if not (math.isfinite(a) and math.isfinite(b)) or abs(a - b) <= disp_thresh:
            i += 1
            continue
        near = min(a, b)
        if near < min_near:
            i += 1
            continue

        spread = int(math.ceil(math.atan2(safety, near) / angle_increment))

        if a > b:
            # near side is i+1; smear LEFT over the open region behind us
            for k in range(max(0, i + 1 - spread), i + 1):
                r[k] = min(r[k], near)
            i += 1                       # region is behind us; nothing to skip
        else:
            # near side is i; smear RIGHT over the open region ahead
            hi = min(n, i + 1 + spread)
            for k in range(i + 1, hi):
                r[k] = min(r[k], near)
            i = hi                       # resume past it; r[hi] stays original
    return r