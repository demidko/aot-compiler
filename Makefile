build-mrd: build-jar
	java -jar build/libs/*-all.jar
build-jar:
	gradle clean build