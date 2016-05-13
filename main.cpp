#include "BetaElephant.h"
using namespace std;

#define lemda 0.5

int main(){
	PositionStruct p;
	//loadPos();
	Node *root = new Node();
	root->pos = p;
	root->fullyExpanded = false;
	genMove(&p, root->K, root->move);
	int k = root->K;
	root->P = new double[k];
	psigma(pos2fen(&p), k, root->move, root->P);
	root->Q = new double[k];
	root->N = new unsigned int[k];
	root->C = new Node*[k];
	for (int i = 0; i < k; i++){
		root->Q[i] = 0;
		root->N[i] = 0;
	}
	
	vector<int> pathi;
	vector<Node*> pathn;
	Node* present;
	int pi, x;
	double v;
	while (1){ //继续循环条件
		present = root;
		pathi.clear();
		pathn.clear();
		pathn.push_back(root);
		while (present->fullyExpanded){
			pi = present->findMaxA();
			pathi.push_back(pi);
			present = present->C[pi];
			pathn.push_back(present);
		}
		x = present->findNew();
		pathi.push_back(x);
		present->C[x] = present->genNode(x);
		v = (1 - lemda)*value(pos2fen(&present->C[x]->pos)) + lemda*present->C[x]->playRollout();
		for (int i = 0; i < pathi.size(); i++){
			pathn[i]->Q[pathi[i]] = (pathn[i]->N[pathi[i]] * pathn[i]->Q[pathi[i]] + v) / (pathn[i]->N[pathi[i]] + 1);
			pathn[i]->N[pathi[i]]++;
		}
	}
	int maxm;
	double max = 0;
	for (int i = 0; i < root->K; i++){
		if (root->Q[i] > max){
			max = root->Q[i];
			maxm = i;
		}
	}
	//output(root->move[i]);
}
