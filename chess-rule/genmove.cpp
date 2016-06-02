#include "../mcts-ucci/BetaElephant.h"
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
