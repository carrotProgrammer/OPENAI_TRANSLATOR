import sys
import os
import gradio as gr
from gui import gui_interface

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator


if __name__ == "__main__":
    # 解析命令行参数
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()

    # 如果用户选择了GUI模式
    if args.gui:
        gui_interface.launch_gui(args)
    else:
        # 命令行模式
        config_loader = ConfigLoader(args.config)
        config = config_loader.load_config()
        args.openai_model = args.openai_model or config['OpenAIModel']['model']
        args.openai_api_key = args.openai_api_key or os.environ.get('OPENAI_API_KEY') or config['OpenAIModel']['api_key']
        args.book = args.book if args.book else config['common']['book']
        args.file_format = args.file_format if args.file_format else config['common']['file_format']
        argument_parser.check_argument(args)
        
        model = OpenAIModel(model=args.openai_model, api_key=args.openai_api_key)
        translator = PDFTranslator(model)
        translator.translate_pdf(args.book, args.file_format)