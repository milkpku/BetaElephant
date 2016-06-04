#include <vector>
#include "eleeye/position.h"
using namespace std;

void psigma(const char *const szFen, const int N, const int *const moves, double *const ps);
//szFen是局面的Fen串，N是着法数量，move是着法的数组（长度为N的着法数组），以上是不可修改的输入
//p是长度为N的概率数组，请对应着法数组的顺序输出每个着法的psigma

int ppi(const char *const szFen, const int N, const int *const moves);
//输入类似，返回P最大的着法的下标

double value(const char *const szFen);
//对输入的Fen串，返回红方的局面评价v

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
