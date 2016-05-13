#include <vector>
#include "eleeye/position.h"
using namespace std;

void psigma(const char *const szFen, const int N, const int *const moves, double *const ps);
//szFen是局面的Fen串，N是着法数量，move是着法的数组（长度为N的着法数组），以上是不可修改的输入
//p是长度为N的概率数组，请对应着法数组的顺序输出每个着法的psigma

int ppi(const char *const szFen, const int N, const int *const moves);
//输入类似，返回P最大的着法的下标

double value(const char *const szFen);
//对输入的Fen串，返回其局面评价v

void genMove(PositionStruct *pos, int K, int* mv){
	int i, nTotal, nLegal;
	MoveStruct mvs[MAX_GEN_MOVES];
	nTotal = pos->GenAllMoves(mvs);
	nLegal = 0;
	for (i = 0; i < nTotal; i++) {
		if (pos->MakeMove(mvs[i].wmv)) {
			pos->UndoMakeMove();
			mv[nLegal] = mvs[i].wmv;
			nLegal++;
		}
	}
	K = nLegal;
}

char* pos2fen(PositionStruct *pos){
	char* c;
	pos->ToFen(c);
	return c;
}

class Node{
public:
	int K; //legal move count
	bool fullyExpanded;
	PositionStruct pos;
	int* move;
	double* P; //prior probability
	double* Q; //action value
	unsigned int* N; //visit count
	Node** C; //children

	int findMaxA(); //找到完全扩展Node的最优孩子
	int findNew(); //找到未完全扩展Node的下一个扩展的孩子
	Node* genNode(int x); //生成扩展的Node并初始化
	int playRollout(); //用ppi模拟到最后返回胜负，返回0为负，1为胜
};
