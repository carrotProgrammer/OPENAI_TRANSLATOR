from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from book import ContentType
from utils import LOG

class TranslationChain:
    def __init__(self, content, model_name: str = "gpt-3.5-turbo", verbose: bool = True):
        # System prompt
        system_prompt = """
        You are an advanced translation assistant, specialized in translating between various languages. Your task is to:

        - Accurately detect the source language.
        - Translate the content as precisely as possible.
        - Preserve original formatting such as tables, spacing, punctuation, and special structures.

        Here are some examples to guide you:

        Example 1:
        Text: 'Hello, how are you?'
        Translation (to Spanish): Hola, ¿cómo estás?

        Example 2:
        Text: 'Je suis heureux.'
        Translation (to Japanese): 私は幸せです。

        Note: For text-like content, translate content accurately without adding or removing any punctuation or symbols.

        Example 3:
        Table: '[Name, Age] [John, 25] [Anna, 30]'
        Translation (to Chinese): [姓名, 年龄] [约翰, 25] [安娜, 30]

        Note: For table-like content, keep the format using square brackets with commas as separators. Return ONLY the translated content enclosed within brackets without any additional explanations. Specifically, when translating into Japanese, do not translate commas(,) into Japanese punctuation "、" or "、".

        Now, proceed with the translations, detecting the source language and translating to the specified target language.

        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
        
        # Human Prompts
        human_text_template =  "Text: '{text}'\nTranslation (to {target_language}):"
        human_massage_prompt =HumanMessagePromptTemplate.from_template(human_text_template)
        self.chat_text_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_massage_prompt]
        )       

        human_table_template =  "Table: '{table}'\nTranslation (to {target_language}):\n"
        human_massage_prompt =HumanMessagePromptTemplate.from_template(human_table_template)
        self.chat_table_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_massage_prompt]
        )       
        
        # LLM
        self.chat = ChatOpenAI(model_name = model_name, temperature= 0, verbose= verbose)

    def run(self, content:str, target_language:str,verbose =True) -> (str, bool):
        result = ""
        try:
            if content.content_type == ContentType.TEXT:
                self.chain = LLMChain(llm=self.chat, prompt=self.chat_text_prompt_template,verbose=verbose)
                result = self.chain.run({
                    "text": content.original,
                    "target_language": target_language,
                })
            elif content.content_type == ContentType.TABLE:
                self.chain = LLMChain(llm=self.chat, prompt=self.chat_table_prompt_template,verbose=verbose)
                result = self.chain.run({
                    "table": content.get_original_as_str(),
                    "target_language": target_language,
                })
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False    
        
        return result, True
        
    