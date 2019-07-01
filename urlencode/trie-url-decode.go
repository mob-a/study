package main

import (
	"io"
	"os"
)

func decode() {

}
func main() {
	const BUFSIZE = 1024 // 読み込みバッファのサイズ
	const ESCAPE = "%"
	const ESCAPEB = '%'

	var numbyte [256]int
	for k := 0; k < 256; k++ {
		numbyte[k] = -1
	}
	numbyte[48] = 0
	numbyte[49] = 1
	numbyte[50] = 2
	numbyte[51] = 3
	numbyte[52] = 4
	numbyte[53] = 5
	numbyte[54] = 6
	numbyte[55] = 7
	numbyte[56] = 8
	numbyte[57] = 9
	numbyte[97] = 10
	numbyte[98] = 11
	numbyte[99] = 12
	numbyte[100] = 13
	numbyte[101] = 14
	numbyte[102] = 15

	numhex := [16]string{
		"0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
		"a", "b", "c", "d", "e", "f"}

	decodeTable := make(map[string]byte)
	for i := 0; i < 256; i++ {
		k := ESCAPE + numhex[(i/16)] + numhex[(i%16)]
		decodeTable[k] = byte(i)
	}

	buf := make([]byte, BUFSIZE)

	const OUT_ENCODED = -2
	const FIRST_ENCODED = -1
	decodeState := OUT_ENCODED
	for {
		n, err := os.Stdin.Read(buf)

		if err == io.EOF || n <= 0 {
			break
		} else if err != nil {
			panic(1)
		}

		var resultBuf []byte
		for i := 0; i < n; i++ {
			b := buf[i]
			if b == '\r' || b == '\n' {
				continue
			}

			if b == ESCAPEB {
				if decodeState != OUT_ENCODED {
					panic(1)
				}
				decodeState = FIRST_ENCODED
			} else if decodeState == FIRST_ENCODED {
				v := numbyte[b]
				if v < 0 {
					panic(1)
				}
				decodeState = v * 16
			} else if decodeState >= 0 {
				v := numbyte[b]
				if v < 0 {
					panic(1)
				}
				resultBuf = append(resultBuf, byte(decodeState+v))
				decodeState = OUT_ENCODED
			} else {
				resultBuf = append(resultBuf, b)
			}

		}
		os.Stdout.Write(resultBuf)
	}
}
