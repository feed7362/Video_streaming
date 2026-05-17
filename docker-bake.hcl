# Buildx Bake config. Replaces `docker compose build` for the heavy targets.
#
# Why bake:
#   - All targets build *concurrently* on the same BuildKit instance (compose
#     serializes more than it should).
#   - Shared BuildKit graph: layers used by both bff and ffmpeg (uv venv, apt
#     deps, the uv binary copy) are built once across all targets.
#   - Cache-to/from with sticky local cache survives across runs.
#
# Usage:
#   docker buildx bake                # build all targets in parallel
#   docker buildx bake bff            # build just one
#   docker buildx bake --print        # inspect resolved plan, no build
#   docker buildx bake --push         # build and push to REGISTRY
#   TAG=v0.4.2 docker buildx bake     # tag override
#
# Image names match what `compose up` expects (project name + service), so
# after a successful bake `docker compose up -d --no-build` runs without
# re-building anything.

variable "TAG" {
  default = "latest"
}

# Set to e.g. "ghcr.io/<owner>/" or "registry.example.com/" to push. The
# trailing slash is required. Empty = local-only.
variable "REGISTRY" {
  default = ""
}

# Compose project name from Docker/docker-compose.yml:`name:`.
# Used to compute the local image names compose will look for.
variable "PROJECT" {
  default = "video_streaming_stack"
}

# Default group when you run `docker buildx bake` with no args.
group "default" {
  targets = ["bff", "frontend", "ffmpeg"]
}

# Group for app code only — skip the heavy GPU base image rebuild.
group "app" {
  targets = ["bff", "frontend"]
}

target "_common" {
  platforms = ["linux/amd64"]
  # Inline cache metadata into the image manifest so `cache-from=type=registry`
  # works without a separate cache image.
  cache-to = ["type=inline"]
}

target "bff" {
  inherits   = ["_common"]
  context    = "./backend"
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}${PROJECT}-bff:${TAG}",
  ]
  cache-from = [
    "type=local,src=.buildx-cache/bff",
    "${REGISTRY}${PROJECT}-bff:${TAG}",
  ]
  cache-to = [
    "type=local,dest=.buildx-cache/bff,mode=max",
    "type=inline",
  ]
}

target "frontend" {
  inherits   = ["_common"]
  context    = "./frontend"
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}${PROJECT}-frontend:${TAG}",
  ]
  cache-from = [
    "type=local,src=.buildx-cache/frontend",
    "${REGISTRY}${PROJECT}-frontend:${TAG}",
  ]
  cache-to = [
    "type=local,dest=.buildx-cache/frontend,mode=max",
    "type=inline",
  ]
}

target "ffmpeg" {
  inherits   = ["_common"]
  context    = "./services/convertor"
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}${PROJECT}-ffmpeg:${TAG}",
  ]
  cache-from = [
    "type=local,src=.buildx-cache/ffmpeg",
    "${REGISTRY}${PROJECT}-ffmpeg:${TAG}",
  ]
  cache-to = [
    "type=local,dest=.buildx-cache/ffmpeg,mode=max",
    "type=inline",
  ]
}
