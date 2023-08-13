import argparse

class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Translate English PDF book to Chinese.')
        self.parser.add_argument('--config', type=str, default='config.yaml', help='Configuration file with model and API settings.')
        self.parser.add_argument('--model_type', type=str, required=True, choices=['GLMModel', 'OpenAIModel'], help='The type of translation model to use. Choose between "GLMModel" and "OpenAIModel".')        
        self.parser.add_argument('--glm_model_url', type=str, help='The URL of the ChatGLM model URL.')
        self.parser.add_argument('--timeout', type=int, help='Timeout for the API request in seconds.')
        self.parser.add_argument('--openai_model', type=str, help='The model name of OpenAI Model. Required if model_type is "OpenAIModel".')
        self.parser.add_argument('--openai_api_key', type=str, help='The API key for OpenAIModel. Required if model_type is "OpenAIModel".')
        self.parser.add_argument('--book', type=str, help='PDF file to translate.')
        self.parser.add_argument('--file_format', type=str, help='The file format of translated book. Now supporting PDF and Markdown')
        self.parser.add_argument('--gui', action='store_true', help='Start GUI mode')

    def parse_arguments(self):
        return self.parser.parse_args()

    def check_argument(self, args):
        if args.model_type == 'OpenAIModel':
            if not args.openai_model:
                self.parser.error("--openai_model is required when using OpenAIModel")
            if not args.openai_api_key:
                self.parser.error("--openai_api_key is required when using OpenAIModel")
            if not args.book:
                self.parser.error("--book is required")
            if not args.file_format:
                self.parser.error("--file_format is required")

