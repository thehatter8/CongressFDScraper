import json,os,requests,zipfile,xml.etree.ElementTree as ET
from datetime import datetime

def download_zip_file(y):
    url=f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{y}FD.zip"
    dl_dir=os.path.join(os.path.expanduser('~'),'Downloads','CongressionalFDs')
    os.makedirs(dl_dir,exist_ok=True)
    out_path=os.path.join(dl_dir,f'{y}FD.zip')
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        with open(out_path,'wb')as f:f.write(r.content)
        print(f"Downloaded {y} Financial Disclosure ZIP")
        return out_path
    except requests.RequestException as e:
        print(f"Download failed: {e}")
        return None

def convert_zip_xml_to_json(zip_path,json_path=None):
    with zipfile.ZipFile(zip_path,'r')as zf:
        xmls=[f for f in zf.namelist()if f.lower().endswith('.xml')]
        if len(xmls)!=1:raise ValueError(f"Expected 1 XML, found {len(xmls)}")
        with zf.open(xmls[0])as xf:
            tree=ET.parse(xf)
            root=tree.getroot()
    
    def xml_to_dict(elem):
        d={}
        for child in elem:
            d[child.tag]=xml_to_dict(child) if len(child)>0 else child.text or""
        return d
    
    members=[xml_to_dict(m) for m in root.findall('.//Member')]
    
    def get_filing_date(m):
        try:return datetime.strptime(m['FilingDate'],'%m/%d/%Y')
        except(KeyError,ValueError):return datetime.min
    
    sorted_members=sorted(members,key=get_filing_date,reverse=True)
    json_data=json.dumps(sorted_members,indent=2)
    
    if json_path:
        with open(json_path,'w')as f:f.write(json_data)
    return json_data

def download_pdfs(json_file,out_folder):
    os.makedirs(out_folder,exist_ok=True)
    with open(json_file,'r')as f:disclosures=json.load(f)
    base_url="https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{}/{}.pdf"
    current_year=datetime.now().year
    success,fail=[],[]
    
    for disc in disclosures:
        doc_id=disc.get('DocID','')
        if not doc_id:continue
        pdf_url=base_url.format(current_year,doc_id)
        out_path=os.path.join(out_folder,f"{doc_id}.pdf")
        
        try:
            r=requests.get(pdf_url,timeout=10)
            r.raise_for_status()
            with open(out_path,'wb')as pdf:pdf.write(r.content)
            print(f"Downloaded: {doc_id}.pdf")
            success.append(disc)
        except requests.RequestException as e:
            print(f"Failed: {doc_id}.pdf. Error: {e}")
            fail_info=disc.copy()
            fail_info['download_error']=str(e)
            fail.append(fail_info)
    
    dl_dir=os.path.join(os.path.expanduser('~'),'Downloads','CongressionalFDs')
    if fail:
        fail_path=os.path.join(dl_dir,'failed_files.json')
        with open(fail_path,'w')as f:json.dump(fail,f,indent=2)
    
    print(f"\nDownload Summary:")
    print(f"Total Documents: {len(disclosures)}")
    print(f"Successful Downloads: {len(success)}")
    print(f"Failed Downloads: {len(fail)}")
    print(f"Failed downloads logged to {fail_path}")

def main():
    current_year=datetime.now().year
    dl_dir=os.path.join(os.path.expanduser('~'),'Downloads','CongressionalFDs')
    os.makedirs(dl_dir,exist_ok=True)
    
    zip_path=os.path.join(dl_dir,f'{current_year}FD.zip')
    json_path=os.path.join(dl_dir,'financial_disclosure.json')
    pdf_dir=os.path.join(dl_dir,'DownloadedPDFs')
    
    downloaded_zip=download_zip_file(current_year)
    
    if downloaded_zip:
        convert_zip_xml_to_json(downloaded_zip,json_path)
        download_pdfs(json_path,pdf_dir)

if __name__=="__main__":main()
