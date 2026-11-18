CC ?= cc
CFLAGS ?= -Wall -Wextra -O2

all: landlock_demo

landlock_demo: landlock_demo.c
	$(CC) $(CFLAGS) landlock_demo.c -o landlock_demo

clean:
	rm -f landlock_demo
