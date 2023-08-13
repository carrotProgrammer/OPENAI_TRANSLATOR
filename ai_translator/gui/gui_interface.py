# 在 gui_interface.py 中
import gradio as gr
import os
from utils import LOG, ConfigLoader
from model import OpenAIModel
from translator import PDFTranslator

# 定义一个全局变量来存储args
global_args = None

def translate_with_gui(pdf_tempfile, target_language, output_format):
    global global_args
    # 获取文件的真实路径
    pdf_path = pdf_tempfile.name

    # 转换语言输入
    language_mapping = {
        "中文": "Chinese",
        "日语": "Japanese",
        "西班牙语": "Spanish"
    }
    target_language = language_mapping.get(target_language, "Chinese")  # 默认为中文

    # 记录PDF文件路径和目标语言
    LOG.debug(f"PDF文件路径: {pdf_path}")
    LOG.debug(f"目标语言: {target_language}")

    config_loader = ConfigLoader(global_args.config)
    config = config_loader.load_config()

    model = OpenAIModel(model=config['OpenAIModel']['model'], api_key=os.environ.get('OPENAI_API_KEY') or config['OpenAIModel']['api_key'])
    output_format = output_format if output_format else config['common']['file_format']

    translator = PDFTranslator(model)
    output_path = translator.translate_pdf(pdf_path, output_format, target_language=target_language)
    return f"翻译成功! 输出到：{output_path}"

def launch_gui(args):
    global global_args
    global_args = args
    iface = gr.Interface(
        fn=translate_with_gui,
        inputs=[
            gr.inputs.File(label="上传PDF文件"),
            gr.inputs.Dropdown(choices=["中文", "日语", "西班牙语"], default="中文", label="选择目标语言"),  # 这里添加了default参数
            gr.inputs.Radio(choices=["PDF", "Markdown"], default="PDF", label="选择输出格式")  # 选择输出格式
        ],
        outputs=gr.outputs.Textbox(label="输出结果")
    )
    iface.launch()

