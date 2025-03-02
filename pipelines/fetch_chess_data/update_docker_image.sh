PROJECT_ID="chess-data-451709"
REGION="us-central1"
IMAGE_NAME="fetch-chess-data"
TAG="latest"
REPO="gcr.io"

docker build --platform=linux/amd64 -t $REPO/$PROJECT_ID/$IMAGE_NAME:$TAG .
docker push $REPO/$PROJECT_ID/$IMAGE_NAME:$TAG
