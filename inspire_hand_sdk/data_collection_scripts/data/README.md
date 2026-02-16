# Inspire Hand Tactile Data

This directory contains raw tactile sensor data collected from the Inspire Hand gripper.

## Folder Structure

Each subfolder corresponds to a single recording session.

Example session names:

```
inspire_gripper_session_02_16_26_132345(smoothon)
inspire_gripper_session_02_16_26_132725(silicone_cup)
inspire_gripper_session_02_16_26_133015(lipo_battery)
inspire_gripper_session_02_16_26_134415
```

Naming convention:

```
inspire_gripper_session_MM_DD_YY_HHMMSS(optional_label)
```

- The timestamp indicates when the session was recorded.
- The optional label (in parentheses) describes the object or condition being tested.

Each folder contains CSV files corresponding to individual tactile sensors on the hand.

Example contents:

```
fingerone_palm_touch.csv
fingerone_tip_touch.csv
fingerone_top_touch.csv
fingertwo_palm_touch.csv
fingertwo_tip_touch.csv
fingertwo_top_touch.csv
fingerthree_palm_touch.csv
fingerthree_tip_touch.csv
fingerthree_top_touch.csv
fingerfour_palm_touch.csv
fingerfour_tip_touch.csv
fingerfour_top_touch.csv
fingerfive_middle_touch.csv
fingerfive_palm_touch.csv
fingerfive_tip_touch.csv
fingerfive_top_touch.csv
palm_touch.csv
```

## File Format

Each CSV file contains time-series tactile readings from a single sensor region.

### First Line

The first line specifies the dimensions of the tactile array:

```
rows,cols
```

Example:

```
8,8
```

### Remaining Lines

- Each subsequent row is one time step.
- Each row contains a flattened 2D tactile frame.
- Reshape each row using the dimensions from the first line to recover the original array.

## Summary

- One folder = one experiment session  
- One CSV file = one tactile sensor region  
- First line = sensor dimensions  
- Each subsequent line = one tactile frame  

All files within a session correspond to synchronized data collected during the same experiment.
