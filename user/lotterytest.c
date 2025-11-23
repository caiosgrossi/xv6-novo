#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"
#include "kernel/pstat.h"

void spin() {
  int i = 0;
  int j = 0;
  volatile int k = 0;
  for(i = 0; i < 500; ++i) {
    for(j = 0; j < 10000000; ++j) {
      k = j % 10;
      k = k + 1;
    }
  }
}

void print_pinfo(struct pstat *st) {
   int i;
   for(i = 0; i < NPROC; i++) {
     if (st->inuse[i]) {
       printf("pid: %d tickets: %d ticks: %d\n", st->pid[i], st->tickets[i], st->ticks[i]);
     }
   }
}

int
main(int argc, char *argv[])
{
  int pid1, pid2, pid3;
  
  // Set parent tickets to something high so it doesn't starve, 
  // though it sleeps mostly.
  settickets(100);

  if((pid1 = fork()) == 0) {
    settickets(30);
    spin();
    exit(0);
  }

  if((pid2 = fork()) == 0) {
    settickets(20);
    spin();
    exit(0);
  }

  if((pid3 = fork()) == 0) {
    settickets(10);
    spin();
    exit(0);
  }

  struct pstat st;
  int time_steps = 0;
  
  // Monitor for a while
  while(time_steps < 20) {
    if(getpinfo(&st) == 0) {
      printf("\nTime step %d:\n", time_steps);
      // Find our children and print their ticks
      int i;
      for(i = 0; i < NPROC; i++) {
        if (st.inuse[i]) {
            if (st.pid[i] == pid1) printf("Child 1 (%d tickets): %d ticks\n", st.tickets[i], st.ticks[i]);
            if (st.pid[i] == pid2) printf("Child 2 (%d tickets): %d ticks\n", st.tickets[i], st.ticks[i]);
            if (st.pid[i] == pid3) printf("Child 3 (%d tickets): %d ticks\n", st.tickets[i], st.ticks[i]);
        }
      }
    }
    pause(10); // Sleep for 10 ticks
    time_steps++;
  }

  // Kill children
  kill(pid1);
  kill(pid2);
  kill(pid3);
  wait(0);
  wait(0);
  wait(0);

  exit(0);
}
