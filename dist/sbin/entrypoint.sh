#!/bin/sh
set -e

# oss util defaults
ALI_OSSUTIL_LANG=${ALI_OSSUTIL_LANG:-EN}
ALI_OSSUTIL_ENDPOINT=${ALI_OSSUTIL_ENDPOINT:-""}
if [ "$ALI_OSSUTIL_ENDPOINT" == '' ]; then
    ALI_OSSUTIL_ENDPOINT=oss-${ALI_DEFAULT_REGION}.aliyuncs.com
fi

sed -i -e s@'${ALI_ACCESS_KEY}'@"$ALI_ACCESS_KEY"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_ACCESS_SECRET}'@"$ALI_ACCESS_SECRET"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_DEFAULT_REGION}'@"$ALI_DEFAULT_REGION"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_OUTPUT_FORMAT}'@"$ALI_OUTPUT_FORMAT"@g /root/.aliyuncli/*

# ossutil
sed -i -e s@'${ALI_ACCESS_KEY}'@"$ALI_ACCESS_KEY"@g /root/.ossutilconfig
sed -i -e s@'${ALI_ACCESS_SECRET}'@"$ALI_ACCESS_SECRET"@g /root/.ossutilconfig
sed -i -e s@'${ALI_OSSUTIL_LANG}'@"$ALI_OSSUTIL_LANG"@g /root/.ossutilconfig
sed -i -e s@'${ALI_OSSUTIL_ENDPOINT}'@"$ALI_OSSUTIL_ENDPOINT"@g /root/.ossutilconfig

# wait indefinitely
/bin/sh