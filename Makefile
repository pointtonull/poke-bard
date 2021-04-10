ROOT = $(realpath .)
DEPS = $(ROOT)/deps
SRC = $(ROOT)/app
TESTS = $(ROOT)/tests
DEPS_DEV = $(VIRTUAL_ENV)
REQUIREMENTS_DEV = $(realpath requirements.txt)
REQUIREMENTS = ${SRC}/requirements.txt
RECURSE=$(MAKE) --no-print-directory
PYTHON=PYTHONPATH=$(DEPS):$(SRC) python

PROJECT = pokebard
SERVICE = FastAPI_PoC
STAGE ?= dev
STACK_NAME := $(shell echo ${PROJECT}-${SERVICE}-$(STAGE)|sed 's/_/-/g')

AWS_PROFILE ?= default
AWS_REGION ?= eu-west-2
S3_BUCKET := $(ARTEFACTS_BUCKET)
S3_KEY := fastapi_sig_api
S3_PATH := s3://${S3_BUCKET}/${S3_KEY}

VERSION := $(shell git describe --always |awk -F"[-.]" '                        \
	NF<2{print "0.0.1"} 2<NF{print $$1 "." $$2 "." $$3 + $$4}')
LOCAL_PATH := $(abspath build/${VERSION})
LAYER := $(LOCAL_PATH)/layer.zip
PACKAGE := $(LOCAL_PATH)/code.zip

.PHONY: run test coverage clean url docker-build docker-run

ifndef ARTEFACTS_BUCKET
$(error Variable ARTEFACTS_BUCKET is undefined, maybe do `source .env`)
endif
ifndef VIRTUAL_ENV
$(error Must run in a virtual environment, I recommend virtualenvwrapper.)
endif
ifndef STAGE
$(error Variable STAGE is undefined, maybe do `source .env`)
endif

help:  ## Show this help.
	@awk -F ":.*?## " '                                                     \
		/^[a-zA-Z_-]+:/&&NF==2{                                         \
			printf "\033[36m%-10s\033[0m %s\n", $$1, $$2 | "sort"   \
		}                                                               \
		/^[a-zA-Z_-]+:/&&NF==1{                                         \
			split($$1, a, ":");                                     \
			printf "\033[36m%-10s\033[0m %s\n", a[1], "--" | "sort" \
		}' $(MAKEFILE_LIST)

echo:  ## Print relevant variables
	@echo DEPS = $(DEPS)
	@echo DEPS_DEV = $(DEPS_DEV)
	@echo LOCAL_PATH = $(LOCAL_PATH)
	@echo PACKAGE = $(PACKAGE)
	@echo PROJECT = $(PROJECT)
	@echo REQUIREMENTS = $(REQUIREMENTS)
	@echo REQUIREMENTS_DEV = $(REQUIREMENTS_DEV)
	@echo S3_BUCKET = $(S3_BUCKET)
	@echo S3_KEY = $(S3_KEY)
	@echo S3_PATH = $(S3_PATH)
	@echo SRC = $(SRC)
	@echo STACK_NAME = $(STACK_NAME)
	@echo LAYER = $(LAYER)
	@echo STAGE = $(STAGE)
	@echo VERSION = $(VERSION)


run: $(DEPS)  ## Runs server locally
	cd $(SRC) &&                                                           \
	$(PYTHON) -m uvicorn --reload main:APP

deps: $(DEPS) $(DEPS_DEV)  # Installs all required dependencies

$(DEPS): $(REQUIREMENTS)
	pip install -r "$(REQUIREMENTS)" -t "$(DEPS)"
	@touch $(DEPS)

$(DEPS_DEV): $(REQUIREMENTS_DEV)
	pip install -r $(REQUIREMENTS_DEV)
	@touch $(DEPS_DEV)

build: $(LAYER) $(PACKAGE) ## creates local artefact.zip

$(LAYER): $(DEPS)
	@-rm -r '$(LOCAL_PATH)' 2>/dev/null || true
	mkdir -p '$(LOCAL_PATH)'
	cd $(DEPS) && zip -9qr '$(LAYER)' -- .

$(PACKAGE): $(SRC) $(LAYER)
	cp $(LAYER) $(PACKAGE)
	cd $(SRC) && zip -gqr '$(PACKAGE)' -- .

upload: .upload  ## pushes artefact to defined s3 path
.upload: $(PACKAGE)
	aws s3 cp --recursive '$(LOCAL_PATH)' $(S3_PATH)/$(VERSION)
	@touch .upload


deploy: .deploy ## Deploy / Update CF and Code
.deploy: upload $(CF_TEMPLATE)
	$(RECURSE) .deploy_cf_silent || $(RECURSE) explain_cf
	@touch .deploy
	@$(RECURSE) --no-print-directory list-outputs


clean:  ## clean local artefacts
	@echo "Cleaning all artefacts..."
	-rm -f .upload
	-rm -f .deploy
	-rm -rf deps


.deploy_cf_silent: validate_cf
	aws cloudformation deploy                                               \
		--capabilities CAPABILITY_IAM                                   \
		--no-fail-on-empty-changeset                                    \
		--parameter-overrides                                           \
				Env=$(STAGE)                                    \
				ArtefactsBucket=$(ARTEFACTS_BUCKET)             \
				FastAPILambdaVersion=$(VERSION)                 \
				Project=$(PROJECT)                              \
				Service=$(SERVICE)                              \
		--stack-name "$(STACK_NAME)"                                    \
		--template-file cfn/cfn.yaml
	@echo "\n\033[1mApplication resources:\033[0m"
	@echo "https://$(AWS_REGION).console.aws.amazon.com/lambda/home?region=$(AWS_REGION)#/applications/$(STACK_NAME)\n"

validate_cf:  ## Quick unexpensive verification of CF format
	@aws cloudformation validate-template                                   \
		--template-body file://cfn/cfn.yaml | jq -C .

delete:  ## Deletes CF Stack
	@aws cloudformation delete-stack                                        \
		--stack-name "$(STACK_NAME)"

explain_cf: $(DEPS_DEV)
	@aws cloudformation describe-stack-events                               \
		--stack-name "$(STACK_NAME)" > .cf.messages
	@python .cf_status.py | ccze -A

graph: doc/pipeline.png doc/pipeline.txt ## Creates diagraph using relationships definition
	@cat doc/pipeline.txt
doc/pipeline.png: doc/pipeline.dot
	@dot doc/pipeline.dot -Tpng -o doc/pipeline.png
doc/pipeline.txt: doc/pipeline.dot
	@graph-easy doc/pipeline.dot --boxart > doc/pipeline.txt

list-outputs:  ## List stack outputs
	@aws cloudformation describe-stacks                                     \
		--stack-name "$(STACK_NAME)"                                    \
		--query "Stacks[].Outputs"                                      \
		--output text

ipython: deps
	cd $(SRC);                                                              \
	$(PYTHON) -m IPython


test: deps ## Run tests
	cd $(SRC);                                                              \
	$(PYTHON) -m pytest $(TESTS)


tdd: deps ## run tests on filesystem events
	cd $(SRC)                                                               \
	&& $(PYTHON) -m pytest_watch \
		--clear                                                         \
		./                                                              \
		$(TESTS)                                                        \
		--                                                              \
		--stepwise                                                      \
		--disable-warnings                                              \
		$(TESTS)


debug_tdd: deps  ## debug tests on filesystem events
	cd $(SRC)                                                               \
	&& $(PYTHON) -m pytest_watch \
		--clear                                                         \
		--pdb                                                           \
		./                                                              \
		$(TESTS)                                                        \
		--                                                              \
		--stepwise                                                      \
		--disable-warnings                                              \
		$(TESTS)


debug: deps
	cd $(SRC)                                                               \
	&& $(PYTHON) -m pytest --stepwise -vv --pdb $(TESTS)


coverage: deps  ## run tests and report coverage
	cd $(SRC)                                                               \
	&& $(PYTHON) -m pytest                                                  \
		-v --doctest-modules ./                                         \
		--cov=./ --cov-report=term-missing                              \
		--ignore=$(DEPS)                                                \
		$(TESTS)


docker-build: .docker-build
.docker-build: app
	docker build -t $(PROJECT) .
	touch .docker-build


docker-run: docker-build
	docker run -d --name $(PROJECT)-$(STAGE) -p 80:80 $(PROJECT)

#  vim: set ts=8 sw=8 tw=0 noet :
