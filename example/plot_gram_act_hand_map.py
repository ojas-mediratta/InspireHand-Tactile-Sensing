import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MultipleLocator
import numpy as np
from scipy.ndimage import zoom

from dds_subscribe_485 import DDSHandler
from inspire_sdkpy import inspire_hand_defaut


# =========================
# USER SETTINGS
# =========================
SCALE_G_PER_COUNT = 0.02106959 * 4

MAX_RAW_DATA = 4095

MAX_G_PER_POINT = SCALE_G_PER_COUNT * MAX_RAW_DATA
DISPLAY_VMIN_G = 0.0
DISPLAY_VMAX_G = max(100.0, MAX_G_PER_POINT)

SMOOTHING_FACTOR = 0.0
PAUSE_S = 0.05
# =========================


def pretty_region_name(var: str) -> str:
    """Human-friendly region label for the left-side table.

    IMPORTANT FIX:
    - Only the real palm sensor should be called Palm.
    - Finger sensors like 'fingerthree_palm_touch' must NOT be classified as Palm.
    """
    # Palm (EXACT match only)
    if var == "palm_touch":
        return "Palm"

    # Thumb (fingerfive)
    if "fingerfive" in var:
        if "tip" in var:
            return "Thumb Tip"
        if "top" in var:
            return "Thumb Pad"
        if "mid" in var or "middle" in var:
            return "Thumb Middle"
        if "palm" in var:
            return "Thumb Base"
        return "Thumb"

    # Other fingers
    finger_map = {
        "fingerone": "Pinky",
        "fingertwo": "Ring",
        "fingerthree": "Middle",
        "fingerfour": "Index",
    }
    for k, finger_name in finger_map.items():
        if k in var:
            if "tip" in var:
                return f"{finger_name} Tip"
            if "top" in var:
                return f"{finger_name} Pad"
            if "mid" in var or "middle" in var:
                return f"{finger_name} Mid"
            # NOTE: many vendors call the proximal pad "palm" because it faces palm side
            if "palm" in var:
                return f"{finger_name} Prox"
            return finger_name

    return var


def get_sensor_regions_on_hand():
    """Map each sensor from data_sheet to its location on the hand visualization"""
    data_sheet = inspire_hand_defaut.data_sheet

    # Finger positions: from left (pinky) to right (index)
    finger_base_x = 0.22
    finger_base_y = 0.42
    finger_width = 0.08
    finger_length = 0.4
    finger_spacing = 0.09

    # Thumb position
    thumb_x = 0.59
    thumb_y = 0.20
    thumb_width = 0.08
    thumb_length = 0.35

    # Palm position
    palm_x = 0.22
    palm_y = 0.1
    palm_width = 0.35
    palm_height = 0.3

    regions = {}

    for name, addr, length, size, var in data_sheet:
        x = y = w = h = None

        # ---- Non-thumb fingers
        if 'fingerone' in var or 'fingertwo' in var or 'fingerthree' in var or 'fingerfour' in var:
            if 'fingerone' in var:
                finger_idx = 0
            elif 'fingertwo' in var:
                finger_idx = 1
            elif 'fingerthree' in var:
                finger_idx = 2
            else:
                finger_idx = 3

            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2

            # Tip
            if 'tip' in var:
                w, h = 0.03, 0.03
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length - 0.05

            # Distal pad (top)
            elif 'top' in var:
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.58

            # ✅ NEW: Mid sensor support (many hands have this)
            elif ('mid' in var or 'middle' in var):
                w, h = 0.06, 0.10
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.40

            # Proximal / palm-side segment of the finger
            elif 'palm' in var:
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.20

        # ---- Thumb (fingerfive)
        elif 'fingerfive' in var:
            thumb_center_x = thumb_x + thumb_width / 2
            w = 0.06

            if 'tip' in var:
                h = thumb_length * 0.08
                w = thumb_width * 0.5
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.95

            elif 'top' in var:
                h = 0.08
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.70

            elif ('middle' in var or 'mid' in var):
                h = 0.08
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.43

            elif 'palm' in var:
                h = 0.10
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.10

        # ---- Palm
        elif var == 'palm_touch':
            palm_center_x = (palm_x + palm_width / 2) + 0.05
            w, h = 0.18, 0.16
            x = (palm_center_x - w / 2) - 0.05
            y = palm_y + 0.12

        # If we recognized the sensor, store bbox
        if x is not None:
            regions[var] = {
                'bbox': (x, y, w, h),
                'size': size,
                'name': name
            }

    return regions


def upsample(data, scale=2):
    return zoom(data, zoom=scale, order=1)


def orient_sensor(var, data):
    """Fix sensor matrix orientation so it matches anatomical visualization."""
    if 'finger' in var and 'fingerfive' not in var:
        return np.flipud(data)

    if 'fingerfive' in var:
        return np.flipud(data)

    if var == 'palm_touch':
        return np.rot90(data, k=1)

    return data


def draw_hand_outline(ax):
    """Draw a simplified hand outline"""
    # Palm
    palm = patches.Rectangle((0.23, 0.1), 0.35, 0.3,
                             linewidth=2, edgecolor='black',
                             facecolor='lightgray', alpha=0.2)
    ax.add_patch(palm)

    # Fingers
    finger_width = 0.08
    finger_length = 0.4
    finger_spacing = 0.09
    finger_base_x = 0.22

    for i in range(4):
        x = finger_base_x + i * finger_spacing
        finger = patches.Rectangle((x, 0.41), finger_width, finger_length,
                                   linewidth=2, edgecolor='black',
                                   facecolor='lightgray', alpha=0.2)
        ax.add_patch(finger)

    # Thumb
    thumb_x = 0.59
    thumb_y = 0.20
    thumb_width = 0.08
    thumb_length = 0.37
    thumb = patches.Rectangle((thumb_x, thumb_y), thumb_width, thumb_length,
                              linewidth=2, edgecolor='black',
                              facecolor='lightgray', alpha=0.2)
    ax.add_patch(thumb)


def main():
    dds_handler = DDSHandler(sub_touch=True)
    data_sheet = inspire_hand_defaut.data_sheet

    # Blue->Cyan->Yellow colormap
    colors_blue_yellow = []
    for i in range(256):
        if i < 128:
            r = 0
            g = i / 127.0
            b = 1.0
        else:
            r = (i - 128) / 127.0
            g = 1.0
            b = 1.0 - (i - 128) / 127.0
        colors_blue_yellow.append((r, g, b))
    blue_yellow_cmap = ListedColormap(colors_blue_yellow)

    sensor_regions = get_sensor_regions_on_hand()

    baselines_raw = {}
    smoothed_g = {}

    # Layout: left table + main map
    fig = plt.figure(figsize=(12, 10))
    ax_map = fig.add_axes([0.30, 0.08, 0.68, 0.84])
    ax_info = fig.add_axes([0.02, 0.08, 0.26, 0.84])
    ax_info.axis("off")

    draw_hand_outline(ax_map)

    # Create overlays
    sensor_images = {}
    for name, addr, length, size, var in data_sheet:
        if var in sensor_regions:
            x, y, w, h = sensor_regions[var]['bbox']
            img_data = np.zeros(size, dtype=float)
            extent = [x, x + w, y, y + h]
            im = ax_map.imshow(
                img_data,
                extent=extent,
                origin='lower',
                cmap=blue_yellow_cmap,
                alpha=0.8,
                vmin=DISPLAY_VMIN_G,
                vmax=DISPLAY_VMAX_G,
                interpolation='nearest'
            )
            sensor_images[var] = im

    ax_map.set_xlim(0, 1)
    ax_map.set_ylim(0, 1)
    ax_map.set_aspect('equal')
    ax_map.axis('off')
    ax_map.set_title("Inspire Hand Touch Sensor Map (g per tactile point)",
                     fontsize=16, weight='bold', pad=20)

    sm = plt.cm.ScalarMappable(cmap=blue_yellow_cmap, norm=plt.Normalize(vmin=DISPLAY_VMIN_G, vmax=DISPLAY_VMAX_G))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax_map, orientation='horizontal', pad=0.05, fraction=0.05)
    cbar.set_label(f'Estimated Tactile Value (g)  [k={SCALE_G_PER_COUNT:.8f} g/count]', fontsize=12)
    cbar.locator = MultipleLocator((DISPLAY_VMAX_G - DISPLAY_VMIN_G) / 10.0)
    cbar.update_ticks()

    info_text = ax_info.text(
        0.0, 1.0,
        "Region Loads (g)\n",
        va="top", ha="left",
        fontsize=11,
        family="monospace"
    )

    plt.ion()
    plt.show()

    try:
        while plt.fignum_exists(fig.number):
            data_dict = dds_handler.read()
            touch_data = data_dict.get('touch', {})

            region_total_g = {}
            region_max_g = {}

            for name, addr, length, size, var in data_sheet:
                if var not in touch_data or var not in sensor_images:
                    continue

                sensor_matrix = touch_data[var]
                if sensor_matrix is None or sensor_matrix.size == 0:
                    continue

                if sensor_matrix.shape != size:
                    try:
                        sensor_matrix = sensor_matrix.reshape(size)
                    except Exception:
                        continue

                if var not in baselines_raw:
                    baselines_raw[var] = sensor_matrix.copy()
                    smoothed_g[var] = np.zeros_like(sensor_matrix, dtype=float)

                delta_counts = sensor_matrix - baselines_raw[var]
                delta_counts = np.clip(delta_counts, 0.0, None)

                delta_g = delta_counts * SCALE_G_PER_COUNT

                if SMOOTHING_FACTOR > 0.0:
                    smoothed_g[var] = (SMOOTHING_FACTOR * delta_g +
                                       (1.0 - SMOOTHING_FACTOR) * smoothed_g[var])
                    current_g = smoothed_g[var]
                else:
                    smoothed_g[var] = delta_g.copy()
                    current_g = smoothed_g[var]

                label = pretty_region_name(var)
                region_total_g[label] = region_total_g.get(label, 0.0) + float(np.sum(current_g))
                region_max_g[label] = max(region_max_g.get(label, 0.0), float(np.max(current_g)))

                display_data = orient_sensor(var, current_g)
                if 'fingerfive' in var and ('mid' in var or 'middle' in var):
                    display_data = upsample(display_data, scale=2)

                sensor_images[var].set_data(display_data)
                sensor_images[var].set_clim(DISPLAY_VMIN_G, DISPLAY_VMAX_G)

            # Build left table text (stable order based on what exists this frame)
            # Put Palm first, then fingers.
            preferred_order = [
                "Palm",
                "Index Tip", "Index Pad", "Index Mid", "Index Prox",
                "Middle Tip", "Middle Pad", "Middle Mid", "Middle Prox",
                "Ring Tip", "Ring Pad", "Ring Mid", "Ring Prox",
                "Pinky Tip", "Pinky Pad", "Pinky Mid", "Pinky Prox",
                "Thumb Tip", "Thumb Pad", "Thumb Middle", "Thumb Base",
            ]
            labels_present = list(region_total_g.keys())
            label_order = [x for x in preferred_order if x in labels_present]
            # add any remaining labels not covered
            for x in labels_present:
                if x not in label_order:
                    label_order.append(x)

            lines = []
            lines.append("Region Loads (g)\n")
            lines.append(f"k = {SCALE_G_PER_COUNT:.8f} g/count\n")
            lines.append("-" * 30 + "\n")
            lines.append(f"{'Region':<14}{'Sum(g)':>8}{'Max(g)':>8}\n")
            lines.append("-" * 30 + "\n")
            for label in label_order:
                total = region_total_g.get(label, 0.0)
                mx = region_max_g.get(label, 0.0)
                lines.append(f"{label:<14}{total:>8.1f}{mx:>8.1f}\n")

            info_text.set_text("".join(lines))

            fig.canvas.draw_idle()
            plt.pause(PAUSE_S)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
