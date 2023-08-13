from typing import Optional
from model import Model
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG

class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = 'Chinese', output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)

        system_prompt = Model.get_system_prompt()

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                prompt = self.model.translate_prompt(content, target_language)
                LOG.debug(prompt)
                translation, status = self.model.make_request(prompt, system_prompt = system_prompt)
                LOG.info(translation)
                
                # Update the content in self.book.pages directly
                content.apply_translated_paragraphs(translation)
                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)
                
        return self.writer.save_translated_book(self.book, output_file_path, file_format)
        