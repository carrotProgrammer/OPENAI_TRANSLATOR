import os
from reportlab.lib import colors, pagesizes, units
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.platypus.flowables import KeepInFrame

from book import Book, ContentType
from utils import LOG

class Writer:
    def __init__(self):
        pass

    def save_translated_book(self, book: Book, output_file_path: str = None, file_format: str = "PDF"):
        if file_format.lower() == "pdf":
            return self._save_translated_book_pdf(book, output_file_path)
        elif file_format.lower() == "markdown":
            return self._save_translated_book_markdown(book, output_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _save_translated_book_pdf(self, book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.pdf')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")

        # Register Chinese font
        font_path = "../fonts/simsun.ttc"  # 请将此路径替换为您的字体文件路径
        pdfmetrics.registerFont(TTFont("SimSun", font_path))

        # Create a new ParagraphStyle with the SimSun font
        simsun_style = ParagraphStyle('SimSun', fontName='SimSun', fontSize=12, leading=14)

        # Create a PDF document
        doc = SimpleDocTemplate(output_file_path, pagesize=pagesizes.letter)
        styles = getSampleStyleSheet()
        story = []

        spacer = Spacer(1, 14)  # Assuming 14 units of space for the spacer

        # Iterate over the pages and contents
        for page in book.pages:
            # Combine all content items (paragraphs and tables) into a common list
            combined_contents = []
            for content in page.contents:
                if content.status:
                    if content.content_type == ContentType.TEXT:
                        for paragraph in content.paragraphs:
                            combined_contents.append(("paragraph", paragraph))
                    elif content.content_type == ContentType.TABLE:
                        combined_contents.append(("table", content))

            # Sort the combined list by the top layout value
            sorted_contents = sorted(combined_contents, key=lambda x: x[1].layout['top'] if x[1].layout else 0)
                            
            for content_type, content_item in sorted_contents:
                if content_type == "paragraph":
                    text = content_item.translation
                    if content_item.layout:
                        height = content_item.layout['bottom'] - content_item.layout['top']

                         # Extract size from the paragraph's style attribute
                        font_size = content_item.style.get('size', None)
                        if font_size is None:
                            font_size = 16  # Default font size
                        else:
                            font_size = float(font_size)  # Convert the size to float

                        # Dynamically adjust the fontSize of the style
                        dynamic_style = ParagraphStyle('DynamicStyle', parent=simsun_style, fontSize=font_size)
                        
                        para = Paragraph(text, dynamic_style)
                        story.append(KeepInFrame(doc.width, height, [para]))
                        story.append(spacer)
         
                elif content_type == "table":
                        # Add table to the PDF
                        table = content_item.translation
                        table_style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        pdf_table = Table([table.columns.tolist()] + table.values.tolist())
                        pdf_table.setStyle(table_style)
                        # Set the width of the table
                        table_width = content_item.layout['right'] - content_item.layout['left']
                        pdf_table._argW[0] = table_width / len(pdf_table._argW)
                        for i in range(1, len(pdf_table._argW)):
                            pdf_table._argW[i] = pdf_table._argW[0]

                        story.append(pdf_table)
                        story.append(spacer)  # Add a spacer after the table for an empty line
            # Add a page break after each page except the last one
            if page != book.pages[-1]:
                story.append(PageBreak())

        # Save the translated book as a new PDF file
        doc.build(story)
        LOG.info(f"翻译完成: {output_file_path}")
        return output_file_path

    def _save_translated_book_markdown(self, book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.md')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Iterate over the pages and contents
            for page in book.pages:
                # Combine all content items (paragraphs and tables) into a common list
                combined_contents = []
                for content in page.contents:
                    if content.status:
                        if content.content_type == ContentType.TEXT:
                            for paragraph in content.paragraphs:
                                combined_contents.append(("paragraph", paragraph))
                        elif content.content_type == ContentType.TABLE:
                            combined_contents.append(("table", content))

                # Sort the combined list by the top layout value
                sorted_contents = sorted(combined_contents, key=lambda x: x[1].layout['top'] if x[1].layout else 0)
                
                for content_type, content_item in sorted_contents:
                    if content_type == "paragraph":
                        text = content_item.translation
                        output_file.write(text + '\n\n')

                    elif content_type == "table":
                        table = content_item.translation
                        header = '| ' + ' | '.join(str(column) for column in table.columns) + ' |' + '\n'
                        separator = '| ' + ' | '.join(['---'] * len(table.columns)) + ' |' + '\n'
                        body = '\n'.join(['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in table.values.tolist()]) + '\n\n'
                        output_file.write(header + separator + body)
                
                # Add a page break (horizontal rule) after each page except the last one
                if page != book.pages[-1]:
                    output_file.write('---\n\n')

        LOG.info(f"翻译完成: {output_file_path}")
        return output_file_path