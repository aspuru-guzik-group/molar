IMAGE_TAG=matterlab/molar


.PHONY: build push
build:
	python setup.py bdist_wheel
	LAST_WHEEL=$$(ls -Art dist/molar-*.whl | tail -n 1); \
	DOCKER_BUILDKIT=1 docker build -t ${IMAGE_TAG} \
		--build-arg MOLAR_PKG_WHEEL=$$LAST_WHEEL --compress .

push:
	docker push ${IMAGE_TAG}

twine:
	LAST_WHEEL=$$(ls -Art dist/molar-*.whl | tail -n 1); \
	twine upload -u tgaudin -p $(pass pypi/login) $$LAST_WHEEL 
