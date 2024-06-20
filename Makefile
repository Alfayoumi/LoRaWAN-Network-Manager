VERSION=0.1.0
NAME=backend
DOCKER_NAME_FULL=$(NAME):$(VERSION)

.EXPORT_ALL_VARIABLES:

clean:
	@find . -iname "*~" -delete
	@find . -iname "*.pyc" -delete
	@rm -rf build

build: clean
	docker-compose build ${NAME}


restart: stop  start

#to use the following commands
# make start ARGS="--option1 value1"

start:
	./scripts/start-services.sh $(ARGS)

stop:
	./scripts/stop-services.sh $(ARGS)

# make delete ARGS="-c my_container_name -d"
delete:
	./scripts/delete-container.sh $(ARGS)

delete-all:
	./scripts/delete_all.sh $(ARGS)

test-all-local:
	./scripts/run_tests_local.sh
