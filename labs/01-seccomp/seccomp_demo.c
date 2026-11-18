#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <seccomp.h>

int main(void) {
    scmp_filter_ctx ctx;

    printf("before seccomp: process is running normally\n");

    ctx = seccomp_init(SCMP_ACT_ALLOW);
    if (ctx == NULL) {
        fprintf(stderr, "seccomp_init failed\n");
        return 1;
    }

    /*
     * Demonstration only:
     * keep the default action as ALLOW,
     * but return EPERM whenever mkdirat is requested.
     *
     * This is intentionally not a production sandbox profile.
     */
    if (seccomp_rule_add(
            ctx,
            SCMP_ACT_ERRNO(EPERM),
            SCMP_SYS(mkdirat),
            0) < 0) {
        fprintf(stderr, "seccomp_rule_add failed\n");
        seccomp_release(ctx);
        return 1;
    }

    if (seccomp_load(ctx) < 0) {
        fprintf(stderr, "seccomp_load failed\n");
        seccomp_release(ctx);
        return 1;
    }

    seccomp_release(ctx);

    printf("seccomp filter loaded\n");

    const char *path = "/tmp/seccomp-demo-created-by-filter";

    /*
     * Call the exact syscall being filtered. mkdirat is available across modern
     * Linux architectures and is the underlying operation used by many libc
     * mkdir() wrappers. SCMP_SYS(mkdirat) resolves the native syscall number.
     */
    long rc = syscall(SCMP_SYS(mkdirat), AT_FDCWD, path, 0700);
    if (rc == -1) {
        printf("mkdir syscall blocked as expected: errno=%d (%s)\n",
               errno, strerror(errno));
    } else {
        printf("unexpected success: %s\n", path);
        rmdir(path);
    }

    /*
     * Normal stdout and process exit still work because their
     * required syscalls were not filtered.
     */
    printf("normal execution continues\n");

    return 0;
}
