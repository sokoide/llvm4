# LLVM4 - Step 02

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

## Supported Numbers

* All numbers are float internally

## Supported Buitin Functions

* write($number)
  * write $number in stdout and \n

## Steps

### Step 01

* Simple grammar
* All numbers are float
* Input examples:

```c
int main(){
	write(1);
	write(3+4*(1.2+2.3));
	return 0;
}
```

### Step 02

* Changed all numbers from float to integers
* Added functions, but function arguments are not supported yet
* Input examples:

```c
int foo(){
	return 2*3;;
}

int main(){
	write(1);
	write(foo());
	return 0;
}
```


