from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import random
import string
import re
from g4f.client import Client
from asyncio import WindowsSelectorEventLoopPolicy
import asyncio

# Set the event loop policy to WindowsSelectorEventLoopPolicy for compatibility with Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

app = Flask(__name__)

# Function to generate a random folder name
def generate_random_folder_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to extract code sections from the response
def extract_code_sections(response):
    sections = {"html": "", "css": "", "js": ""}
    
    # Regular expressions to match code blocks
    html_pattern = re.compile(r'```html:?(.*?)```', re.DOTALL | re.IGNORECASE)
    css_pattern = re.compile(r'```css:?(.*?)```', re.DOTALL | re.IGNORECASE)
    js_pattern = re.compile(r'```javascript(.*?)```', re.DOTALL | re.IGNORECASE)
    
    # Search for HTML, CSS, JS code blocks
    html_match = html_pattern.search(response)
    css_match = css_pattern.search(response)
    js_match = js_pattern.search(response)
    
    if html_match:
        sections["html"] = html_match.group(1).strip()
    if css_match:
        sections["css"] = css_match.group(1).strip()
    if js_match:
        sections["js"] = js_match.group(1).strip()
    
    return sections

# Function to check if HTML contains multiple "here" words in comments
def check_html_comments(html_content):
    # Count occurrences of "here" in comment lines
    comment_lines = re.findall(r'<!--.*?-->', html_content, re.DOTALL)
    count_here = sum(1 for line in comment_lines if "here" in line.lower())
    
    return count_here > 1

# Function to handle the creation and regeneration of files
def create_files(code_sections, folder_name):
    # Create the folder
    os.makedirs(folder_name, exist_ok=True)
    
    # Write HTML content to index.html
    with open(os.path.join(folder_name, 'index.html'), 'w', encoding='utf-8') as html_file:
        html_content = code_sections["html"]
        
        # Check if <head> tag exists and if the stylesheet link is already present
        head_tag_index = html_content.find('</head>')
        if head_tag_index != -1:
            # Check if the <link> tag for the stylesheet is present
            if '<link rel="stylesheet" href="styles.css">' not in html_content:
                # Insert the <link> tag inside <head>
                html_content = html_content[:head_tag_index] + '<link rel="stylesheet" href="styles.css">\n' + html_content[head_tag_index:]
        else:
            # If <head> tag does not exist, just append the <link> tag at the beginning
            html_content = '<link rel="stylesheet" href="styles.css">\n' + html_content
        
        # Check if HTML content needs regeneration
        if check_html_comments(html_content):
            return False
        
        html_file.write(html_content)
    
    # Write CSS content to styles.css
    with open(os.path.join(folder_name, 'styles.css'), 'w', encoding='utf-8') as css_file:
        css_file.write(code_sections["css"])
    
    # Write JavaScript content to script.js
    with open(os.path.join(folder_name, 'script.js'), 'w', encoding='utf-8') as js_file:
        js_file.write(code_sections["js"])
    
    return True

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Function to regenerate code with a modified prompt
def regenerate_code(prompt):
    client = Client()
    retry = True

    while retry:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        response_content = response.choices[0].message.content

        if "您的ip已由于触发防滥用检测而被封禁" in response_content:
            continue
        else:
            retry = False

    return response_content

# Route to generate code
@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    base_prompt = ''' Please answer only in simplified English and do not use any Chinese words in your response. Create a web page with HTML and Tailwind CSS, including the CDN. Ensure a beautiful layout with necessary sections. Use linear gradient colors, and vibrant design elements. Make the page broad, techy, and visually engaging with rich colors and a modern aesthetic. Add the required JavaScript to make the page work functionally with all necessary functionalities, use localstorage for storage uses. Use Tailwind classes in the HTML and add extra plain CSS for any additional enhancements. Provide the complete HTML, CSS, and JavaScript code separately.'''

    prompt += base_prompt

    response_content = regenerate_code(prompt)
    code_sections = extract_code_sections(response_content)

    # Check if HTML content needs regeneration
    if not create_files(code_sections, 'temp_folder'):
        prompt_html = prompt + " Please regenerate HTML, CSS, and JavaScript code."
        response_content = regenerate_code(prompt_html)
        code_sections = extract_code_sections(response_content)

    folder_name = generate_random_folder_name()
    create_files(code_sections, folder_name)

    return jsonify({"folder": folder_name})

# Route to serve the generated files
@app.route('/view/<folder>/<path:filename>')
def view(folder, filename):
    return send_from_directory(folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
