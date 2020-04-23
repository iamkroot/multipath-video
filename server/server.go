package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"

	"github.com/lucas-clemente/quic-go/h2quic"
)

func main() {
	dir := flag.String("dir", "", "Path to directory to be served, required")
	port := flag.Int("port", 6060, "The port to bind")
	protocol := flag.String("protocol", "quic", "The protocol to be used")
	certPath := flag.String("cert", "cert.crt", "Path to TLS cert file, required for quic")
	keyPath := flag.String("key", "priv.key", "Path to TLS key file, required for quic")
	flag.Parse()
	if *dir == "" {
		panic("parameter 'dir' is required")
	}
	fs := http.FileServer(http.Dir(*dir))
	addr := fmt.Sprintf(":%v", *port)
	fmt.Println("Creating", *protocol, "server at", addr)
	if *protocol == "quic" {
		log.Fatal(h2quic.ListenAndServeQUIC(addr, *certPath, *keyPath, fs))
	} else if *protocol == "tcp" {
		log.Fatal(http.ListenAndServe(addr, fs))
	} else {
		panic("Unrecognized protocol")
	}
}
