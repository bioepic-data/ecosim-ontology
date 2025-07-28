"""
Convert bervo fortran code to parameters.

This code was authored by ChatGPT: https://chat.openai.com/share/e6e723ec-ea87-44ac-b728-c919a568325a

You can use the code by setting directory_path to the path of your Fortran directory and then calling the traverse_and_extract_parameters function. The function will return a list of dictionaries containing the extracted parameters, their descriptions, and units.
"""
import os
import re

def extract_parameters_from_file(file_path):
    """
    Extract parameters, descriptions, and units from a Fortran file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression pattern to capture potential parameter declarations
    pattern = r"\breal\(r8\)\s*,\s*target\s*,\s*allocatable\s*::\s*(\w+)\s*(?:\((.*?)\))?\s*!\s*(.*?)\s*,\s*\[(.*?)\]"
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    # Extract parameters, descriptions, and units
    extracted_data = [{"variable_name": match[0].strip(),
                       "description": match[2].strip(),
                       "units": match[3].strip()}
                      for match in matches]
    
    return extracted_data

def traverse_and_extract_parameters(directory_path):
    """
    Traverse through a directory and extract parameters from all Fortran files.
    """
    extracted_params = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.F90'):
                file_path = os.path.join(root, file)
                extracted_params.extend(extract_parameters_from_file(file_path))
                
    return extracted_params

# Usage:
# directory_path = "path_to_your_fortran_directory"
# extracted_parameters = traverse_and_extract_parameters(directory_path)
