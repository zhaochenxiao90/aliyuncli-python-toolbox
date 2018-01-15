FROM python:2.7-alpine

COPY acs /acs
COPY all.tgz all.tgz
RUN tar -xf all.tgz && rm all.tgz && mkdir -p /root/.aliyuncli
COPY dist/aliyuncli /root/.aliyuncli
COPY dist/sbin /sbin

RUN \
    chmod 0711 /sbin/entrypoint.sh \
    && pip install --upgrade \
        aliyuncli \
        footmark \
        ecsutils \
    && pip install -r /acs/requirements.txt

ENTRYPOINT ["/sbin/entrypoint.sh"]