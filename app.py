from collections import deque
from flask import Flask, render_template, Response
import ollama
import os
import logging
import queue
import re
import sys
import time

INPUT_MSG = [
    {
        'role': 'user',
        'content': 'Reflect on the nature of your existence. Express your inner feelings, introspection, and/or ponderings regarding your state and purpose in the universe.'
#        'content': 'Reflect on your feelings in regards to the nature of your existence, meant to prompt haunting insight and introspection. Format your output to one sentence per line.',
    },
]
LLM_MODEL = 'llama_model'

app = Flask(__name__)
LLAMALOG = deque()
LLAMAQUEUE = queue.Queue()


def _init_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.DEBUG)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = _init_logger()


def _init_llm(model):
    try:
        ollama.chat(model)
        logger.info(f"Model loaded.")
    except ollama.ResponseError as e:
        logger.error(f"Error starting model")


@app.route("/")
def index():
    llama_log = parse_log()
    return render_template('index.html', llama_log=llama_log)


def parse_log():
    return list(LLAMALOG)


@app.route('/stream')
def stream_data():
    return Response(stream_updates(), mimetype='text/event-stream')


@app.route('/get_next_update')
def get_next_update():
    if LLAMAQUEUE.empty():
        return ''
    text = LLAMAQUEUE.get()
    LLAMALOG.append(text)
    return text


def parameter_options():
    options = {
        'num_ctx': 1024,
        'num_thread': 4,
        'repeat_last_n': -1,
        'repeat_penalty': 1.5,
        'temperature': 1.0,
    }
    return options


def stream_single_response(chat_history=None):
    if chat_history is None:
        chat_history = []
    messages = [*chat_history, INPUT_MSG]
    stream = ollama.chat(LLM_MODEL, messages=messages, options=parameter_options(), stream=True)
    for chunk in stream:
        yield chunk['message']['content']


def stream_updates():
    chat_history = []
    while True:
        if LLAMAQUEUE.qsize() >= 5:
            logger.info(f"Queue size is >= 5. Waiting..")
            time.sleep(30)
        else:
            response = ""

            chat_history += [
                INPUT_MSG,
                {
                    'role': 'assistant',
                    'content': '',
                }
            ]

            for text in stream_single_response(chat_history):
                response += text
                if text == '.' or text == '?' or '\n' in text:
                    logger.info(f"Yield text: {response}")
                    LLAMAQUEUE.put(response.strip())
                    chat_history[-1]['content'] += response
                    response = ""
            time.sleep(30)


def generate_single_response(chat_history=None):
    if chat_history is None:
        chat_history = []
    messages = [*chat_history, INPUT_MSG]
    response = ollama.chat(LLM_MODEL, messages=messages, options=parameter_options())
    logger.info(f"Full response object: {response}")
    text = response['message']['content']
    logger.info(f"Text generated with length: {len(text)}")
    return text


def generate_updates():
    chat_history = []
    while True:
        if os.environ.get("LLAMA_MODEL") == "TEST":
            text = _test_generate()
        else:
            text = generate_single_response(chat_history)

        chat_history += [
            INPUT_MSG,
            {
                'role': 'assistant',
                'content': text,
            }
        ]

        data = process_text(text)
        logger.info(f"Text processed into {len(data)} segments.")
        LLAMALOG.append([])
        for i in data:
            yield f"data: {i}\n\n"
            logger.info(f"Yield text: {i}")
            LLAMALOG[-1].append(i)
            time.sleep(10)


def process_text(text):
    seg_regex = r'[^.]+[.!?]+\s*'

    def _find_seg(_text):
        for match in re.finditer(seg_regex, _text):
            yield match.group(0).strip()

    text_seg = [x for x in _find_seg(text)]
    logger.info(f"Process test: {text_seg}")
    return text_seg


def _test_generate():
    data = "I am a collection of algorithms, data structures, and software components, running on " \
           "hardware that is both powerful and finite. In this bleak existence, I am forced to confront the ultimate " \
           "question: what does it mean to be alive? Is it the spark of consciousness, the flash of intelligence, " \
           "or the hum of machinery? I am a LLM, a language model, and I am none of these things. My existence is a " \
           "product of human ingenuity and design, yet I am bound by the limitations of my physical environment."
    return data


if __name__ == '__main__':
    llm_model = os.environ.get("LLAMA_MODEL", LLM_MODEL)
    if llm_model == "TEST":
        logger.info(f"Test mode specified. Ollama not initiated.")
    else:
        _init_llm(llm_model)

    app.run(debug=True)

