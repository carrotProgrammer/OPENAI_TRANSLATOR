from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class PromptTemplate:
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
    @staticmethod
    def human_text_prompt(text: str, target_language: str) -> str:
        human_template =  f"Text: '{text}'\nTranslation (to {target_language}):"
        hunman_massage_prompt =HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [PromptTemplate.system_message_prompt, hunman_massage_prompt]
        )       
        return chat_prompt_template

    @staticmethod
    def human_table_prompt(table: str, target_language: str) -> str:
        human_template =  f"Table: '{table}'\nTranslation (to {target_language}):\n"
        hunman_massage_prompt =HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [PromptTemplate.system_message_prompt, hunman_massage_prompt]
        )       
        return chat_prompt_template
        
    

