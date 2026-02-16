# Inspire Hand SDK Setup Guide (LIDAR Lab @ GT)

This guide describes the setup and usage of the Inspire Hand SDK for the LIDAR Lab at Georgia Tech.

---

## Virtual Environment Management (Conda)

We use **conda** to manage the Python virtual environment.

### 1. Create and Activate Environment

```bash
conda create -n inspire_hand python=3.8
conda activate inspire_hand
```
---

## Installation

### 1. Clone Repository (if not already done)

```bash
git clone <repo_url>
cd InspireHand-Tactile-Sensing
```

### 2. Initialize and Update Submodules

```bash
git submodule init
git submodule update
```

### 3. Install SDKs (Editable Mode)

⚠️ We **do NOT** use `pip install -r requirements.txt`.

Instead, install the two SDKs in editable mode:

```bash
cd unitree_sdk2_python
pip install -e .

cd ../inspire_hand_sdk
pip install -e .
```

After installation, return to the root directory:

```bash
cd ..
```

---

## Running the Inspire Hands (LIDAR Lab Workflow)

All runtime scripts are located in:

```
/home/lidar/InspireHand-Tactile-Sensing/inspire_hand_sdk/example
```

### ⚠️ Important: Multi-Terminal Setup Required

You must run the driver in **one terminal**, and all visualization or other scripts in **separate terminals**.

---

### Step 1: Start the Headless Driver (Required)

In **Terminal 1**, activate conda and run:

```bash
conda activate inspire_hand
python inspire_hand_sdk/example/Headless_driver_double.py
```

This script:
- Initializes the hands
- Starts DDS communication
- Publishes and subscribes to required topics

***This must remain running before launching any other scripts.***

---

### Step 2: Run Visualization or Other Scripts

In **Terminal 2 (or more terminals)**:

```bash
conda activate inspire_hand
python inspire_hand_sdk/example/plot_force_hand_map_updated.py
```

This script:
- Subscribes to tactile sensor data
- Displays a GUI
- Plots force values on the tactile sensor map

Any additional example scripts should also be run in separate terminals while the driver is active.

---

## Control Modes

The Inspire Hand SDK supports multiple control modes:

- **Mode 0**: `0000` (No operation)  
- **Mode 1**: `0001` (Angle)  
- **Mode 2**: `0010` (Position)  
- **Mode 3**: `0011` (Angle + Position)  
- **Mode 4**: `0100` (Force control)  
- **Mode 5**: `0101` (Angle + Force control)  
- **Mode 6**: `0110` (Position + Force control)  
- **Mode 7**: `0111` (Angle + Position + Force control)  
- **Mode 8**: `1000` (Velocity)  
- **Mode 9**: `1001` (Angle + Velocity)  
- **Mode 10**: `1010` (Position + Velocity)  
- **Mode 11**: `1011` (Angle + Position + Velocity)  
- **Mode 12**: `1100` (Force control + Velocity)  
- **Mode 13**: `1101` (Angle + Force control + Velocity)  
- **Mode 14**: `1110` (Position + Force control + Velocity)  
- **Mode 15**: `1111` (Angle + Position + Force control + Velocity)  

---

## Summary (LIDAR Lab Standard Workflow)

1. Activate conda environment  
2. Start `Headless_driver_double.py` (Terminal 1)  
3. Run GUI or control scripts in separate terminals  
