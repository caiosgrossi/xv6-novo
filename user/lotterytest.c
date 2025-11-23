#include "kernel/types.h"
#include "user.h"
#include "pstat.h"

// Longer run for more stable statistics (about 1s per sample)
// Increase samples and sample faster so the run converges more quickly
#define SAMPLES 600
#define SLEEP_TICKS 1

int
main(int argc, char *argv[])
{
  int tickets[3] = {30, 20, 10};
  int pids[3];

  // fork 3 children
  for(int i = 0; i < 3; i++){
    int pid = fork();
    if(pid < 0){
      printf("fork failed\n");
      exit(1);
    }
    if(pid == 0){
      // child: set tickets and busy-loop
      settickets(tickets[i]);
      // busy loop to consume CPU
      while(1) ;
      exit(0);
    } else {
      pids[i] = pid;
    }
  }

  // parent: sample ticks and print CSV header
  // print pid and ticket info to verify settickets worked
  struct pstat st0;
  // give children some time to run settickets; poll pstat until tickets set
  int waited = 0;
  int t0=0,t1=0,t2=0;
  while(waited < 100){
    if(getpinfo(&st0) == 0){
      for(int i=0;i<NPROC;i++){
        if(st0.inuse[i]){
          if(st0.pid[i]==pids[0]) t0 = st0.tickets[i];
          if(st0.pid[i]==pids[1]) t1 = st0.tickets[i];
          if(st0.pid[i]==pids[2]) t2 = st0.tickets[i];
        }
      }
      if(t0==tickets[0] && t1==tickets[1] && t2==tickets[2]) break;
    }
    pause(1);
    waited++;
  }
  printf("pids: %d(%d), %d(%d), %d(%d)\n", pids[0], t0, pids[1], t1, pids[2], t2);
  printf("sample,%d,%d,%d\n", pids[0], pids[1], pids[2]);

  struct pstat st;
  for(int s = 0; s < SAMPLES; s++){
    if(getpinfo(&st) < 0){
      printf("getpinfo failed\n");
      break;
    }
    int ticks0 = 0, ticks1 = 0, ticks2 = 0;
    for(int i = 0; i < NPROC; i++){
      if(st.inuse[i]){
        if(st.pid[i] == pids[0]) ticks0 = st.ticks[i];
        if(st.pid[i] == pids[1]) ticks1 = st.ticks[i];
        if(st.pid[i] == pids[2]) ticks2 = st.ticks[i];
      }
    }
    printf("%d,%d,%d,%d\n", s, ticks0, ticks1, ticks2);
    pause(SLEEP_TICKS);
  }

  // kill children and wait
  for(int i = 0; i < 3; i++){
    kill(pids[i]);
    wait(0);
  }

  exit(0);
}
