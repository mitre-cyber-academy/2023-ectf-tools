# Tasks

## Attack and Design

- Develop exploits for the `uart_readline()` buffer overflow. One exploit for arbitrary read. Another exploit for arbitrary write. Test the exploits on the reference system (Gaoxiang)
- Fix the `uart_readline` bug by adding length in the function (Gaoxiang)
- Fix `strcpy()` and other unsafe functions
- Add stack cookies in compiling our system (Zheyuan)
- Add MPU to add DEP to stack (Zheyuan)
- Check the entropy source of MBed TLS (Zheyuan, Xi)

## Tools

1. Port the host tools to be independent from the docker conatiner
   - unlock_tool
   - pair_tool
   - enable_tool
2. Build a customized board firmware that can receive the `UART1` message, relay it, and send it out through `UART0`
3. Build a customized board firmware and a host tool. The firmware can receive the `UART1` message, relay it to `UART0`. It also can receive message from `UART0` and send through the `UART1`. The host tool is able to receive the message from `UART0` and send it back to `UART0`