#include <stdio.h>

int main(){
  int b, e, res;

  scanf("%d",&b);
  scanf("%d",&e);

  res = 1;

  for (;e>0;e--) res *= b;

  printf("%d",res);
  return 0;
}