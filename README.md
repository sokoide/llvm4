# LLVM4 - Step 01

## About

* Step XX means the README is for 'stepxx' tag in git
* LLVM frontend (IR generation) Simple language example with Antlr4 for Python3
* Please refer to the following 2 for simpler versions
  * [LLVM1](https://github.com/sokoide/llvm1)
  * [LLVM2](https://github.com/sokoide/llvm2)
  * [LLVM3](https://github.com/sokoide/llvm3)


## How to build

* Change ANTLR4 in Makefile and run `make` to build

## How to run

* Run `make test` to see what happens

```sh
make test

```

## Supported Inputs

* The follwing inputs are supported
* See grammar/SoLang4.g4 for details

```c
int main(){
	write(1);
	write(1*2.3+(4+6)/2);
	write(2);
	return 0;
}
```


