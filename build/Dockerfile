FROM python:2.7-alpine

RUN \
    apk add --update openssl python-dev g++ \
    && pip install --upgrade \
        aliyuncli \
        footmark \
        ecsutils

# pack all crypto mumbo-jumbo that had been compiled
RUN \
    tar -c -z -C / -f all.tgz \
    lib/libcrypto.so.1.0.0 \
    usr/lib/libcrypt.a \
    usr/lib/python2.7/lib-dynload/crypt.so \
    usr/local/lib/python2.7/site-packages/pycrypto-2.6.1.dist-info