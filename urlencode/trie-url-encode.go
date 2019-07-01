package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"strings"
)

type Trie struct {
	children [256]*Trie
	terminal bool
}

func readdict() (*Trie, int) {
	root := new(Trie)
	maxLength := 0

	data, err := ioutil.ReadFile(`urlencode-go-dict.txt`)
	if err != nil {
		panic(1)
	}

	for _, entry := range strings.Split(string(data), "\n") {
		length := len(entry)
		if length > 0 {
			if length > maxLength {
				maxLength = length
			}

			entryBytes := []byte(entry)
			node := root
			for i := 0; i < length; i++ {
				b := entryBytes[i]
				if node.children[b] == nil {
					node.children[b] = new(Trie)
				}
				node = node.children[b]
				if i == length-1 {
					node.terminal = true
				}
			}
		}
	}
	return root, maxLength
}

func getEntry(buf []byte, bufSize int, index int, trieDict *Trie) (bool, int) {
	node := trieDict
	isEntry := false
	length := 1
	for j := index; j < bufSize; j++ {
		b := buf[j]
		if node.children[b] == nil {
			break
		} else {
			node = node.children[b]
			if node.terminal {
				isEntry = true
				length = (j - index + 1)
			}
		}

	}
	return isEntry, length
}

func encodeBuf(buf []byte, bufSize int, trieDict *Trie, encodeTable []string, bufRest int) (string, int) {
	var result []string
	i := 0
	for i < bufSize-bufRest {
		isEntry, length := getEntry(buf, bufSize, i, trieDict)
		if isEntry {
			result = append(result, string(buf[i:i+length]))
			i += length
		} else {
			result = append(result, encodeTable[buf[i]])
			i += 1
		}
	}
	return strings.Join(result, ""), i
}

func main() {
	const BUFSIZE = 1024 // 読み込みバッファのサイズ
	const ESCAPE = "%"

	numhex := [16]string{
		"0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
		"a", "b", "c", "d", "e", "f"}

	encodeTable := make([]string, 256)
	for i := 0; i < 256; i++ {
		encodeTable[i] = ESCAPE + numhex[(i/16)] + numhex[(i%16)]
	}

	charDict, maxDictLength := readdict()
	bufRestMax := maxDictLength + 1 // バッファ末尾が文字の途中にならないように余裕をもたせる

	buf := make([]byte, BUFSIZE)
	bufRestSize := 0
	for {
		buf2 := buf[bufRestSize:len(buf)]
		bufSize, err := os.Stdin.Read(buf2)
		bufSize = bufSize + bufRestSize

		if err == io.EOF || bufSize <= 0 {
			break
		} else if err != nil {
			panic(1)
		}

		result, restStart := encodeBuf(buf, bufSize, charDict, encodeTable, bufRestMax)

		if len(result) > 0 {
			fmt.Print(result)
		}

		i := restStart
		bufRestSize = 0
		for i < bufSize {
			buf[bufRestSize] = buf[i]
			bufRestSize += 1
			i += 1
		}
	}

	if bufRestSize > 0 {
		result, _ := encodeBuf(buf, bufRestSize, charDict, encodeTable, 0)
		fmt.Print(result)
	}
}
