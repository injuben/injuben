#!/bin/bash

CSS_PATH="../app/static/css"
JS_PATH="../app/static/js"

rm *.css
rm *.js

function yuicompressor(){
    in_file=$1
    out_file=$2 
    java -jar yuicompressor-2.4.8.jar $1 -o $2
}

CSS_LIST=('bulma.min.css'
'codemirror/addon/fold/foldgutter.css'
'codemirror/addon/scroll/simplescrollbars.css'
'codemirror/lib/codemirror.css'
'codemirror/theme/idea.css'
'codemirror/theme/dracula.css'
'foundation-icons.css')

JS_LIST=('codemirror/addon/display/placeholder.js'
'codemirror/addon/fold/foldcode.js'
'codemirror/addon/fold/foldgutter.js'
'codemirror/addon/fold/indent-fold.js'
'codemirror/addon/fold/markdown-fold.js'
'codemirror/addon/scroll/simplescrollbars.js'
'codemirror/addon/selection/active-line.js'
'codemirror/mode/markdown/markdown.js')

for css in ${CSS_LIST[@]};do
  yuicompressor ${CSS_PATH}/${css} tmp.min.css
  cat tmp.min.css >> in.min.css
done

cp in.min.css ${CSS_PATH}/

for js in ${JS_LIST[@]};do
  yuicompressor ${JS_PATH}/${js} tmp.min.js
  cat tmp.min.js >> codemirror.composer.min.js
done

cp codemirror.composer.min.js ${JS_PATH}/codemirror/composer/composer

yuicompressor ${JS_PATH}/codemirror/lib/codemirror.js codemirror.min.js
cp codemirror.min.js ${JS_PATH}/codemirror/lib

yuicompressor ${JS_PATH}/js.cookie.js js.cookie.min.js
cp js.cookie.min.js ${JS_PATH}


rm *.js
rm *.css
