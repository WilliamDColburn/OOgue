all:
	-echo "Options are: push, autopush, pull, add, newversion"

push:
	git commit -a
	git push

autopush:
	git commit -a -m "autopush"
	git push

pull:
	git pull

add:
	git add *.py

newversion:
	date +%s > .tmp
	sed -i "s/^__OOGUEVERSION__ = .*/__OOGUEVERSION__ = `cat .tmp`/" *.py
	/usr/bin/rm oogue-*.tar.gz
	tar zcvf oogue-`cat .tmp`.tar.gz README *.py
