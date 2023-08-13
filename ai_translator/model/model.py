from book import ContentType
from .prompt_template import PromptTemplate

class Model:
    def make_text_prompt(self, text: str, target_language: str) -> str:
        return PromptTemplate.user_text_prompt(text, target_language)

    def make_table_prompt(self, table: str, target_language: str) -> str:
        return PromptTemplate.user_table_prompt(table, target_language)

    def translate_prompt(self, content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return self.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_prompt(content.get_original_as_str(), target_language)
        
    @staticmethod
    def get_system_prompt():
        return PromptTemplate.system_prompt

    def make_request(self, prompt):
        raise NotImplementedError("子类必须实现 make_request 方法")
