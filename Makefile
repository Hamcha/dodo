all: dep dodo

dodo:
	go build -o dodo ./src

dep:
	go get github.com/cloudflare/gokabinet/kc
	go get github.com/gorilla/mux
	go get github.com/hoisie/mustache
	touch dep

clean:
	rm -f dep
	rm -f dodo