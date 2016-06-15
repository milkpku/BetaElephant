#include "../mcts-xboard/BetaElephant.h"
#include <iostream>
#include <time.h>
#include <boost/python.hpp>
#include <stdlib.h>
using namespace std;

void turn_round(char *str){
    
    char *tail = strstr(str, " ");
    if(*(tail+1)=='b')
        *(tail+1)='w';
    else
        *(tail+1)='b';    
}

char const* gen(char *infen){
    char *in = (char *)malloc(1024*sizeof(char));
    strcpy(in, infen);
    char *out = (char *)malloc(1024*sizeof(char)); 
    char *selfmove, *selfprot, *emymove, *emyprot;
    PreGenInit();
    selfmove = genMove(in);
    strcat(out, selfmove);
    turn_round(in);
    emymove = genMove(in);
    strcat(out, emymove);
    turn_round(in);
    selfprot = genProtMove(in);
    strcat(out, selfprot);
    turn_round(in);
    emyprot = genProtMove(in);
    strcat(out, emyprot);
    return out;
}

BOOST_PYTHON_MODULE(genmove){
    using namespace boost::python;
    def("gen", gen);
}
