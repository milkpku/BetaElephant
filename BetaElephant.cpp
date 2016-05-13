#include "BetaElephant.h"
using namespace std;

#define weightU 1

int Node::findMaxA(){
	double max = 0;
	double temp;
	int maxi;
	for (int i = 0; i < K; i++){
		temp = Q[i] + weightU*P[i] / (1 + N[i]);
		if (temp > max){
			max = temp;
			maxi = i;
		}
	}
	return maxi;
}

int Node::findNew(){
	double max = 0;
	double temp;
	int maxi = 0;
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

Node* Node::genNode(int x){
	Node *newNode = new Node();
	newNode->pos = pos;
	newNode->pos.MakeMove(move[x]);
	newNode->fullyExpanded = false;
	genMove(&newNode->pos, newNode->K, newNode->move);
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

int Node::playRollout(){
	PositionStruct p = pos;
	int player = p.sdPlayer;
	int k = K;
	int mv[128];
	int i;
	for (i = 0; i < k; i++){
		mv[k] = move[k];
	}
	while (1){
		p.MakeMove(mv[ppi(pos2fen(&p), k, mv)]);
		genMove(&p, k, mv);
		if (k == 0){ //无子可走被将死
			if (p.sdPlayer == player){ //自己被将死
				return 0;
			}
			else{
				return 1;
			}
		}
	}
}
