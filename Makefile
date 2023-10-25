PYTHON	= python
PYDOC	= pydoc
PYCS	= $(shell find . -name "*.pyc")
PYCACHE	= $(shell find . -name "__pycache__")
MODULE	= indexer
TARGET	= $(MODULE).py
ARCHIVE	= $(shell basename `pwd`)
PYLINTRST	= pylintresult.txt
FLAKE8RST	= flake8result.txt

all:
	@:

edit:
	@open ./$(TARGET)

wipe: clean
	(cd ../ ; rm -f ./$(ARCHIVE).zip)
	(cd ../ ; rm -f ./$(ARCHIVE).tar)

clean:
	@for each in ${PYCS} ; do echo "rm -f $${each}" ; rm -f $${each} ; done
	@for each in ${PYCACHE} ; do echo "rm -rf $${each}" ; rm -rf $${each} ; done
	@if [ -e $(PYLINTRST) ] ; then echo "rm -f $(PYLINTRST)" ; rm -f $(PYLINTRST) ; fi
	@if [ -e $(FLAKE8RST) ] ; then echo "rm -f $(FLAKE8RST)" ; rm -f $(FLAKE8RST) ; fi
	@find . -name ".DS_Store" -exec rm {} ";" -exec echo rm -f {} ";"

test:
ifeq ($(MODULE),crawler)
	@$(PYTHON) ./$(TARGET) --article_nums 100 --output_path output
endif

ifeq ($(MODULE),indexer)
	@$(PYTHON) ./$(TARGET)
endif
	
doc:
	@$(PYDOC) ./$(TARGET)

zip: clean
	(cd ../ ; rm -f ./$(ARCHIVE).zip)
	(cd ../ ; zip -r ./$(ARCHIVE).zip ./$(ARCHIVE)/ --exclude='*/.svn/*' --exclude='*/.python-version' --exclude='*/.tool-versions')

tar: clean
	(cd ../ ; rm -f ./$(ARCHIVE).tar)
	(cd ../ ; tar -cvf ./$(ARCHIVE).tar --exclude='*/.svn/*' --exclude='*/.python-version' --exclude='*/.tool-versions' ./$(ARCHIVE)/)

pydoc:
	(sleep 3 ; open http://localhost:9999/$(MODULE).html) & $(PYDOC) -p 9999

lint:
	pylint --exit-zero --reports y $(TARGET) > $(PYLINTRST)
	flake8 --exit-zero --statistics $(TARGET) > $(FLAKE8RST)
	@less $(PYLINTRST)
	@less $(FLAKE8RST)

pip:
	pip install -U pip

pylint:
	@PYPIPACKAGE=pylint; \
	if [ -z $(pip list --format=freeze | grep ^$${PYPIPACKAGE}==) ]; \
	then \
		pip install $${PYPIPACKAGE}; \
	else \
		pip install -U $${PYPIPACKAGE}; \
	fi

flake8:
	@PYPIPACKAGE=flake8; \
	if [ -z $(pip list --format=freeze | grep ^$${PYPIPACKAGE}==) ]; \
	then \
		pip install $${PYPIPACKAGE}; \
	else \
		pip install -U $${PYPIPACKAGE}; \
	fi

requests:
	@PYPIPACKAGE=requests; \
	if [ -z $(pip list --format=freeze | grep ^$${PYPIPACKAGE}==) ]; \
	then \
		pip install $${PYPIPACKAGE}; \
	else \
		pip install -U $${PYPIPACKAGE}; \
	fi

beautifulsoup4:
	@PYPIPACKAGE=beautifulsoup4; \
	if [ -z $(pip list --format=freeze | grep ^$${PYPIPACKAGE}==) ]; \
	then \
		pip install $${PYPIPACKAGE}; \
	else \
		pip install -U $${PYPIPACKAGE}; \
	fi

list: pip
	@(pip list --format=freeze | grep ^pip==)
	@(pip list --format=freeze | grep ^pylint==)
	@(pip list --format=freeze | grep ^flake8==)
	@(pip list --format=freeze | grep ^requests==)
	@(pip list --format=freeze | grep ^beautifulsoup4==)

prepare: pip pylint flake8 requests beautifulsoup4

update: prepare
