################################################################
# Containerization stuff
################################################################

# For absolute path usage later
cwd := $(shell pwd)

.PHONY:	docker
docker:
	docker build --tag 'colloids' .
	docker run \
		--mount type=bind,source="${cwd}",target="/host" \
		-i \
		-t colloids:latest \

.PHONY:	podman
podman:
	podman build --tag 'colloids' .
	podman run \
		--mount type=bind,source="${cwd}",target="/host" \
		-i \
		-t colloids:latest \
