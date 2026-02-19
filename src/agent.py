
import os
import re
from openai import OpenAI
from lxml import etree

class PLCAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

    def extract_scl(self, xml_content):
        """Extract SCL code from TIA Portal XML export"""
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_content.encode('utf-8'), parser=parser)
            
            # TIA Portal XML uses namespaces, often without a prefix in the file but with a default xmlns
            # We'll use a wildcard to find StatementList tags or handle the root namespace
            ns = root.nsmap.get(None)
            namespaces = {'ns': ns} if ns else {}
            
            scl_blocks = []
            
            # Find all CompileUnits with Language="SCL"
            query = ".//ns:SW.Blocks.CompileUnit[ns:AttributeList/ns:Language='SCL']" if ns else ".//SW.Blocks.CompileUnit[AttributeList/Language='SCL']"
            
            for unit in root.xpath(query, namespaces=namespaces):
                # Extract all tokens from StatementList
                token_query = ".//ns:Token" if ns else ".//Token"
                tokens = unit.xpath(token_query, namespaces=namespaces)
                scl_code = "".join([t.get("Text", "") for t in tokens])
                if scl_code.strip():
                    scl_blocks.append(scl_code)
            
            if not scl_blocks:
                return None
                
            return "\n\n".join(scl_blocks)
        except Exception as e:
            print(f"Error extracting SCL: {e}")
            return None

    def analyze_xml(self, xml_content, mock=False):
        """Send XML content (or extracted SCL) to LLM for analysis"""
        if mock:
            return "### Mock Analysis\nThis is a mock analysis of the PLC code. The logic appears to be a standard motor start/stop latch."

        scl_content = self.extract_scl(xml_content)
        
        if scl_content:
            content_to_analyze = f"Extracted SCL Code:\n```scl\n{scl_content}\n```"
            print("Successfully extracted SCL for analysis.")
        else:
            content_to_analyze = f"Raw XML Content:\n```xml\n{xml_content}\n```"
            print("Falling back to raw XML analysis.")

        if not self.client:
            self.client = OpenAI(api_key=self.api_key)
        
        prompt = f"""
        You are an expert Siemens PLC programmer. 
        Analyze the following TIA Portal PLC block code.
        Explain what the code does, identify any potential issues, and suggest improvements.
        
        {content_to_analyze}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4", 
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
