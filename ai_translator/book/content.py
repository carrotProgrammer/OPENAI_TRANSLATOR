import pandas as pd
import re
from enum import Enum, auto
from PIL import Image as PILImage
from utils import LOG

class ContentType(Enum):
    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()


UNIQUE_IDENTIFIER = "¶¶¶"  # 使用此特殊字符作为标识符，分割段落。

class Content:
    def __init__(self, content_type, original, translation=None, layout=None, style=None):
        self.content_type = content_type
        self.original = original
        self.translation = translation
        self.status = False
        self.layout = layout
        self.style = style if style else {}
        self.paragraphs = []

    def set_translation(self, translation, status):
        if not self.check_translation_type(translation):
            raise ValueError(f"Invalid translation type. Expected {self.content_type}, but got {type(translation)}")
        self.translation = translation
        self.status = status
    
    def apply_translated_paragraphs(self, translated_text: str):
        """Updates the translation for each paragraph based on the translated content."""
        paragraphs = translated_text.split('\n' + UNIQUE_IDENTIFIER + '\n')
        for para, trans in zip(self.paragraphs, paragraphs):
            para.set_translation(trans)
        # Update the complete translation for the content
        self.translation = '\n'.join(paragraphs)

    def check_translation_type(self, translation):
        if self.content_type == ContentType.TEXT and isinstance(translation, str):
            return True
        elif self.content_type == ContentType.TABLE and isinstance(translation, list):
            return True
        elif self.content_type == ContentType.IMAGE and isinstance(translation, PILImage.Image):
            return True
        return False
    
    def add_paragraph(self, paragraph):
        self.paragraphs.append(paragraph)

    def update_layout(self):
        if self.paragraphs:
            self.layout = {
                'top': self.paragraphs[0].layout['top'],
                'bottom': self.paragraphs[-1].layout['bottom'],
            }

    def prepare_translation_input(self):
        """Prepares the content for translation by inserting unique identifiers."""
        return ('\n' + UNIQUE_IDENTIFIER + '\n').join([para.text for para in self.paragraphs])

class Paragraph:
    def __init__(self, text, layout=None, translation = None, style = None):
        self.text = text
        self.layout = layout
        self.tanslation = translation
        self.style = style if style else {}  # 新添加的style属性

    def set_translation(self, translation: str):
        """Sets the translation for the paragraph."""
        self.translation = translation


class TableContent(Content):
    def __init__(self, data, translation=None, layout = None, left=None, right=None):
        df = pd.DataFrame(data)

        # Verify if the number of rows and columns in the data and DataFrame object match
        if len(data) != len(df) or len(data[0]) != len(df.columns):
            raise ValueError("The number of rows and columns in the extracted table data and DataFrame object do not match.")

        super().__init__(ContentType.TABLE, df, translation=translation, layout=layout)

    def set_translation(self, translation, status):
        try:
            if not isinstance(translation, str):
                raise ValueError(f"Invalid translation type. Expected str, but got {type(translation)}")

            # Remove any single quotes
            translation = translation.replace("'", "")
            
            # Replace full-width comma with half-width comma
            translation = translation.replace("，", ",")

            LOG.debug(translation)

            # Use regex to split by '] [' and account for potential spaces or other whitespace characters
            rows = re.split(r'\]\s*\[\s*', translation.strip('[]'))

            # For each row, split by comma ','
            table_data = [row.split(',') for row in rows]  # 使用','作为分隔符，并不考虑其后的空格

            # Strip any potential spaces from each cell
            table_data = [[cell.strip() for cell in row] for row in table_data]

            # Ensure we have at least two rows
            if len(table_data) < 2:
                raise ValueError("Translation doesn't contain enough rows for a table.")

            # Create a DataFrame from the table_data
            translated_df = pd.DataFrame(table_data[1:], columns=table_data[0])
            LOG.debug(translated_df)
            self.translation = translated_df
            self.status = status
        except Exception as e:
            LOG.error(f"An error occurred during table translation: {e}")
            self.translation = None
            self.status = False

    def __str__(self):
        formatted_rows = []
        for _, row in self.original.iterrows():
            formatted_row = ', '.join(map(str, row))  # 修改这里，加入逗号和空格
            formatted_rows.append(f"[{formatted_row}]")
        
        return ' '.join(formatted_rows)  # 使用空格连接所有的格式化行

    def iter_items(self, translated=False):
        target_df = self.translation if translated else self.original
        for row_idx, row in target_df.iterrows():
            for col_idx, item in enumerate(row):
                yield (row_idx, col_idx, item)

    def update_item(self, row_idx, col_idx, new_value, translated=False):
        target_df = self.translation if translated else self.original
        target_df.at[row_idx, col_idx] = new_value

    def get_original_as_str(self):
        formatted_rows = []
        for _, row in self.original.iterrows():
            formatted_row = ', '.join(map(str, row))  # 修改这里，加入逗号和空格
            formatted_rows.append(f"[{formatted_row}]")
        
        return ' '.join(formatted_rows)  # 使用空格连接所有的格式化行
