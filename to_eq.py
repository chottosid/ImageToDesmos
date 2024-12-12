import cv2
import numpy as np
from scipy.optimize import minimize
import desmos_loader
class ImageToDesmos:
    def preprocess_image(self, image_path):
        """
        Convert the image to grayscale and extract edges.
        """
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # rotate the image
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ## Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        ## Canny edge detection with adjusted thresholds
        edges = cv2.Canny(gray, 120, 160)  # Edge detection
        return image, edges

    def extract_contours(self, edge_image):
        """
        Extract contours from the edge-detected image.
        """
        contours, _ = cv2.findContours(edge_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def split_contour_into_segments(self, contour, segment_size=10):
        """
        Split a contour into smaller segments of a fixed size.
        """
        segments = []
        for i in range(0, len(contour) - segment_size + 1, segment_size):
            segment = contour[i:i + segment_size]
            segments.append(segment)
        return segments

    def fit_cubic_bezier_curve(self, segment):
        """
        Approximate a segment with a 3rd-degree polynomial Bézier curve.
        """
        segment = segment.reshape(-1, 2)  # Ensure the segment is in 2D form

        # Parameterize the input points with t values in [0, 1]
        N = len(segment)
        t_samples = np.linspace(0, 1, N)

        # Bézier parametric equations
        def bezier(t, P0, P1, P2, P3):
            return (
                (1-t)**3 * P0 +
                3 * (1-t)**2 * t * P1 +
                3 * (1-t) * t**2 * P2 +
                t**3 * P3
            )

        # Error function to minimize
        def bezier_error(control_points):
            P0 = control_points[0:2]
            P1 = control_points[2:4]
            P2 = control_points[4:6]
            P3 = control_points[6:8]

            error = 0
            for t, target in zip(t_samples, segment):
                bezier_point = bezier(t, P0, P1, P2, P3)
                error += np.linalg.norm(bezier_point - target)**2  # Sum of squared errors
            return error

        # Initial guess for control points (linear approximation)
        P0 = segment[0]
        P3 = segment[-1]
        P1 = P0 + (P3 - P0) / 3
        P2 = P3 - (P3 - P0) / 3
        initial_guess = np.concatenate([P0, P1, P2, P3])

        # Optimize control points
        result = minimize(bezier_error, initial_guess, method='BFGS')
        P0, P1, P2, P3 = result.x[0:2], result.x[2:4], result.x[4:6], result.x[6:8]

        return [P0, P1, P2, P3]

    def generate_cubic_equations(self, bezier_points):
        """
        Generate Desmos-compatible equations for cubic Bézier curves.
        """
        equations = []
        for points in bezier_points:
            P0, P1, P2, P3 = points
            x_eq = f"(1-t)^3*{P0[0]:.4f} + 3*(1-t)^2*t*{P1[0]:.4f} + 3*(1-t)*t^2*{P2[0]:.4f} + t^3*{P3[0]:.4f}"
            y_eq = f"(1-t)^3*{P0[1]:.4f} + 3*(1-t)^2*t*{P1[1]:.4f} + 3*(1-t)*t^2*{P2[1]:.4f} + t^3*{P3[1]:.4f}"
            equations.append(f"({x_eq}, {y_eq})")
        return equations

    def save_equations_to_file(self, equations, output_file="equations.txt"):
        """
        Save the generated equations to a text file.
        """
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n".join(equations))

    def convert_image_to_segments(self, image_path, segment_size=10, output_file="equations.txt", contour_image_file="contours.jpg"):
        """
        Convert an image into cubic Bézier curve segments and generate equations.
        """
        # Preprocess the image
        image, edge_image = self.preprocess_image(image_path)

        # Extract contours
        contours = self.extract_contours(edge_image)

        # Save only the contours as an image
        contour_image = np.zeros_like(image)
        cv2.drawContours(contour_image, contours, -1, (255, 255, 255), 1)
        cv2.imwrite(contour_image_file, contour_image)

        # Split contours into segments
        all_segments = []
        for contour in contours:
            segments = self.split_contour_into_segments(contour, segment_size)
            all_segments.extend(segments)

        # Fit cubic Bézier curves to each segment
        bezier_curves = [self.fit_cubic_bezier_curve(s) for s in all_segments]

        # Generate equations
        equations = self.generate_cubic_equations(bezier_curves)

        # Save equations to file
        self.save_equations_to_file(equations, output_file)

        print(f"Equations saved to {output_file}!")

# Main script
if __name__ == "__main__":
    converter = ImageToDesmos()

    # Specify the image path and output files
    image_path = "archi3.png"  # Replace with your image path
    output_file = "latex_equations.txt"
    contour_image_file = "contours.jpg"  # The output file for the contour image

    # Convert image to Desmos equations and save contour image
    converter.convert_image_to_segments(image_path, segment_size=3, output_file=output_file, contour_image_file=contour_image_file)