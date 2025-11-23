#include "kernel/param.h"
#include "kernel/types.h"
#include "kernel/pstat.h"
#include "user/user.h"

int main(int argc, char *argv[]) {
    struct pstat st;

    printf("Setting tickets to 10...\n");
    if (settickets(10) < 0) {
        printf("settickets failed\n");
        exit(1);
    }

    printf("Getting pinfo...\n");
    if (getpinfo(&st) < 0) {
        printf("getpinfo failed\n");
        exit(1);
    }

    printf("Success!\n");
    exit(0);
}
