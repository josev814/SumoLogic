VERSION?=1.0

clean:
	rm -rf build
	rm -rf SumoLogic/*.pyc

tarball: clean
	cd .. && tar czf sumologic-$(VERSION).tar.gz sumologic --exclude=.git

