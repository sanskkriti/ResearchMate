import fitz
import camelot

def extract_pdf_sections(file_path):
    full_text = ""
    
    # Extract text and figure captions
    doc = fitz.open(file_path)
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        full_text += f"\n[Page {page_num}]\n{text}\n"
        
        blocks = page.get_text("blocks")
        for b in blocks:
            block_text = b[4].strip()
            if block_text.lower().startswith(("figure", "fig.")):
                full_text += f"[Page {page_num}] Caption: {block_text}\n"
    
    # Extract tables and convert to descriptive sentences
    try:
        tables = camelot.read_pdf(file_path, pages="all")
        for i, table in enumerate(tables):
            table_text = ""
            headers = table.df.columns.tolist()
            for row in table.df.itertuples(index=False):
                row_text = ", ".join(f"{h}: {v}" for h, v in zip(headers, row))
                table_text += f"- {row_text}\n"
            full_text += f"[Table {i+1}: {table.df.columns[0]}]\n{table_text}\n"
    except Exception as e:
        print(f"No tables detected or error: {e}")

    return full_text
