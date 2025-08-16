# ImageToDesmos

Converts images to math equations for Desmos graphing calculator.

## Quick Start

Just run this:

```bash
python image_to_desmos.py <image_name>
```

Example:

```bash
python image_to_desmos.py reimann.jpg
```

This does everything - converts your image to equations, makes an HTML viewer, and opens it in your browser.

**Options:**
- `--segment-size 50` - adjust precision (smaller = more detail, takes longer)
- `--no-browser` - don't auto-open browser

## Manual Process

If you want more control:

### 1. Install stuff

```bash
pip install -r requirements.txt
```

### 2. Convert image

```bash
python to_eq.py <image_name>
```

This creates:
- `<image_name>_equations.txt` - the math equations
- `contours.jpg` - processed edge image (rotated)

### 3. View in Desmos

```python
python desmos_loader.py
```

Opens `desmos_loader.html` in your browser. Click "Start Animation" to see your image drawn with math curves.

## How it works

1. Finds edges in your image
2. Fits cubic bezier curves to the edges  
3. Converts curves to Desmos equations
4. Makes an HTML page to view it
