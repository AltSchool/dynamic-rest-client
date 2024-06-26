APP_NAME := 'dynamic_rest_client'
INSTALL_DIR  ?= ./build

define header
	@tput setaf 6
	@echo "* $1"
	@tput sgr0
endef

.PHONY: docs

pypi_upload_test: install build
	$(call header,"Uploading new version to PyPi - test")
	@. $(INSTALL_DIR)/bin/activate; pip install twine; twine upload --repository testpypi dist/*

pypi_upload: install build
	$(call header,"Uploading new version to PyPi")
	@. $(INSTALL_DIR)/bin/activate; pip install twine; twine upload --repository dynamic-rest-client dist/*

build: install
	$(call header,"Building the package")
	@. $(INSTALL_DIR)/bin/activate; python setup.py sdist
# Build/install the app
# Runs on every command
install: $(INSTALL_DIR)
	$(call header,"Installing")
	@$(INSTALL_DIR)/bin/python setup.py -q develop

shell: install
	@$(INSTALL_DIR)/bin/python

# Install/update dependencies
# Runs whenever the requirements.txt file changes
$(INSTALL_DIR): $(INSTALL_DIR)/bin/activate
$(INSTALL_DIR)/bin/activate: requirements.txt install_requires.txt
	$(call header,"Updating dependencies")
	@test -d $(INSTALL_DIR) || virtualenv $(INSTALL_DIR)
	@$(INSTALL_DIR)/bin/pip install -q --upgrade pip==24.0 setuptools flake8==7.0.0
	@$(INSTALL_DIR)/bin/pip install -Ur requirements.txt
	@touch $(INSTALL_DIR)/bin/activate

# Removes build files in working directory
clean_working_directory:
	$(call header,"Cleaning working directory")
	@rm -rf ./.tox ./dist ./$(APP_NAME).egg-info;
	@find . -name '*.pyc' -type f -exec rm -rf {} \;

# Full clean
clean: clean_working_directory
	$(call header,"Cleaning all build files")
	@rm -rf $(INSTALL_DIR)

# Run tests
test: install lint
	$(call header,"Running unit tests")
	@$(INSTALL_DIR)/bin/py.test -s --cov=$(APP_NAME) tests/$(TEST) --ds=tests.settings

# Lint the project
lint: clean_working_directory
	$(call header,"Linting code")
	@find . -type f -name '*.py' -not -path '$(INSTALL_DIR)/*' -not -path './docs/*' -not -path '$(INSTALL_DIR)/*' | xargs $(INSTALL_DIR)/bin/flake8

# Auto-format the project
format: clean_working_directory
	$(call header,"Auto-formatting code")
	@find $(APP_NAME) -type f -name '*.py' | xargs $(INSTALL_DIR)/bin/flake8 | sed -E 's/^([^:]*\.py).*/\1/g' | uniq | xargs autopep8 --experimental -a --in-place

tox:
	pip install -U tox==4.14.2 virtualenv-pyenv==0.5.0; \
	tox --develop

migrations: install
	$(call header,"Creating test app migrations")
	$(INSTALL_DIR)/bin/python manage.py makemigrations --settings=tests.settings
