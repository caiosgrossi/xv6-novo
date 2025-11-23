#include "kernel/types.h"
#include "kernel/stat.h"
#include "user.h"
#include "pstat.h"

int
main(int argc, char *argv[])
{
  struct pstat st;
  if(getpinfo(&st) < 0){
    printf("getpinfo failed\n");
    exit(1);
  }

  printf("pid\tinuse\ttickets\tticks\n");
  for(int i = 0; i < NPROC; i++){
    if(st.inuse[i]){
      printf("%d\t%d\t%d\t%d\n", st.pid[i], st.inuse[i], st.tickets[i], st.ticks[i]);
    }
  }
  exit(0);
}
