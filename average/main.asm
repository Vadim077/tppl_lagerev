section .text
global main
default rel
extern printf

BUFFER_SIZE equ 65536

main:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    sub rsp, 8

    cmp rdi, 2
    jl no_args

    mov rax, [rsi + 8]
    mov [filename], rax

    ; --- Открытие файла (sys_open) ---
    mov rax, 2
    mov rdi, [filename]
    xor rsi, rsi
    xor rdx, rdx
    syscall
    test rax, rax
    js open_error
    mov [fd], rax

    ; --- Чтение файла в буфер (sys_read) ---
    mov rax, 0
    mov rdi, [fd]
    lea rsi, [buffer]
    mov rdx, BUFFER_SIZE
    syscall
    test rax, rax
    jle read_error
    mov [bytes_read], rax

    ; --- Закрытие файла (sys_close) ---
    mov rax, 3
    mov rdi, [fd]
    syscall

    lea rsi, [buffer]          ; rsi = начало данных
    mov rdi, rsi
    add rdi, [bytes_read]      ; rdi = конец прочитанных данных

    call parse_line            ; первая строка (x)
    jc format_error
    mov rbx, rax               ; rbx = сумма x
    mov r12, rcx               ; r12 = количество чисел x

    call parse_line            ; вторая строка (y)
    jc format_error
    cmp rcx, r12               ; количество чисел должно совпадать
    jne format_error
    sub rbx, rax               ; rbx = (сумма x) - (сумма y)

.trail:
    cmp rsi, rdi
    jae .compute
    mov r10b, [rsi]
    inc rsi
    cmp r10b, ' '
    je .trail
    cmp r10b, 9
    je .trail
    cmp r10b, 10
    je .trail
    cmp r10b, 13
    je .trail
    jmp format_error

.compute:
    mov rax, rbx               ; rax = делимое
    cqo
    idiv r12                   ; rax = sum / count

    ; --- Вывод результата через printf ---
    lea rdi, [fmt_result]
    mov rsi, [filename]
    mov rdx, rax
    xor rax, rax
    call printf

    add rsp, 8
    pop r12
    pop rbx
    pop rbp
    xor eax, eax
    ret

read_error:
    mov rax, 3
    mov rdi, [fd]
    syscall

open_error:
format_error:
    lea rdi, [fmt_error]
    mov rsi, [filename]
    xor rax, rax
    call printf

    add rsp, 8
    pop r12
    pop rbx
    pop rbp
    mov eax, 1
    ret

no_args:
    lea rdi, [fmt_usage]
    xor rax, rax
    call printf

    add rsp, 8
    pop r12
    pop rbx
    pop rbp
    mov eax, 1
    ret

; ---------------------------------------------------------------------------
skip_ws:
.loop:
    cmp rsi, rdi
    jae .done
    mov r10b, [rsi]
    cmp r10b, ' '
    je .skip
    cmp r10b, 9
    je .skip
    cmp r10b, 13
    jne .done
.skip:
    inc rsi
    jmp .loop
.done:
    ret

; ---------------------------------------------------------------------------
parse_line:
    xor rax, rax
    xor rcx, rcx

.next_number:
    call skip_ws
    cmp rsi, rdi
    jae .error

    xor r8, r8
    cmp byte [rsi], '-'
    jne .check_plus
    mov r8, 1
    inc rsi
    jmp .digits

.check_plus:
    cmp byte [rsi], '+'
    jne .digits
    inc rsi

.digits:
    xor rdx, rdx
    xor r9, r9
.digit_loop:
    cmp rsi, rdi
    jae .digits_done
    movzx r10, byte [rsi]
    sub r10, '0'
    cmp r10, 9
    ja .digits_done
    imul rdx, rdx, 10
    add rdx, r10
    inc rsi
    inc r9
    jmp .digit_loop

.digits_done:
    test r9, r9
    jz .error
    test r8, r8
    jz .add
    neg rdx

.add:
    add rax, rdx
    inc rcx
    call skip_ws
    cmp rsi, rdi
    jae .ok

    mov r10b, [rsi]
    inc rsi
    cmp r10b, ','
    je .next_number
    cmp r10b, 10
    je .ok

.error:
    stc
    ret

.ok:
    clc
    ret

; ---------------------------------------------------------------------------
section .data
    fmt_result db "%s: %ld", 10, 0
    fmt_error  db "%s: файл испорчен", 10, 0
    fmt_usage  db "Usage: ./average <filename>", 10, 0

section .bss
    fd         resq 1
    filename   resq 1
    bytes_read resq 1
    buffer     resb BUFFER_SIZE
