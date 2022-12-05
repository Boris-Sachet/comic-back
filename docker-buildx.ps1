# Enable buildx and create a builder instance
docker buildx create --use

# Run the buildx build command
docker buildx build --push --tag junnsorran/comic-back --file .\docker\Dockerfile --platform linux/amd64,linux/arm64 .
