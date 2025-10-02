import json
import os
from dotenv import load_dotenv

def desmos_loader(input_file, output_file='desmos_loader.html', template_file='desmos_loader.html'):
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('DESMOS_API_KEY')
    if not api_key:
        raise ValueError("DESMOS_API_KEY not found in environment variables. Please check your .env file.")
    
    # Read equations from input file
    with open(input_file, 'r') as f:
        equations = f.readlines()

    clean_equations = [eq.strip() for eq in equations if eq.strip()]

    # Read HTML template
    with open(template_file, 'r') as f:
        html_template = f.read()
    
    # Replace placeholders in template
    html_content = html_template.replace('{{DESMOS_API_KEY}}', api_key)
    html_content = html_content.replace('{{EQUATIONS_JSON}}', json.dumps(clean_equations))

    # Write the final HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    try:
        desmos_loader('durga_scaled_equations.txt', 'desmos_output.html')
        print(f"Created desmos_output.html")
        print("Open this file in a browser to view the equations")
    except Exception as e:
        print(f"Error: {e}")
