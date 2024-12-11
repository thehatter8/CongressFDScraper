import zipfile
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

#
#
# https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2024FD.zip
#
#
def convert_zip_xml_to_json(zip_file_path, json_file_path=None):
    """
    Extract XML from a ZIP file, convert multiple members to a JSON array, 
    and sort by filing date from most recent to least recent.
    
    Args:
        zip_file_path (str): Path to the input ZIP file
        json_file_path (str, optional): Path to save the JSON output. 
                                        If not provided, returns JSON as a string.
    
    Returns:
        str: JSON array representation of XML members, sorted by filing date
    """
    # Open the ZIP file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Get list of files in the ZIP
        xml_files = [f for f in zip_ref.namelist() if f.lower().endswith('.xml')]
        
        # Check if exactly one XML file exists
        if len(xml_files) != 1:
            raise ValueError(f"Expected exactly one XML file in the ZIP, found {len(xml_files)}")
        
        # Extract the XML file
        xml_filename = xml_files[0]
        
        # Read the XML content
        with zip_ref.open(xml_filename) as xml_file:
            # Parse the XML content
            tree = ET.parse(xml_file)
            root = tree.getroot()
    
    # Convert XML member to a dictionary
    def xml_member_to_dict(member):
        member_dict = {}
        for child in member:
            # If the child has no children, store its text
            if len(child) == 0:
                # Store empty string instead of None for empty elements
                member_dict[child.tag] = child.text or ""
            else:
                # Recursively process child elements
                member_dict[child.tag] = xml_member_to_dict(child)
        return member_dict
    
    # Convert all members to a list of dictionaries
    members = []
    for member in root.findall('.//Member'):
        member_dict = xml_member_to_dict(member)
        members.append(member_dict)
    
    # Sort members by filing date (most recent first)
    def parse_filing_date(member):
        try:
            # Parse the date in the format 'M/D/YYYY'
            return datetime.strptime(member['FilingDate'], '%m/%d/%Y')
        except (KeyError, ValueError):
            # If date parsing fails, put it at the end
            return datetime.min
    
    sorted_members = sorted(members, key=parse_filing_date, reverse=True)
    
    # Convert to JSON
    json_data = json.dumps(sorted_members, indent=2)
    
    # If a json file path is provided, write to file
    if json_file_path:
        with open(json_file_path, 'w') as f:
            f.write(json_data)
    
    return json_data

# Example usage
if __name__ == "__main__":
    # Convert ZIP containing XML to JSON and print
    input_zip = "C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\2024FD.zip"
    output_json = "C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\financial_disclosure.json"
    
    # Convert and optionally save to file
    json_output = convert_zip_xml_to_json(input_zip, output_json)
    print(f"Converted and sorted {len(json.loads(json_output))} members")
    
    # Print the first few filing dates to verify sorting
    parsed_output = json.loads(json_output)
    for member in parsed_output[:5]:  # Print first 5 members
        print(f"Filing Date: {member['FilingDate']}")