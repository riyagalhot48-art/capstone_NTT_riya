// Box.asm  -  K = 10
// Black box while any key is pressed. Rows 10..29, 3 words wide (48 px).
// Start address = SCREEN + 32*10 = 16384 + 320 = 16704

(LOOP)
    @KBD
    D=M
    @PRESSED
    D;JNE           // key pressed -> go set color to black
    @color
    M=0             // no key -> white
    @DRAW
    0;JMP
(PRESSED)
    @color
    M=-1            // black (all 16 bits = 1)

(DRAW)
    @16704
    D=A
    @addr
    M=D             // addr = first word of row 10
    @20
    D=A
    @rows
    M=D             // rows left = 20

(ROWLOOP)
    @color
    D=M
    @addr
    A=M
    M=D             // word 0 of this row
    A=A+1
    M=D             // word 1
    A=A+1
    M=D             // word 2 (3 words = 48 px)

    @32
    D=A
    @addr
    M=D+M           // move to next row (+32 words)

    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT           // repeat until 20 rows done

    @LOOP
    0;JMP