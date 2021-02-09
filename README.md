# About in剧本(jù běn)

in剧本(jù běn) is an open source software which can help you to write a screenplay as a plain text. The online version is available.


*  中文版  [juben.in](https://juben.in) 
*  English [juben.in/en](https://juben.in/en)


# Development

## Download Fonts

Download SourceHan_ttc.zip from https://github.com/injuben/Source-Han-TrueType , unzip it and copy *.ttc to folder _app/juben/fonts_

## Setup Python(3.5+)

    python3 -m venv ~/.venv/injuben
    source ~/.venv/injuben/bin/activate
    cd app
    pip install -r requirements.txt

## Run App

    FLASK_APP=in_juben.py FLASK_ENV=development flask run --host=0.0.0.0

# Docker

## Local Build

    docker build --tag injuben .
    docker run --rm -it --name injuben -p 5000:5000 injuben
    
## Docker Hub

    docker pull injuben/injuben
    docker run --rm -it --name injuben -p 5000:5000 injuben/injuben
    
Access http://localhost:5000/

    
# Thanks

[Fountain](https://fountain.io)

Python : [cachelib](https://github.com/pallets/cachelib), [Flask](http://flask.pocoo.org), [Reportlab](https://www.reportlab.com), [Screenplain](http://www.screenplain.com)

JavaScript: [CodeMirror](https://codemirror.net), [download.js](http://danml.com/download.html), [jQuery](https://jquery.com/), [JavaScirpt Cookie](https://github.com/js-cookie/js-cookie), [PDF JS](https://mozilla.github.io/pdf.js)

CSS: [Bulma](https://bulma.io), [Foundation Icon Font Sets](https://github.com/zurb/foundation-icons)

Compressor: [YUI Compressor](http://yui.github.io/yuicompressor)
