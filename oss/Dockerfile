FROM golang:alpine

RUN \
    apk update && apk add zip openssl git \
    && wget https://github.com/aliyun/ossutil/archive/master.zip \
    && unzip master.zip

RUN cd src \
    && go get \
        github.com/droundy/goopt \
        github.com/alyu/configparser \
        github.com/syndtr/goleveldb/leveldb \
        github.com/aliyun/aliyun-oss-go-sdk/oss \
        gopkg.in/check.v1 \
        github.com/aliyun/ossutil \
    && go build github.com/aliyun/ossutil/ossutil.go