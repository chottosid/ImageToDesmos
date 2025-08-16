"""
Image to Desmos Converter

This module converts images to Desmos equations
and generates the HTML viewer in one step.

Usage:
    python image_to_desmos.py <image_path> [options]
"""

import sys
import os
import argparse
from to_eq import ImageToDesmos
from desmos_loader import create_desmos_loader


class IntegratedImageToDesmos:
    """
    Integrated converter that combines image processing and Desmos HTML generation.
    """
    
    def __init__(self):
        self.converter = ImageToDesmos()
    
    def process_image_to_desmos(self, image_path, segment_size=20, open_browser=True):
        # Validate input
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found.")
        
        # Generate output file names
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        equations_file = f"{image_name}_equations.txt"
        contours_file = "contours.jpg"
        html_file = f"{image_name}_desmos.html"
        
        print(f"🔄 Processing image: {image_path}")
        
        print("Converting image to mathematical equations")
        self.converter.convert_image_to_segments(
            image_path, 
            segment_size=segment_size, 
            output_file=equations_file, 
            contour_image_file=contours_file
        )
        
        print("Generating Desmos HTML viewer")
        create_desmos_loader(equations_file, html_file)
        
        results = {
            'input_image': image_path,
            'equations_file': equations_file,
            'contours_file': contours_file,
            'html_file': html_file
        }
        
        print("Conversion completed successfully")
        print(f"Equations: {equations_file}")
        print(f"Contours: {contours_file}")
        print(f"Desmos HTML: {html_file}")
        
        # Optional: Try to open the HTML file
        if open_browser:
            self._try_open_browser(html_file)
        
        return results
    
    def _try_open_browser(self, html_file):
        try:
            import webbrowser
            full_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{full_path}')
            print(f"Opening {html_file} in your default browser")
        except Exception as e:
            print(f"Failed opening in browser, Open {html_file} manually")


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to Desmos equations with HTML viewer",
        epilog="Example: python image_to_desmos.py jagannath.jpg --segment-size 10"
    )
    
    parser.add_argument(
        "image_path",
        help="Path to the input image file"
    )
    
    parser.add_argument(
        "--segment-size", "-s",
        type=int,
        default=20,
        help="Size of curve segments for fitting (default: 20, smaller = more detailed)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't attempt to open the HTML file in browser"
    )
    
    args = parser.parse_args()
    
    try:
        converter = IntegratedImageToDesmos()
        results = converter.process_image_to_desmos(
            args.image_path,
            segment_size=args.segment_size,
            open_browser=not args.no_browser
        )
        
        print(f"Image has been converted to Desmos equations")
        print(f"Generated files:")
        for key, value in results.items():
            if key != 'input_image':
                print(f"\t{value}")
                
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
