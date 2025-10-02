# ImageToDesmos

Converts images to math equations for Desmos graphing calculator.

## Process

The process involves two steps.


### 1. Convert image

```bash
python to_eq.py <image_name>
```

This creates:
- `<image_name>_equations.txt` - the math equations
- `contours.jpg` - processed edge image (rotated)

(Play around with threshold values in preprocess_image to find best fit)
### 2. View in Desmos

```python
python desmos_loader.py
```

Opens `desmos_loader.html` in your browser. Click "Start Animation" to see your image drawn with math curves.

## How it works

1. Finds edges in your image
2. Fits cubic bezier curves to the edges  
3. Converts curves to Desmos equations
4. Makes an HTML page to view it
