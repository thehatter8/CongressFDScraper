import json
import os
import requests
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def download_zip_file(year):
    """
    Download the Congressional Financial Disclosure ZIP file for the specified year.
    
    Args:
        year (int): Year of the financial disclosure ZIP file
    
    Returns:
        str: Path to the downloaded ZIP file
    """
    # Construct the URL based on the current year
    url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip"
    
    # Create downloads directory if it doesn't exist
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'CongressionalFDs')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Define the output file path
    output_path = os.path.join(downloads_dir, f'{year}FD.zip')
    
    try:
        # Send a GET request to download the ZIP file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Write the ZIP file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Successfully downloaded {year} Financial Disclosure ZIP file")
        return output_path
    
    except requests.RequestException as e:
        print(f"Failed to download ZIP file. Error: {e}")
        return None

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

def download_pdfs(json_file, output_folder):
    """
    Download PDFs for all financial disclosures in the JSON file.
    
    Args:
        json_file (str): Path to the JSON file containing disclosure information
        output_folder (str): Path to the folder where PDFs will be saved
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Read the JSON file
    with open(json_file, 'r') as f:
        disclosures = json.load(f)
    
    # Base URL for the PDFs
    base_url = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{}/{}.pdf"
    
    # Get current year
    current_year = datetime.now().year
    
    # Lists to track downloads
    successful_downloads = []
    failed_downloads = []
    
    # Download each PDF
    for disclosure in disclosures:
        doc_id = disclosure.get('DocID', '')
        if not doc_id:
            continue
        
        pdf_url = base_url.format(current_year, doc_id)
        output_path = os.path.join(output_folder, f"{doc_id}.pdf")
        
        try:
            # Send a GET request to download the PDF
            response = requests.get(pdf_url, timeout=10)
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            # Write the PDF to file
            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            
            print(f"Successfully downloaded: {doc_id}.pdf")
            successful_downloads.append(disclosure)
        
        except requests.RequestException as e:
            print(f"Failed to download {doc_id}.pdf. Error: {e}")
            # Add the full disclosure information to failed downloads
            failed_download_info = disclosure.copy()
            failed_download_info['download_error'] = str(e)
            failed_downloads.append(failed_download_info)
    
    # Determine the downloads directory
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'CongressionalFDs')
    
    # Write failed downloads to a JSON file
    if failed_downloads:
        failed_download_path = os.path.join(downloads_dir, 'failed_files.json')
        with open(failed_download_path, 'w') as f:
            json.dump(failed_downloads, f, indent=2)
    
    # Print summary
    print(f"\nDownload Summary:")
    print(f"Total Documents: {len(disclosures)}")
    print(f"Successful Downloads: {len(successful_downloads)}")
    print(f"Failed Downloads: {len(failed_downloads)}")
    print(f"Failed downloads logged to {failed_download_path}")

def main():
    # Determine the current year
    current_year = datetime.now().year
    
    # Set up directories
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'CongressionalFDs')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Paths for files
    zip_file_path = os.path.join(downloads_dir, f'{current_year}FD.zip')
    json_file_path = os.path.join(downloads_dir, 'C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\financial_disclosure.json')
    pdf_output_folder = os.path.join(downloads_dir, 'DownloadedPDFs')
    
    # Download the ZIP file
    downloaded_zip = download_zip_file(current_year)
    
    if downloaded_zip:
        # Convert XML to JSON
        convert_zip_xml_to_json(downloaded_zip, json_file_path)
        
        # Download PDFs
        download_pdfs(json_file_path, pdf_output_folder)

if __name__ == "__main__":
    main()
