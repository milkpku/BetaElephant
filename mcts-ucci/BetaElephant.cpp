#include "BetaElephant.h"
using namespace std;

#define weightU 30
#define thread 4

char* genMove(char* szFen){
	PositionStruct pos;
	pos.FromFen(szFen);
	int i, nTotal, nLegal;
	MoveStruct mvs[MAX_GEN_MOVES];
	nTotal = pos.GenAllMoves(mvs);
	char out[1024] = "";
	for (i = 0; i < nTotal; i++) {
		if (pos.MakeMove(mvs[i].wmv)) {
			pos.UndoMakeMove();
			//cout << nTotal<< " " << nLegal << " " << i << endl;
			char strmv[] = "A0-A0 ";
			strmv[0] = (mvs[i].wmv & 15) - 3 + 'A';
			strmv[1] = 12 - ((mvs[i].wmv & 255) >> 4) + '0';
			strmv[3] = ((mvs[i].wmv >> 8) & 15) - 3 + 'A';
			strmv[4] = 12 - (mvs[i].wmv >> 12) + '0';
			strcat(out, strmv);
		}
	}
	strcat(out, "\n");
	strcat(out, "");
	return out;
}

char* genProtMove(char* szFen){
	PositionStruct pos;
	pos.FromFen(szFen);
	int i, nTotal;
	int mvs[MAX_GEN_MOVES];
	nTotal = pos.GenProtMoves(mvs);
	char out[1024] = "";
	char strmv[] = "A0-A0 ";
	for (i = 0; i < nTotal; i++) {
		strmv[0] = (mvs[i] & 15) - 3 + 'A';
		strmv[1] = 12 - ((mvs[i] & 255) >> 4) + '0';
		strmv[3] = ((mvs[i] >> 8) & 15) - 3 + 'A';
		strmv[4] = 12 - (mvs[i] >> 12) + '0';
		strcat(out, strmv);
	}
	strcat(out, "\n");
	strcat(out, "");
	return out;
}

int genMove(PositionStruct *pos, int* mv){
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
	return nLegal;
}

char* pos2fen(PositionStruct *pos){
	char c[100];
	pos->ToFen(c);
	return c;
}

int Node::findMaxA(){
	double max = -DBL_MAX;
	double temp;
	int maxi = -1;
	int aa = 0;
	for (int i = 0; i < K; i++){
		aa += N[i];
	}
	for (int i = 0; i < K; i++){
		//(1 - 2 * pos.sdPlayer) returns 1 for red and -1 for black
		//temp = Q[i] + weightU*P[i] / (1 + N[i]);
		temp = Q[i] + 0.4 * sqrt(log(aa + 2) / (N[i] + 1));
		if (temp > max){
			max = temp;
			maxi = i;
		}
	}
	return maxi;
}

int Node::findNew(){
	double max = -DBL_MAX;
	int maxi = -1;
	for (int i = 0; i < K; i++){
		if (N[i] == 0){
			if (P[i] > max){
				max = P[i];
				maxi = i;
			}
		}
	}
	return maxi;
}

/*
Node* Node::genNode(int x){
Node *newNode = new Node();
newNode->pos = pos;
newNode->pos.MakeMove(move[x]);
newNode->fullyExpanded = false;
newNode->K = genMove(&newNode->pos, newNode->move);
int k = newNode->K;
newNode->P = new double[k];
psigma(pos2fen(&newNode->pos), k, newNode->move, newNode->P);
newNode->Q = new double[k];
newNode->N = new unsigned int[k];
newNode->C = new Node*[k];
for (int i = 0; i < k; i++){
newNode->Q[i] = 0;
newNode->N[i] = 0;
}
return newNode;
}
*/

Node* Node::genNode(int x){
	Node *newNode = new Node();
	newNode->pos = pos;
	newNode->pos.MakeMove(move[x]);
	newNode->fullyExpanded = false;
	newNode->K = genMove(&newNode->pos, newNode->move);
	psigma(pos2fen(&newNode->pos), newNode->K, newNode->move, newNode->P);
	for (int i = 0; i < newNode->K; i++){
		newNode->Q[i] = 0;
		newNode->N[i] = 0;
	}
	return newNode;
}

double Node::playRollout(){
	PositionStruct p[thread];
	int k[thread];
	int mv[thread][128];
	int result[thread];
	for (int t = 0; t < thread; t++){
		p[t] = pos;
		k[t] = K;
		for (int s = 0; s < K; s++){
			mv[t][s] = move[s];
		}
	}

#pragma omp parallel for
	for (int t = 0; t < thread; t++){
		while (1){
			//cout << mv[0] << " ";
			if (k[t] == 0){ //无子可走被将死
				if (p[t].sdPlayer == 0){ //红方被将死
					result[t] = 0;
					break;
				}
				else{
					result[t] = 1;
					break;
				}
			}
			p[t].MakeMove(mv[t][ppi(pos2fen(&p[t]), k[t], mv[t])]);
			k[t] = genMove(&p[t], mv[t]);
		}
	}

	int re = 0;
	for (int t = 0; t < thread; t++){
		re += result[t];
	}
	return ((double)re) / thread;
}

/*
int Node::playRollout(){
PositionStruct p = pos;
int k = K;
int mv[128];
int i;
for (i = 0; i < k; i++){
mv[i] = move[i];
}
while (1){
//cout << mv[0] << " ";
p.MakeMove(mv[ppi(pos2fen(&p), k, mv)]);
k = genMove(&p, mv);
if (k == 0){ //无子可走被将死
if (p.sdPlayer == 0){ //红方被将死
return 0;
}
else{
return 1;
}
}
}
}
*/

void psigma(const char *const szFen, const int N, const int *const moves, double *const ps){
	for (int i = 0; i < N; i++){
		//ps[i] = 1.0*i / ((N - 1)*N / 2);
		ps[i] = 1.0 / N;
	}
}

//szFen是局面的Fen串，N是着法数量，move是着法的数组（长度为N的着法数组），以上是不可修改的输入
//p是长度为N的概率数组，请对应着法数组的顺序输出每个着法的psigma

int ppi(const char *const szFen, const int N, const int *const moves){
	return (int)(N * rand() / (RAND_MAX + 1));
}
//输入类似，返回P最大的着法的下标

double value(const char *const szFen){
	return 1.0;
}
//对输入的Fen串，返回其局面评价v
