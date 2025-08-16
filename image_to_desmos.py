import sys
import os
import argparse
from to_eq import ImageToDesmos
from desmos_loader import create_desmos_loader


class IntegratedImageToDesmos:
    
    def __init__(self):
        self.converter = ImageToDesmos()
    
    def process_image_to_desmos(self, image_path, segment_size=20, open_browser=True):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found.")
        
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        equations_file = f"{image_name}_equations.txt"
        contours_file = "contours.jpg"
        html_file = f"{image_name}_desmos.html"
        
        print(f"Processing image: {image_path}")
        
        print("Converting to equations...")
        self.converter.convert_image_to_segments(
            image_path, 
            segment_size=segment_size, 
            output_file=equations_file, 
            contour_image_file=contours_file
        )
        
        print("Creating HTML viewer...")
        create_desmos_loader(equations_file, html_file)
        
        results = {
            'input_image': image_path,
            'equations_file': equations_file,
            'contours_file': contours_file,
            'html_file': html_file
        }
        
        print("Done!")
        print(f"Equations: {equations_file}")
        print(f"Contours: {contours_file}")
        print(f"HTML: {html_file}")
        
        if open_browser:
            self._try_open_browser(html_file)
        
        return results
    
    def _try_open_browser(self, html_file):
        try:
            import webbrowser
            full_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{full_path}')
            print(f"Opening {html_file} in browser")
        except Exception as e:
            print(f"Couldn't open browser, open {html_file} manually")


def main():
    parser = argparse.ArgumentParser(description="Convert images to Desmos equations")
    
    parser.add_argument("image_path", help="Path to the input image file")
    
    parser.add_argument(
        "--segment-size", "-s",
        type=int,
        default=20,
        help="Curve segment size (default: 20, smaller = more detail)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open the HTML file automatically"
    )
    
    args = parser.parse_args()
    
    try:
        converter = IntegratedImageToDesmos()
        results = converter.process_image_to_desmos(
            args.image_path,
            segment_size=args.segment_size,
            open_browser=not args.no_browser
        )
        
        print(f"Converted image to Desmos")
        print(f"Files created:")
        for key, value in results.items():
            if key != 'input_image':
                print(f"\t{value}")
                
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
