#include "BetaElephant.h"
#include <iostream>
#include <cstdlib>
#include <time.h>

using namespace std;

#define lemda 0.5

int main(){
	srand(time(0));
	PreGenInit();

	char infen[100];
	cin.getline(infen, 100);

	char * a = genProtMove(infen);
	cout << a;
	cin >> a;
}
