all:
	python2.4 ./setup.py build  
clean: 	
	python2.4 setup.py clean --all
install:
	python2.4 setup.py install --root $(DESTDIR)
