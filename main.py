import os
import random
import string
import re
from asyncio import WindowsSelectorEventLoopPolicy
import asyncio
from g4f.client import Client

# Set the event loop policy to WindowsSelectorEventLoopPolicy
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Function to generate a random folder name
def generate_random_folder_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to extract code sections from the response
def extract_code_sections(response):
    sections = {"html": "", "css": "", "js": ""}
    
    # Regular expressions to match code blocks
    html_pattern = re.compile(r'```html(.*?)```', re.DOTALL)
    css_pattern = re.compile(r'```css(.*?)```', re.DOTALL)
    js_pattern = re.compile(r'```javascript(.*?)```', re.DOTALL)
    
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

# List to store the conversation history
conversation_history = []

def main():
    while True:
        # Get user input
        prompt = input("Enter your prompt (press 'q' to quit): ") + ' answer only in simplified english only do not add any chineese word in the response'
        
        # Check if the user wants to quit
        if prompt.lower() == 'q':
            break
        
        # Add the user input to the conversation history
        conversation_history.append({"role": "user", "content": prompt})
        
        # Get the response from the API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        
        # Get the response content
        response_content = response.choices[0].message.content
        
        # Add the assistant response to the conversation history
        conversation_history.append({"role": "assistant", "content": response_content})
        
        # Print the response
        print(response_content)
        
        # Extract the code sections from the response
        code_sections = extract_code_sections(response_content)
        
        # Generate a random folder name
        folder_name = generate_random_folder_name()
        
        # Create the folder
        os.makedirs(folder_name, exist_ok=True)
        
        # Write HTML content to index.html
        with open(os.path.join(folder_name, 'index.html'), 'w', encoding='utf-8') as html_file:
            html_file.write(code_sections["html"])
        
        # Write CSS content to styles.css
        with open(os.path.join(folder_name, 'styles.css'), 'w', encoding='utf-8') as css_file:
            css_file.write(code_sections["css"])
        
        # Write JavaScript content to script.js
        with open(os.path.join(folder_name, 'script.js'), 'w', encoding='utf-8') as js_file:
            js_file.write(code_sections["js"])
        
        print(f"Files have been created in the folder: {folder_name}")

if __name__ == "__main__":
    main()
