import cv2
import numpy as np
from scipy.optimize import minimize
import desmos_loader
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

class ImageToDesmos:
    """
    Optimized image-to-Desmos equation converter with:
    - Vectorized Bezier curve calculations for improved performance
    - L-BFGS-B optimizer for more robust and faster convergence
    - Enhanced multithreading with concurrent.futures and error handling
    - Fallback mechanisms for failed optimizations
    """
    def preprocess_image(self, image_path):
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        image = cv2.rotate(image, cv2.ROTATE_180)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 300, 600)
        return image, edges

    def extract_contours(self, edge_image):
        contours, _ = cv2.findContours(edge_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def split_contour_into_segments(self, contour, segment_size=10):
        segments = []
        for i in range(0, len(contour) - segment_size + 1, segment_size):
            segment = contour[i:i + segment_size]
            segments.append(segment)
        return segments

    def bezier(self, t, P0, P1, P2, P3):
        """Calculate point on cubic Bezier curve at parameter t"""
        return (
            (1-t)**3 * P0 +
            3 * (1-t)**2 * t * P1 +
            3 * (1-t) * t**2 * P2 +
            t**3 * P3
        )

    def bezier_vectorized(self, t_samples, P0, P1, P2, P3):
        """Calculate points on cubic Bezier curve for multiple t values (vectorized)"""
        t = t_samples.reshape(-1, 1)  # Shape: (n, 1)
        
        # Pre-calculate powers and coefficients for better performance
        t2 = t * t
        t3 = t2 * t
        one_minus_t = 1 - t
        one_minus_t2 = one_minus_t * one_minus_t
        one_minus_t3 = one_minus_t2 * one_minus_t
        
        # Vectorized calculation for all t values at once
        points = (
            one_minus_t3 * P0 +
            3 * one_minus_t2 * t * P1 +
            3 * one_minus_t * t2 * P2 +
            t3 * P3
        )
        return points  # Shape: (n, 2)

    def bezier_error_vectorized(self, control_points, t_samples, segment):
        """Calculate error between Bezier curve and target segment points (vectorized)"""
        P0 = control_points[0:2]
        P1 = control_points[2:4]
        P2 = control_points[4:6]
        P3 = control_points[6:8]

        # Get all Bezier points at once
        bezier_points = self.bezier_vectorized(t_samples, P0, P1, P2, P3)
        
        # Vectorized error calculation
        differences = bezier_points - segment
        squared_distances = np.sum(differences**2, axis=1)
        total_error = np.sum(squared_distances)
        
        return total_error

    def fit_cubic_bezier_curve(self, segment):
        segment = segment.reshape(-1, 2).astype(np.float64)

        N = len(segment)
        t_samples = np.linspace(0, 1, N)

        # Set up initial control points
        P0 = segment[0]
        P3 = segment[-1]
        P1 = P0 + (P3 - P0) / 3
        P2 = P3 - (P3 - P0) / 3
        initial_guess = np.concatenate([P0, P1, P2, P3])

        # Define bounds to keep control points reasonable (optional but can help convergence)
        min_coord = np.min(segment) - 100
        max_coord = np.max(segment) + 100
        bounds = [(min_coord, max_coord)] * 8  # 8 coordinates (4 points × 2 dimensions)

        # Optimize control points using L-BFGS-B and vectorized error function
        result = minimize(
            lambda control_points: self.bezier_error_vectorized(control_points, t_samples, segment),
            initial_guess, 
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        if not result.success:
            # Fallback to BFGS if L-BFGS-B fails
            result = minimize(
                lambda control_points: self.bezier_error_vectorized(control_points, t_samples, segment),
                initial_guess, 
                method='BFGS',
                options={'maxiter': 1000}
            )
        
        P0, P1, P2, P3 = result.x[0:2], result.x[2:4], result.x[4:6], result.x[6:8]

        return [P0, P1, P2, P3]

    def generate_cubic_equations(self, bezier_points):
        equations = []
        for points in bezier_points:
            P0, P1, P2, P3 = points
            x_eq = f"(1-t)^3*{P0[0]:.4f} + 3*(1-t)^2*t*{P1[0]:.4f} + 3*(1-t)*t^2*{P2[0]:.4f} + t^3*{P3[0]:.4f}"
            y_eq = f"(1-t)^3*{P0[1]:.4f} + 3*(1-t)^2*t*{P1[1]:.4f} + 3*(1-t)*t^2*{P2[1]:.4f} + t^3*{P3[1]:.4f}"
            equations.append(f"({x_eq}, {y_eq})")
        return equations

    def save_equations_to_file(self, equations, output_file="equations.txt"):
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n".join(equations))

    def convert_image_to_segments(self, image_path, segment_size=20, output_file="equations.txt", contour_image_file="contours.jpg"):
        image, edge_image = self.preprocess_image(image_path)
        contours = self.extract_contours(edge_image)

        contour_image = np.zeros_like(image)
        cv2.drawContours(contour_image, contours, -1, (255, 255, 255), 1)
        cv2.imwrite(contour_image_file, contour_image)

        all_segments = []
        for contour in contours:
            segments = self.split_contour_into_segments(contour, segment_size)
            all_segments.extend(segments)

        # Use multithreading to fit cubic Bezier curves with progress tracking
        print(f"Processing {len(all_segments)} segments...")
        
        if len(all_segments) > 1:
            # Determine optimal number of workers
            import os
            max_workers = min(len(all_segments), os.cpu_count() or 1)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks and get futures
                future_to_segment = {
                    executor.submit(self.fit_cubic_bezier_curve, segment): i 
                    for i, segment in enumerate(all_segments)
                }
                
                # Process results with progress bar and error handling
                bezier_curves = [None] * len(all_segments)
                failed_segments = []
                
                for future in tqdm(future_to_segment, desc="Fitting Bezier curves", unit="segment"):
                    segment_index = future_to_segment[future]
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per segment
                        bezier_curves[segment_index] = result
                    except Exception as e:
                        print(f"Warning: Failed to process segment {segment_index}: {e}")
                        failed_segments.append(segment_index)
                        # Use a simple linear approximation as fallback
                        segment = all_segments[segment_index].reshape(-1, 2)
                        P0, P3 = segment[0], segment[-1]
                        P1 = P0 + (P3 - P0) * 0.33
                        P2 = P0 + (P3 - P0) * 0.67
                        bezier_curves[segment_index] = [P0, P1, P2, P3]
                
                # Remove None values (should not happen with fallback)
                bezier_curves = [curve for curve in bezier_curves if curve is not None]
                
                if failed_segments:
                    print(f"Note: {len(failed_segments)} segments used fallback linear approximation")
        else:
            # Fallback to sequential processing for single segment
            try:
                bezier_curves = [self.fit_cubic_bezier_curve(all_segments[0])]
            except Exception as e:
                print(f"Warning: Failed to process segment: {e}")
                segment = all_segments[0].reshape(-1, 2)
                P0, P3 = segment[0], segment[-1]
                P1 = P0 + (P3 - P0) * 0.33
                P2 = P0 + (P3 - P0) * 0.67
                bezier_curves = [[P0, P1, P2, P3]]
        
        equations = self.generate_cubic_equations(bezier_curves)
        self.save_equations_to_file(equations, output_file)

        print(f"Saved {len(equations)} equations to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python to_eq.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)
    
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    output_file = f"{image_name}_equations.txt"
    contour_image_file = "contours.jpg"
    
    converter = ImageToDesmos()
    converter.convert_image_to_segments(image_path, segment_size=10, output_file=output_file, contour_image_file=contour_image_file)
    
    print(f"Image: {image_path}")
    print(f"Equations: {output_file}")
    print(f"Contours: {contour_image_file}")