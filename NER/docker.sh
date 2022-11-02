#!/bin/bash
########################################################
## Shell Script to Build Docker Image 
########################################################
DATE=`date +%Y.%m.%d.%H.%M`

BASEDIR=$PWD
ENDPATH=$(basename $(pwd)) 
IMAGE=$1
CONTAINER="${IMAGE}_ctr"
VOLUME_DATA=$2

result="$(sudo docker images -q "$IMAGE" ) " 
if [[ -n "$result" ]]; then
echo "image exists"
sudo docker image rm --force $result
else
echo "No such image"
fi

echo "build the docker image"
sudo docker build -t $IMAGE .
echo "built docker images and proceeding to delete existing container"
result="$( sudo docker ps -q -f name="$CONTAINER" )"
if [[ $? -eq 0 ]]; then
echo "Container exists"
sudo docker container rm -f $CONTAINER
echo "Deleted the existing docker container"
else
echo "No such container"
fi
echo "Deploying the updated container"
sudo docker run -ti --name=$CONTAINER --net=host -v $VOLUME_DATA:/data -v $BASEDIR:/$ENDPATH $IMAGE
echo "Deploying the container"
