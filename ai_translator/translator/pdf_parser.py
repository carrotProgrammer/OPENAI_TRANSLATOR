import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent, Paragraph
from translator.exceptions import PageOutOfRangeException
from utils import LOG

class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()
                words = pdf_page.extract_words()
                tables = pdf_page.extract_tables()

                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            if cell is not None:
                                idx = 0
                                while idx < len(words):
                                    match, next_idx = self.words_match_cell(words, idx, cell)
                                    if match:
                                        del words[idx:next_idx]
                                        idx = next_idx - 1
                                    idx += 1

                # Group words by top value to detect lines
                lines = {}
                for word in words:
                    lines.setdefault(word['top'], []).append(word)

                grouped_lines = sorted(lines.values(), key=lambda l: l[0]['top'])

                # Construct paragraphs based on empty space or large gaps between lines
                paragraphs = []
                current_paragraph = []
                previous_bottom = 0
                for line_words in grouped_lines:
                    if previous_bottom and (line_words[0]['top'] - previous_bottom) > 10:  # Assuming gap > 10 means new paragraph
                        paragraphs.append(current_paragraph)
                        current_paragraph = []

                    current_paragraph.extend(line_words)
                    previous_bottom = line_words[0]['bottom']

                if current_paragraph:
                    paragraphs.append(current_paragraph)

                content = Content(content_type=ContentType.TEXT, original="")
                for paragraph_words in paragraphs:
                    paragraph_text = " ".join([word['text'] for word in paragraph_words])
                    
                    # 这里简单假设每一个段落的字体都和第一个文字的字体一致
                    style = self.extract_style_from_word(paragraph_words[0])
                    
                    # 将每个段落添加到original属性，并插入标识符
                    if content.original:
                        content.original += '\n' + "¶¶¶" + '\n'
                    content.original += paragraph_text

                    layout = {
                        'top': paragraph_words[0]['top'],
                        'bottom': paragraph_words[-1]['bottom']
                    }
                    paragraph = Paragraph(text=paragraph_text, layout=layout, style=style)

                    content.add_paragraph(paragraph)
                content.update_layout() 

                page.add_content(content)   

                # Handling tables
                tables_objects = pdf_page.find_tables()
                for table_index, table_obj in enumerate(tables_objects):
                    table_bbox = table_obj.bbox
                    table_layout = {
                        'top': table_bbox[1],
                        'bottom': table_bbox[3],
                        'left': table_bbox[0],  # 获取表格的左边界
                        'right': table_bbox[2]   # 获取表格的右边界
                    }                  
                    # 这里使用 tables[table_index]，确保对每个表格分别处理
                    table = TableContent(tables[table_index], layout=table_layout)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                book.add_page(page)

        return book

    # 使用扩展匹配从文本中删除表格单元格中的文字。扩展匹配：在检查是否移除一个单词之前，考虑单词及其后面的几个单词与单元格内容的匹配。
    def words_match_cell(self, words, start_idx, cell_text):
        end_idx = start_idx
        combined_text = ''
        cell_text_cleaned = cell_text.replace("\n", " ").strip()  # 对单元格文本进行清理，替换换行符为空格
        
        while end_idx < len(words) and combined_text.strip() != cell_text_cleaned:
            combined_text += ' ' + words[end_idx]['text']
            end_idx += 1

        return combined_text.strip() == cell_text_cleaned, end_idx

    #   这个方法没有完全实现，只简单估计了文本大小
    def extract_style_from_word(self, word):
         # Use 'top' and 'bottom' to estimate the font size
        font_height = word['bottom'] - word['top']
        
        style = {
            "size": font_height,  # Use the calculated font height as size
            "font": word.get('font', None),  # Example to extract font. Adjust based on Word object's attributes
            # You may need more intricate logic to determine 'bold' and 'italy' properties based on font names or other attributes.
            "bold": "Bold" in word.get('font', ''),
            "italy": "Ital" in word.get('font', '') or "Italic" in word.get('font', '')
        }
        return style

    