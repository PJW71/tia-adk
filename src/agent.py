
import os
from openai import OpenAI

class PLCAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

    def analyze_xml(self, xml_content, mock=False):
        """Send XML content to LLM for analysis"""
        if mock:
            return "### Mock Analysis\nThis is a mock analysis of the PLC code. The logic appears to be a standard motor start/stop latch."

        if not self.client:
            self.client = OpenAI(api_key=self.api_key)
        
        prompt = f"""
        You are an expert Siemens PLC programmer. 
        Analyze the following TIA Portal XML export of a PLC block.
        Explain what the code does, identify any potential issues, and suggest improvements.
        
        XML Content:
        ```xml
        {xml_content}
        ```
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4", # Or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant proficient in Siemens PLC programming (SCL/STL/LAD)."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    def process_directory(self, input_dir, output_dir, mock=False, limit=None):
        """Process all XML files in a directory"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        count = 0
        for filename in os.listdir(input_dir):
            if limit and count >= limit:
                print(f"Limit of {limit} files reached.")
                break

            if filename.endswith(".xml"):
                full_path = os.path.join(input_dir, filename)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"Analyzing {filename}...")
                analysis = self.analyze_xml(content, mock=mock)
                
                output_file = os.path.join(output_dir, f"{filename}_analysis.md")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(analysis)
                print(f"Saved analysis to {output_file}")
                count += 1
