import json

def create_desmos_loader(input_file, output_file='desmos_loader.html'):
    """
    Create an HTML file that automatically loads equations into Desmos with animation.

    :param input_file: Text file containing LaTeX equations
    :param output_file: Output HTML file to load equations in Desmos
    """
    with open(input_file, 'r') as f:
        equations = f.readlines()

    clean_equations = [eq.strip() for eq in equations if eq.strip()]

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Desmos Equation Loader</title>
    <script src="https://www.desmos.com/api/v1.10/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6"></script>
</head>
<body>
    <div id="calculator" style="width: 100%; height: 500px;"></div>
    <button id="start-animation" style="margin-top: 10px;">Start Animation</button>
    <script>
        var elt = document.getElementById('calculator');
        var calculator = Desmos.GraphingCalculator(elt);

        // Equations to load
        var equations = {json.dumps(clean_equations)};

        // Current equation index
        var currentIndex = 0;

        // Function to zoom to the proper section
        function zoomToEquation(equation) {{
            calculator.setMathBounds({{
                left: -210, // Adjust these values as per your need
                right: 910,
                bottom: -40,
                top: 500
            }});
        }}

        // Function to show equations one by one with a delay
        function showEquations() {{
            if (currentIndex < equations.length) {{
                calculator.setExpression({{
                    id: `eq_${{currentIndex}}`,
                    latex: equations[currentIndex],
                    hidden: false,
                    color: 'black',  // Set all equations to blue (or any color you prefer)
                    lineWidth: 1  // Set line width to 2 (or any width you prefer)
                }});
                zoomToEquation(equations[currentIndex]);
                currentIndex++;
                setTimeout(showEquations, 1); // Adjust delay (1000ms = 1 second) as needed
            }} else {{
                console.log('All equations are shown!');
            }}
        }}

        // Add event listener to the button
        document.getElementById('start-animation').addEventListener('click', function() {{
            showEquations();
        }});
    </script>
</body>
</html>
    """

    with open(output_file, 'w') as f:
        f.write(html_template)

    print(f"Desmos loader HTML created at {output_file}")
    print("Open this HTML file in a web browser to automatically load equations into Desmos")

if __name__ == "__main__":
    create_desmos_loader('latex_equations.txt')
