package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"strings"
	"unicode/utf8"
)

func readdict() map[uint32]string {
	m := make(map[uint32]string)
	tmpbuf := make([]byte, 4)

	data, err := ioutil.ReadFile(`/tmp/dict`)
	if err != nil {
		panic(1)
	}

	for _, uchar := range strings.Split(string(data), "\n") {
		if len(uchar) > 0 {
			r, bytesNum := utf8.DecodeLastRuneInString(uchar)
			if bytesNum != len(uchar) {
				panic(1)
			}

			utf8.EncodeRune(tmpbuf, r)
			var id uint32
			if bytesNum == 1 {
				id = uint32(tmpbuf[0])
			} else if bytesNum == 2 {
				id = (uint32(tmpbuf[0]) << 8) + uint32(tmpbuf[1])
			} else if bytesNum == 3 {
				id = (uint32(tmpbuf[0]) << 16) + (uint32(tmpbuf[1]) << 8) + uint32(tmpbuf[2])
			} else if bytesNum == 4 {
				id = (uint32(tmpbuf[0]) << 24) + (uint32(tmpbuf[1]) << 16) + (uint32(tmpbuf[2]) << 8) + uint32(tmpbuf[3])
			} else {
				panic(1)
			}
			m[id] = uchar
		}
	}
	return m
}

func getDictionaryChar(
	utf8Char uint32, utf8CharLength int, charMap map[uint32]string, encodeTable []string, head byte) (string, int) {
	// 辞書存在判定
	s, ok := charMap[utf8Char]
	if ok {
		return s, utf8CharLength
	} else {
		return encodeTable[head], 1
	}
}

func getCandChar(buf []byte, bufSize int, index int) (uint32, int) {
	// https://ja.wikipedia.org/wiki/UTF-8
	// 現在位置の1バイトが
	//  110yyyyx => 2バイト文字の可能性
	//  1110yyyy => 3バイト文字の可能性
	//  11110yyy => 4バイト文字の可能性
	// 先読みして、uint32に入れる (最大4バイトまでなので)
	//
	// 返り値: utf8char(文字ID)
	head := buf[index]
	if (head >> 5) == 6 { // 2バイト文字
		if index+1 < bufSize {
			return (uint32(buf[index]) << 8) + uint32(buf[index+1]), 2
		}
	} else if (head >> 4) == 14 { // 3バイト文字
		if index+2 < bufSize {
			return (uint32(buf[index]) << 16) + (uint32(buf[index+1]) << 8) + uint32(buf[index+2]), 3
		}
	} else if (head >> 3) == 30 { // 4バイト文字
		if index+3 < bufSize {
			return (uint32(buf[index]) << 24) + (uint32(buf[index+1]) << 16) + (uint32(buf[index+2]) << 8) + uint32(buf[index+3]), 4
		}
	}
	// 1バイト ( ascii文字 or utf8として不適切 )
	return (uint32(buf[index])), 1
}

func encodeBuf(buf []byte, bufSize int, charDict map[uint32]string, encodeTable []string, bufRest int) (string, int) {
	var result []string
	i := 0
	for i < bufSize-bufRest {
		candChar, candCharLength := getCandChar(buf, bufSize, i)
		dictChar, dictCharLength := getDictionaryChar(candChar, candCharLength, charDict, encodeTable, buf[i])
		result = append(result, dictChar)
		i += dictCharLength
	}
	return strings.Join(result, ""), i
}

func main() {
	const BUFSIZE = 1024 // 読み込みバッファのサイズ
	const BUFRESTMAX = 5 // バッファ末尾が文字の途中にならないように余裕をもたせる
	const ESCAPE = "="

	numhex := [16]string{
		"0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
		"a", "b", "c", "d", "e", "f"}

	encodeTable := make([]string, 256)
	for i := 0; i < 256; i++ {
		encodeTable[i] = ESCAPE + numhex[(i/16)] + numhex[(i%16)]
	}

	charDict := readdict()

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

		result, restStart := encodeBuf(buf, bufSize, charDict, encodeTable, BUFRESTMAX)

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
