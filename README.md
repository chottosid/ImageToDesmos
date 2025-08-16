# ImageToDesmos

Convert images to mathematical equations that can be visualized in Desmos graphing calculator.

## Quick Start (Recommended)

### One-Step Conversion

Use the integrated module for the easiest experience:

```bash
python image_to_desmos.py <image_name>
```

Example:

```bash
python image_to_desmos.py reimann.jpg
```

This will automatically:

1. Convert your image to mathematical equations
2. Generate a Desmos HTML viewer
3. Open the result in your browser

**Options:**

- `--segment-size 50` - Adjust curve precision (smaller = more detailed, more time to execute)
- `--no-browser` - Don't auto-open in browser

## Manual Process

If you prefer step-by-step control:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Convert Image to Equations

Place your image file in the project directory and run:

```bash
python to_eq.py <image_name>
```

Example:

```bash
python to_eq.py reimann.jpg
```

The script will generate:

- `<image_name>_equations.txt` - Mathematical equations representing your image (e.g., `reimann_equations.txt`)
- `contours.jpg` - Processed contour image(upside down)

### 3. Visualize in Desmos

Generate an HTML file to automatically load equations into Desmos:

```python
python desmos_loader.py
```

This creates `desmos_loader.html`. Open this file in your web browser and click "Start Animation" to see your image recreated with mathematical curves in Desmos.

## What It Does

1. **Image Processing**: Converts images to grayscale, applies edge detection, and extracts contours
2. **Mathematical Conversion**: Fits cubic Bézier curves to image contours
3. **Desmos Integration**: Generates equations compatible with Desmos graphing calculator
4. **Visualization**: Creates an interactive HTML page for viewing results
