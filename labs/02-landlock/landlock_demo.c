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
     * This demo intentionally handles only a small set of filesystem
     * permissions. It is for learning, not production isolation.
     */
    const __u64 handled =
        LANDLOCK_ACCESS_FS_EXECUTE |
        LANDLOCK_ACCESS_FS_READ_FILE |
        LANDLOCK_ACCESS_FS_WRITE_FILE |
        LANDLOCK_ACCESS_FS_READ_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_FILE |
        LANDLOCK_ACCESS_FS_MAKE_REG |
        LANDLOCK_ACCESS_FS_MAKE_DIR;

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
        O_CREAT | O_WRONLY | O_TRUNC,
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
