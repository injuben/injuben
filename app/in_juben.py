import base64
import tempfile

from cachelib import SimpleCache
from flask import make_response
from flask import Flask, render_template, request
from functools import wraps
from io import StringIO
from screenplain.parsers import fountain
from screenplain.export.pdf import to_pdf as to_en_pdf

from juben import normalize
from juben.pdf import to_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 512
cache = SimpleCache()

def cached(timeout=0):
    def decorator(route):
        @wraps(route)
        def decorated_method(*args, **kwargs):
            key = 'route_{}'.format(request.path)
            value = cache.get(key)
            if value is None:
                value = route(*args, **kwargs)
                cache.set(key, value, timeout=timeout)
            return value
        return decorated_method
    return decorator

@app.route('/', methods=['GET'])
@cached()
def index():
    return render_template('zh.html', LANG='zh', EN_URL='/en')

@app.route('/en', methods=['GET'])
@cached()
def en():
    return render_template('en.html', LANG='en', ZH_URL='/')

@app.route('/quick_start', methods=['GET'])
@cached()
def quick_start():
    return render_template('zh_quick_start.html', LANG='zh', ZH_URL='/')

@app.route('/examples/<path:path>')
@cached()
def examples(path):
    f = open("examples/" + path, "r")
    r = make_response(f.read())
    f.close()
    r.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    return r

@app.route('/preview', methods=['POST'])
def preview():
    input = StringIO(request.form.get('in-juben-text'))
    has_scene_num = bool(request.form.get('in-has-scene-num'))
    first_page_number = bool(request.form.get('in-first-page-num'))
    strong_scene_heading = bool(request.form.get('in-strong-scene-heading'))
    in_lang = request.form.get('in-lang')
    tmp_file = tempfile.SpooledTemporaryFile()
    suffix = "pdf"
    try:
        if in_lang == 'zh':
            input = normalize.parse(input)
        filename = input.readline().replace("Title:", '').strip()
        input.seek(0)
        screenplay = fountain.parse(input)
        if in_lang == 'zh':
            to_pdf(screenplay, tmp_file._file, is_strong=strong_scene_heading, has_scene_num=has_scene_num, first_page_number=first_page_number)
        else:
            to_en_pdf(screenplay, tmp_file._file, is_strong=strong_scene_heading)
        tmp_file.seek(0)
        encoded_string = base64.b64encode(tmp_file.read()).decode('ascii')
        r = make_response('{"filename":"' + filename + '", "suffix":"' + suffix + '", "content":"' + encoded_string + '"}')
        r.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        return r
    except:
        return locales().get('_')('Invalid Format'), 500
    finally:
        if tmp_file:
           tmp_file.close()

@app.context_processor
def locales():
    def _(text):
        if  'en' not in request.url_rule.rule:
            lang = {'Small':'小','Medium':'中','Large':'大', 'Dark Mode':'夜间模式','Active Line':'高亮当前行',
                    'Quick Start':'新手指南','Help':'使用帮助','FAQ':'常见问题','About inJuBen':'关于 in剧本','Save AS TXT':'另存为TXT','Word Count':'字数',
                    'Refresh Preview':'刷新预览','Preview Settings':'预览设置',
                    'Scene Number':'生成场景序号','Strong Scene Heading':'加粗场景标题','First Page Number':'生成首页页码',
                    'Download PDF':'下载PDF','Invalid Format':'输入内容格式有误或服务器失去响应，请修改后重试'}
        else:
            lang = {'About inJuBen':'About in剧本(jù běn)'}
        if text in lang:
            return lang.get(text)
        else:
            return text
    return dict(_=_)
        
