// cmd/myapp/main.go
package main

import (
	"fmt"
	"os"
)

func main() {
	if err := Execute(); err != nil {
		// SilenceErrors is set on the root command, so print the error ourselves
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
