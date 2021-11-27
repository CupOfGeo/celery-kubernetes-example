FROM alpine:3.12
COPY lcs /usr/src/lcs
COPY spotify2genius /usr/src/spotify2genius

COPY myproject /usr/src/myproject

#COPY myproject/*.py /usr/src/myproject/
#COPY myproject/requirements.txt /usr/src/myproject
#COPY myproject/static /usr/src/myproject/static
#COPY myproject/templates /usr/src/myproject/templates
#COPY myproject/models /usr/src/myproject/models



RUN apk add --no-cache python3 py3-pip bash \
    && pip install /usr/src/lcs \
    && pip install /usr/src/spotify2genius \
    && pip install -r /usr/src/myproject/requirements.txt
EXPOSE 5000
WORKDIR /usr/src/myproject
ENTRYPOINT python3 main.py
