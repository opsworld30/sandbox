CC ?= cc
CFLAGS ?= -Wall -Wextra -O2

all: seccomp_demo

seccomp_demo: seccomp_demo.c
	$(CC) $(CFLAGS) seccomp_demo.c -lseccomp -o seccomp_demo

clean:
	rm -f seccomp_demo
