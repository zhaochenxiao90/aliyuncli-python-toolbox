#!/bin/bash
# script to build the docker image
set -euox pipefail

REPO=${REPO:-"aliyunca"}
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT=${PROJECT:-"$(basename $ROOT)"}
TAG=${TAG:-"latest"};

DIR=$ROOT;
PWD=`pwd`
cd $ROOT

# build the build container (requires compilation of certain things)
docker build -t $REPO/$PROJECT-build:$TAG -f $ROOT/build/Dockerfile $ROOT
build=$(docker run -dti $REPO/$PROJECT-build:$TAG)
docker cp $build:/all.tgz .

# ossutil
docker build -t $REPO/$PROJECT-build-oss:$TAG -f $ROOT/oss/Dockerfile $ROOT
build2=$(docker run -dti $REPO/$PROJECT-build-oss:$TAG sh)
docker cp $build2:/go/bin/ossutil .

# build the distribution container
docker build -t $REPO/$PROJECT:$TAG -f $ROOT/dist/Dockerfile $ROOT
rm all.tgz ossutil
docker stop $build $build2
docker rm $build $build2

