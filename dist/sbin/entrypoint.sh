#!/bin/sh
set -e

sed -i -e s@'${ALI_ACCESS_KEY}'@"$ALI_ACCESS_KEY"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_ACCESS_SECRET}'@"$ALI_ACCESS_SECRET"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_DEFAULT_REGION}'@"$ALI_DEFAULT_REGION"@g /root/.aliyuncli/*
sed -i -e s@'${ALI_OUTPUT_FORMAT}'@"$ALI_OUTPUT_FORMAT"@g /root/.aliyuncli/*

# wait indefinitely
/bin/sh