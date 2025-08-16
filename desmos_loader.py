import json

def create_desmos_loader(input_file, output_file='desmos_loader.html'):
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

        var equations = {json.dumps(clean_equations)};
        var currentIndex = 0;

        function zoomToEquation() {{
            calculator.setMathBounds({{
                left: -210,
                right: 910,
                bottom: -40,
                top: 500
            }});
        }}

        function showEquations() {{
            if (currentIndex < equations.length) {{
                calculator.setExpression({{
                    id: `eq_${{currentIndex}}`,
                    latex: equations[currentIndex],
                    hidden: false,
                    color: 'black',
                    lineWidth: 1
                }});
                currentIndex++;
                setTimeout(showEquations, 1);
            }}
        }}

        document.getElementById('start-animation').addEventListener('click', function() {{
            zoomToEquation();
            showEquations();
        }});
    </script>
</body>
</html>
    """

    with open(output_file, 'w') as f:
        f.write(html_template)

    print(f"Created {output_file}")
    print("Open this file in a browser to view the equations")

if __name__ == "__main__":
    create_desmos_loader('latex_equations.txt')
