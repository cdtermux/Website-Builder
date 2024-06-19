import os
import random
import string
import re
from asyncio import WindowsSelectorEventLoopPolicy
import asyncio
from g4f.client import Client

# Set the event loop policy to WindowsSelectorEventLoopPolicy for compatibility with Windows
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

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

# Initialize the client
client = Client()

def main():
    while True:
        # Get user input
        prompt = input("Enter your prompt (press 'q' to quit): ")
        
        # Check if the user wants to quit
        if prompt.lower() == 'q':
            break
        
        # Append additional requirements to the prompt
        prompt += ''' Please answer only in simplified English and do not use any Chinese words in your response. Create a web page with HTML and Tailwind CSS, including the CDN. Ensure a beautiful layout with necessary sections. Use linear gradient colors, images from Unsplash if needed only ("For using Unsplash images, use the following code snippet in your JavaScript:
const response = await fetch('https://api.unsplash.com/photos/random/?query=required_query_here', {
    headers: {
        Authorization: `Client-ID ${accessKey}`
    }
}); Replace 'required_query_here' with your desired query for the image in the webpage.
Also, ensure to add the following line at the beginning of your generated 'script.js' file:
const accessKey = 'RmhCkkuNwBE12HKmv3XwasWBaB_Z7U7mzP5EaZTqPt4';  and use them correctly to manage the layout of web page"), and vibrant design elements. Make the page broad, techy, and visually engaging with rich colors and a modern aesthetic. Add the required JavaScript to make the page work functionally with all necessary functionalities, use localstorage for storage uses. Use Tailwind classes in the HTML and add extra plain CSS for any additional enhancements. Provide the complete HTML, CSS, and JavaScript code separately.'''
        
        # Create a variable to track if we need to retry
        retry = True
        
        while retry:
            # Get the response from the API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Get the response content
            response_content = response.choices[0].message.content
            
            # Print the response
            print("Debug: API response received.\n")
            print(response_content)
            
            # Check if response indicates IP blocking
            if "您的ip已由于触发防滥用检测而被封禁" in response_content:
                print("Response indicates IP block. Retrying...")
            else:
                # No IP block, continue with normal processing
                retry = False
                
                # Extract the code sections from the response
                code_sections = extract_code_sections(response_content)
                
                # Generate a random folder name
                folder_name = generate_random_folder_name()
                
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
                    
                    html_file.write(html_content)
                
                # Write CSS content to styles.css
                with open(os.path.join(folder_name, 'styles.css'), 'w', encoding='utf-8') as css_file:
                    css_file.write(code_sections["css"])
                
                # Write JavaScript content to script.js
                with open(os.path.join(folder_name, 'script.js'), 'w', encoding='utf-8') as js_file:
                    js_file.write(code_sections["js"])
                
                print(f"Files have been created in the folder: {folder_name}")

if __name__ == "__main__":
    main()
