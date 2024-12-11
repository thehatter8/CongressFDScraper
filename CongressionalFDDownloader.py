import json
import os
import requests

def download_pdfs(json_file, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Read the JSON file
    with open(json_file, 'r') as f:
        disclosures = json.load(f)
    
    # Base URL for the PDFs
    base_url = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/{}.pdf"
    
    # Lists to track downloads
    successful_downloads = []
    failed_downloads = []
    
    # Download each PDF
    for disclosure in disclosures:
        doc_id = disclosure['DocID']
        pdf_url = base_url.format(doc_id)
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
    
    # Write failed downloads to a JSON file
    if failed_downloads:
        with open('C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\failed_files.json', 'w') as f:
            json.dump(failed_downloads, f, indent=2)
    
    # Print summary
    print(f"\nDownload Summary:")
    print(f"Total Documents: {len(disclosures)}")
    print(f"Successful Downloads: {len(successful_downloads)}")
    print(f"Failed Downloads: {len(failed_downloads)}")
    print(f"Failed downloads logged to failed_files.json")

def main():
        # Path to your JSON file
    json_file = 'C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\financial_disclosure.json'
    
    # Output folder for PDFs
    output_folder = 'C:\\Users\\ITSAMEEEEE\\Downloads\\CongressionalFDs\\PDFs'
    
    # Run the download function
    download_pdfs(json_file, output_folder)

if __name__ == "__main__":
    main()