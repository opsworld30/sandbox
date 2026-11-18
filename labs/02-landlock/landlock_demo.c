#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <linux/landlock.h>
#include <stdio.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

static int landlock_create_ruleset(
    const struct landlock_ruleset_attr *attr,
    size_t size,
    __u32 flags
) {
    return syscall(
        SYS_landlock_create_ruleset,
        attr,
        size,
        flags
    );
}

static int landlock_add_rule(
    int ruleset_fd,
    enum landlock_rule_type type,
    const void *rule_attr
) {
    return syscall(
        SYS_landlock_add_rule,
        ruleset_fd,
        type,
        rule_attr,
        0
    );
}

static int landlock_restrict_self(int ruleset_fd) {
    return syscall(
        SYS_landlock_restrict_self,
        ruleset_fd,
        0
    );
}

int main(void) {
    /*
     * This is a teaching demo, not a production policy.
     * Landlock only denies access rights listed in handled_access_fs.
     * Rights omitted here remain governed by the ordinary OS permissions.
     */
    int abi = landlock_create_ruleset(
        NULL,
        0,
        LANDLOCK_CREATE_RULESET_VERSION
    );

    if (abi < 1) {
        if (abi < 0) {
            perror("Landlock is unavailable or disabled");
        } else {
            fprintf(stderr, "Landlock ABI is too old: %d\n", abi);
        }
        return 1;
    }

    __u64 handled =
        LANDLOCK_ACCESS_FS_EXECUTE |
        LANDLOCK_ACCESS_FS_READ_FILE |
        LANDLOCK_ACCESS_FS_WRITE_FILE |
        LANDLOCK_ACCESS_FS_READ_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_FILE |
        LANDLOCK_ACCESS_FS_MAKE_CHAR |
        LANDLOCK_ACCESS_FS_MAKE_DIR |
        LANDLOCK_ACCESS_FS_MAKE_REG |
        LANDLOCK_ACCESS_FS_MAKE_SOCK |
        LANDLOCK_ACCESS_FS_MAKE_FIFO |
        LANDLOCK_ACCESS_FS_MAKE_BLOCK |
        LANDLOCK_ACCESS_FS_MAKE_SYM;

#ifdef LANDLOCK_ACCESS_FS_REFER
    if (abi >= 2) {
        handled |= LANDLOCK_ACCESS_FS_REFER;
    }
#endif
#ifdef LANDLOCK_ACCESS_FS_TRUNCATE
    if (abi >= 3) {
        handled |= LANDLOCK_ACCESS_FS_TRUNCATE;
    }
#endif
#ifdef LANDLOCK_ACCESS_FS_IOCTL_DEV
    if (abi >= 5) {
        handled |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
    }
#endif
#ifdef LANDLOCK_ACCESS_FS_RESOLVE_UNIX
    if (abi >= 9) {
        handled |= LANDLOCK_ACCESS_FS_RESOLVE_UNIX;
    }
#endif

    printf("Detected Landlock ABI: %d\n", abi);

    struct landlock_ruleset_attr ruleset_attr = {
        .handled_access_fs = handled,
    };

    int ruleset_fd = landlock_create_ruleset(
        &ruleset_attr,
        sizeof(ruleset_attr),
        0
    );

    if (ruleset_fd < 0) {
        perror("landlock_create_ruleset");
        return 1;
    }

    /*
     * Open the directory before entering the Landlock domain.
     * The O_PATH descriptor identifies the directory hierarchy.
     */
    int workspace_fd = open(
        "workspace",
        O_PATH | O_CLOEXEC
    );

    if (workspace_fd < 0) {
        perror("open workspace");
        return 1;
    }

    struct landlock_path_beneath_attr path_rule = {
        .allowed_access = handled,
        .parent_fd = workspace_fd,
    };

    if (landlock_add_rule(
            ruleset_fd,
            LANDLOCK_RULE_PATH_BENEATH,
            &path_rule) < 0) {
        perror("landlock_add_rule");
        return 1;
    }

    /*
     * This demo is single-threaded. landlock_restrict_self() restricts
     * the calling thread and its future children; it does not retroactively
     * confine unrelated threads that already existed.
     *
     * An unprivileged process normally uses no_new_privs before
     * restricting itself with Landlock.
     */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return 1;
    }

    if (landlock_restrict_self(ruleset_fd) < 0) {
        perror("landlock_restrict_self");
        return 1;
    }

    close(ruleset_fd);
    close(workspace_fd);

    printf("Landlock policy is active.\n");

    /*
     * Allowed: file is inside workspace.
     */
    int ok_fd = open(
        "workspace/hello.txt",
        O_RDONLY
    );

    if (ok_fd >= 0) {
        printf("workspace/hello.txt: ALLOW\n");
        close(ok_fd);
    } else {
        printf("workspace/hello.txt: DENY (%s)\n",
               strerror(errno));
    }

    /*
     * Denied: file is outside the allowed hierarchy.
     */
    int secret_fd = open(
        "secret.txt",
        O_RDONLY
    );

    if (secret_fd >= 0) {
        printf("secret.txt: UNEXPECTED ALLOW\n");
        close(secret_fd);
    } else {
        printf("secret.txt: DENY (%s)\n",
               strerror(errno));
    }

    /*
     * Allowed: create a new regular file under workspace.
     */
    int created_fd = open(
        "workspace/created.txt",
        O_CREAT | O_WRONLY,
        0600
    );

    if (created_fd >= 0) {
        const char *message = "created inside Landlock workspace\n";
        write(created_fd, message, strlen(message));
        close(created_fd);
        printf("workspace/created.txt: WRITE ALLOW\n");
    } else {
        printf("workspace/created.txt: WRITE DENY (%s)\n",
               strerror(errno));
    }

    return 0;
}
