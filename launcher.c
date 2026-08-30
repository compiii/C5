// Privileged boundary: Linux-only, fixed paths and a dedicated caller/UID range.
// Requires an independent Linux sandbox review before installing setuid.
#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <grp.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <dirent.h>
#include <fcntl.h>
#include <errno.h>
#ifdef __linux__
#include <sys/prctl.h>
#else
static int clearenv(void) { return -1; } // syntax checks only; main refuses non-Linux
#endif
#ifndef C5_SERVICE_UID
#define C5_SERVICE_UID 0 /* fail closed unless explicitly set at build time */
#endif
#define UID_FIRST 50000
#define UID_LAST 50999

static void die(void) { fputs("C5 launcher refused\n", stderr); exit(1); }
static long number(const char *s, long low, long high) {
    char *end;
    errno = 0;
    long n = strtol(s, &end, 10);
    if (errno || !*s || *end || n < low || n > high) die();
    return n;
}
static int directory(int parent, const char *name) {
    int fd = openat(parent, name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) die();
    return fd;
}
static int absolute_dir(const char *path) {
    int fd = directory(AT_FDCWD, "/");
    char buffer[512];
    if (strlen(path) >= sizeof(buffer)) die();
    strcpy(buffer, path);
    char *save, *part = strtok_r(buffer, "/", &save);
    while (part) {
        int next = directory(fd, part);
        close(fd); fd = next; part = strtok_r(NULL, "/", &save);
    }
    return fd;
}
static void owned_tree(int fd, uid_t uid, gid_t service_group, unsigned depth) {
    struct stat st;
    if (depth > 32 || fstat(fd, &st)) die();
    if (st.st_uid != getuid() && st.st_uid != uid) die();
    if (S_ISREG(st.st_mode)) {
        if (st.st_nlink != 1) die(); // no privileged hard-link ownership changes
    } else if (!S_ISDIR(st.st_mode)) die();
    if (S_ISDIR(st.st_mode)) {
        DIR *content = fdopendir(dup(fd));
        if (!content) die();
        struct dirent *entry;
        while ((entry = readdir(content))) {
            if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
            int child = openat(fd, entry->d_name, O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
            if (child < 0) die();
            owned_tree(child, uid, service_group, depth + 1);
            close(child);
        }
        closedir(content);
    }
    mode_t mode = S_ISDIR(st.st_mode) ? 0770 : ((st.st_mode & 0111) ? 0770 : 0660);
    if (fchown(fd, uid, service_group) || fchmod(fd, mode)) die();
}
static void limit(int resource, rlim_t amount) {
    struct rlimit value = {amount, amount};
    if (setrlimit(resource, &value)) die();
}
int main(int argc, char **argv) {
#ifndef __linux__
    (void)argc; (void)argv;
    die();
#endif
    if (argc < 6 || C5_SERVICE_UID == 0 || getuid() != C5_SERVICE_UID || geteuid() != 0) die();
    uid_t uid = (uid_t)number(argv[2], UID_FIRST, UID_LAST);
    long cpu = number(argv[4], 1, 10);
    char home[128], uid_name[32], group_name[64];
    snprintf(home, sizeof(home), "PROC/%u/HOME", uid);
    if (strcmp(home, argv[3])) die();
    if (strcmp(argv[5], "a.out") && strcmp(argv[5], "target/debug/home") &&
        strcmp(argv[5], "/usr/bin/swipl")) die();
    if (!*argv[1] || strlen(argv[1]) > 4096 ||
        strspn(argv[1], "abcdefghijklmnopqrstuvwxyz0123456789_:") != strlen(argv[1])) die();

    int libdir = absolute_dir("/opt/c5/lib");
    struct stat st;
    if (fstat(libdir, &st) || st.st_uid || (st.st_mode & 0022)) die();
    int lib = openat(libdir, "libsandbox.so", O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (lib < 0 || fstat(lib, &st) || !S_ISREG(st.st_mode) || st.st_uid || (st.st_mode & 0022)) die();
    close(lib); close(libdir);

    int proc = absolute_dir("/var/lib/c5/runtime/PROC");
    snprintf(uid_name, sizeof(uid_name), "%u", uid);
    int userdir = directory(proc, uid_name);
    int homedir = directory(userdir, "HOME");
    close(proc); close(userdir);

    int groups = absolute_dir("/sys/fs/cgroup");
    snprintf(group_name, sizeof(group_name), "C5_%u", uid);
    if (mkdirat(groups, group_name, 0755) && errno != EEXIST) die();
    int group = directory(groups, group_name);
    close(groups);
    if (fstat(group, &st) || st.st_uid || (st.st_mode & 0022)) die();
    int procs = openat(group, "cgroup.procs", O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    if (procs < 0 || dprintf(procs, "%d\n", getpid()) < 0 || close(procs)) die();
    int killer = openat(group, "cgroup.kill", O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    if (killer < 0 || fchown(killer, getuid(), getgid())) die();
    close(killer); close(group);

    limit(RLIMIT_CPU, (rlim_t)cpu);
    limit(RLIMIT_DATA, 100*1024*1024);
    limit(RLIMIT_NPROC, 11);
    limit(RLIMIT_FSIZE, 1024*1024);
    limit(RLIMIT_CORE, 0);
    owned_tree(homedir, uid, getgid(), 0);
    if (fchdir(homedir)) die();
    close(homedir);
    umask(0007);
    if (clearenv() ||
        setenv("HOME", ".", 1) || setenv("PATH", "/bin:/usr/bin", 1) ||
        setenv("LANG", "C.UTF-8", 1) ||
        setenv("LD_PRELOAD", "/opt/c5/lib/libsandbox.so", 1) ||
        setenv("SECCOMP_SYSCALL_ALLOW", argv[1], 1)) die();
    if (setgroups(0, NULL) || setregid(uid, uid) || setreuid(uid, uid)) die();
#ifdef __linux__
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) die();
#endif
    execv(argv[5], argv + 5);
    die();
}
