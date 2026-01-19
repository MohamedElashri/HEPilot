# Scraper for LHCb Twiki facts page. 

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime


def scrape_lhcb_facts():
    
    url = "https://twiki.cern.ch/twiki/bin/view/Main/LHCb-Facts"  
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        # parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # data storage structure
        data = {
            'url': url,
            'scrape_date': datetime.now().isoformat(),
            'title': '',
            'sections': {},
            'facts': [],
            'tables': [],
            'raw_text': ''
        }
        
        # acquire title
        title = soup.find('title')
        if title:
            data['title'] = title.text.strip()
            print(f"Title found: {data['title']}")
        
        #  main content area
        content = soup.find('div', class_='patternContent')
        if not content:
            content = soup.find('div', id='patternMainContents')
        if not content:
            content = soup.body
            print("Using full body content")
        
        if content:
            # acquire all text
            data['raw_text'] = content.get_text(separator='\n', strip=True)
            
            # extract sections (headers and following content)
            for header_level in ['h1', 'h2', 'h3', 'h4']:
                headers_found = content.find_all(header_level)
                for header in headers_found:
                    header_text = header.get_text(strip=True)
                    
                    # get content after this header
                    content_parts = []
                    next_sibling = header.find_next_sibling()
                    
                    while next_sibling and next_sibling.name not in ['h1', 'h2', 'h3', 'h4']:
                        text = next_sibling.get_text(strip=True)
                        if text:
                            content_parts.append(text)
                        next_sibling = next_sibling.find_next_sibling()
                    
                    if content_parts:
                        data['sections'][header_text] = '\n'.join(content_parts)
            
            # extract bullet points
            all_lists = content.find_all(['ul', 'ol'])
            for lst in all_lists:
                items = lst.find_all('li')
                for item in items:
                    fact = item.get_text(strip=True)
                    if fact:
                        data['facts'].append(fact)
            
            # extract tables
            tables = content.find_all('table')
            for i, table in enumerate(tables):
                table_data = []
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        table_data.append(row_data)
                
                if table_data:
                    data['tables'].append({
                        'id': i,
                        'data': table_data
                    })
        
        print(f"scraping complete: {len(data['sections'])} sections, {len(data['facts'])} facts, {len(data['tables'])} tables")
        return data
        
    except requests.exceptions.RequestException as e:  
        print(f"Error fetching page: {e}")
        return None
    except Exception as e:  # Catch any other exceptions
        print(f"Unexpected error: {e}")
        return None


def save_data(data):
    # Save data in differnt formats.
    
    if not data:
        print("No data to save, mijo")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. JSON file (complete data)
    json_file = f"lhcb_facts_{timestamp}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved complete data to: {json_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
    
    # 2.  text file
    txt_file = f"lhcb_facts_{timestamp}.txt"
    try:
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"LHCb Facts from CERN TWiki\n")
            f.write(f"Scraped: {data['scrape_date']}\n")
            f.write(f"URL: {data['url']}\n\n")
            
            # Write sections
            if data['sections']:
                f.write("SECTIONS\n")
                for section, content in data['sections'].items():
                    f.write(f"\n{section}\n")
                    f.write(f"{content}\n")
            
            if data['facts']:
                f.write("\n\nFACTS\n")
                for i, fact in enumerate(data['facts'], 1):
                    f.write(f"{i}. {fact}\n")
        
        print(f"Saved text version to: {txt_file}")
    except Exception as e:
        print(f"Error saving text file: {e}")
    
    # 3. Saving tables as CSV files
    if data.get('tables'):
        for table in data['tables']:
            csv_file = f"lhcb_table_{table['id']}_{timestamp}.csv"
            try:
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in table['data']:
                        writer.writerow(row)
                print(f"Saved table {table['id']} to: {csv_file}")
            except Exception as e:
                print(f"Error saving CSV {csv_file}: {e}")
    
    # 4. Save raw text
    raw_file = f"lhcb_raw_{timestamp}.txt"
    try:
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(data.get('raw_text', ''))
        print(f"Saved raw text to: {raw_file}")
    except Exception as e:
        print(f"Error saving raw text: {e}")
    
    return {
        'json': json_file,
        'text': txt_file,
        'raw': raw_file
    }


def print_summary(data):
    if not data:
        print("No data to extract summary from")
        return
    
    print("summary:")
    print(f"Page Title: {data.get('title', 'N/A')}")
    print(f"Sections found: {len(data.get('sections', {}))}")
    print(f"Files extracted: {len(data.get('facts', []))}")
    print(f"Tables found: {len(data.get('tables', []))}")
    
    if data.get('sections'):
        print("\nSection Headers:")
        for i, section in enumerate(data['sections'].keys(), 1):
            print(f"  {i}. {section}")
    
    if data.get('facts') and len(data['facts']) > 0:
        print(f"\nFirst 5 facts:")
        for fact in data['facts'][:5]:
            preview = fact[:100] + "..." if len(fact) > 100 else fact
            print(f"  • {preview}")

if __name__ == "__main__":
    print("LHCb Facts Scraper")
    print("="*50)
    
    # scrape the data
    data = scrape_lhcb_facts()
    
    if data:
        # print entire summary
        print_summary(data)
        
        # save in multiple formats
        print("\nSaving data...")
        saved_files = save_data(data)
        
        print("\n Scraping complete, amor")
        print("Data has been saved in multiple formats.")
    else:
        print("\n Scraping failed.")