#include "../mcts-xboard/BetaElephant.h"
#include <iostream>
#include <time.h>
#include <boost/python.hpp>
#include <stdlib.h>
using namespace std;

void rev_str(char *str, int len){
    char temp;
    for(int i = 0; i < len/2; i++){
        temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

void rev_letter(char *str, int len){
    for(int i = 0; i < len; i++){
        if (isupper(str[i]))
            str[i] = tolower(str[i]);
        else if (islower(str[i]))
            str[i] = toupper(str[i]);
    }
}

void turn_round(char *str){
    char *tail = strstr(str, " ");
    char *start, *end;
    rev_letter(str, tail - str);
    start = str;
    for(int i = 0; i <= 9; i++){
        if(i == 9)
            end = strstr(start, " ");
        else
            end = strstr(start, "/");
        rev_str(start, end - start);
        start = end + 1;
    }
}

char const* gen(char *infen){
    char *out = (char *)malloc(1024*sizeof(char)); 
    char *selfmove, *selfprot, *emymove, *emyprot;
    PreGenInit();
    selfmove = genMove(infen);
    strcat(out, selfmove);
    selfprot = genProtMove(infen);
    strcat(out, selfprot);
    turn_round(infen);
    emymove = genMove(infen);
    strcat(out, emymove);
    emyprot = genProtMove(infen);
    strcat(out, emyprot);
    return out;
}

BOOST_PYTHON_MODULE(genmove){
    using namespace boost::python;
    def("gen", gen);
}
