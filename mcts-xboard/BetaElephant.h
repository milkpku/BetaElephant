#include <vector>
#include "eleeye/position.h"
using namespace std;

void psigma(PositionStruct pos, double *const ps);

int ppi(const char *const szFen, const int N, const int *const moves);

double value(const char *const szFen);

int genMove(PositionStruct *pos, int* mv);

char* pos2fen(PositionStruct *pos);

char* genMove(char* szFen);

char* genProtMove(char* szFen);

class Node{
public:
	int K; //legal move count
	bool fullyExpanded;
	PositionStruct pos;
	int move[MAX_GEN_MOVES];
	double P[MAX_GEN_MOVES]; //prior probability
	double Q[MAX_GEN_MOVES]; //action value
	unsigned int N[MAX_GEN_MOVES]; //visit count
	Node* C[MAX_GEN_MOVES]; //children

	int findMaxA(); //找到完全扩展Node的最优孩子
	int findNew(); //找到未完全扩展Node的下一个扩展的孩子
	Node* genNode(int x); //生成扩展的Node并初始化
	double playRollout(); //用ppi模拟到最后返回红方是否获胜，返回0为负，1为胜
};