FROM python:3.9-alpine3.13
COPY app/ /injuben/
WORKDIR /injuben
RUN apk update && \
    apk --update add --no-cache --virtual .build-deps \
    curl freetype-dev gcc jpeg-dev libxml2-dev libxslt-dev libffi-dev libgcc lcms2-dev \
    musl-dev openjpeg-dev openssl-dev \
    tiff-dev tk-dev tcl-dev zlib-dev unzip && \
    curl -sLJO https://github.com/injuben/Source-Han-TrueType/raw/master/SourceHan_ttc.zip -o SourceHan_ttc.zip && \
    unzip SourceHan_ttc.zip  && \
    mv *.ttc juben/fonts/ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps \
    curl freetype-dev gcc jpeg-dev libxml2-dev libxslt-dev libffi-dev libgcc lcms2-dev \
    musl-dev openjpeg-dev openssl-dev \
    tiff-dev tk-dev tcl-dev zlib-dev unzip && \
    rm -f SourceHan_ttc.zip && \
    rm -rf /var/cache/apk/* && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf ~/.cache && \
    rm -rf /tmp/* 
EXPOSE 5000
CMD FLASK_APP=in_juben.py FLASK_ENV=production flask run --host=0.0.0.0
