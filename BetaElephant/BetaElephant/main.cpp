#include "BetaElephant.h"
#include <iostream>
#include <time.h>
#include <boost/python.hpp>
using namespace std;

#define lemda 0.5



char const* gen(char *infen){
    PreGenInit();
    return genMove(infen);
}



BOOST_PYTHON_MODULE(genmove){
    using namespace boost::python;
    def("gen", gen);
}




/*
int main()
{
    char *fen = "r1bak3r/4a4/2n1bc3/p1p1p3p/1c3np2/1CP6/P3P1P1P/2NCB1N2/4A4/R3KABR1 b - - 0 18";
    
    time_t t1, t2;

    t1 = clock();
    srand(time(0));
	PreGenInit();
    for (int i = 0; i<100000; i++){
	    genMove(fen);
    }
    t2 = clock();
    printf("t1: %f\n", ((double)(t2-t1)/CLOCKS_PER_SEC));

    t1 = clock();
    srand(time(0));
    for (int i = 0; i<100000; i++){
	    genMove(fen);
    }
    t2 = clock();
    printf("t2: %f\n", ((double)(t2-t1)/CLOCKS_PER_SEC));

 



*
	char infen[100];
	cin.getline(infen, 100);

	cout << a;
	cin >> a;
/
}
*/
