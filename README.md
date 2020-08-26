# LLVM4

## About

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


## Steps

* Step XX corresponds to 'stepxx' tag in git

### Step 01

* Simple grammar
* All numbers are `float`
* Supported Buitin Functions
  * write($number)
    * write $number in stdout and \n
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
* Supported Buitin Functions -> Same as Step01
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

### Step 03

* Added variables which must be defined before using
* Function definition + initialization (int x=3;) is not supported
* Added function arguments
* Supported Buitin Functions -> Same as Step01
* Input examples:

```c
int add(int a,int b){
	return a+b;;
}

int main(){
	int x;
	int y;
	x=2;
	write(x*2);
	y=3;
	write(add(1,2));
	write(add(x,y));
	return 0;
}
```


