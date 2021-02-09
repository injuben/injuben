FROM python:3.9-alpine3.13
COPY app/ /injuben/
WORKDIR /injuben
ADD https://github.com/injuben/Source-Han-TrueType/raw/master/SourceHan_ttc.zip .
RUN rm -rf /var/cache/apk/* && \
    rm -rf /tmp/*
RUN apk update
RUN apk --update add --no-cache --virtual .build-deps \
    curl freetype-dev gcc jpeg-dev libxml2-dev libxslt-dev libffi-dev libgcc lcms2-dev \
    musl-dev openjpeg-dev openssl-dev \
    tiff-dev tk-dev tcl-dev zlib-dev unzip
RUN unzip SourceHan_ttc.zip
RUN mv *.ttc juben/fonts/
RUN rm -f SourceHan_ttc.zip
RUN pwd
RUN ls -la
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apk del .build-deps \
    curl freetype-dev gcc jpeg-dev libxml2-dev libxslt-dev libffi-dev libgcc lcms2-dev \
    musl-dev openjpeg-dev openssl-dev \
    tiff-dev tk-dev tcl-dev zlib-dev unzip
EXPOSE 5000
CMD FLASK_APP=in_juben.py FLASK_ENV=prodution flask run --host=0.0.0.0
