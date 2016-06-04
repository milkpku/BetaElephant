#include "BetaElephant.h"
#include <stdio.h>
#include <time.h>
#include "eleeye/search.h"
using namespace std;

#define lemda 0.5

void ClearMemory(Node* n){
	for (int i = 0; i < n->K; i++){
		if (n->C[i] != NULL){
			ClearMemory(n->C[i]);
		}
	}
	delete n;
}

void MonteCarlo(int maxNode){
	Node *root = new Node();
	root->pos = Search.pos;
	root->fullyExpanded = false;
	root->K = genMove(&root->pos, root->move);
	if (root->K == 0){
		printf("nobestmove\n");
		fflush(stdout);
	}
	psigma(pos2fen(&root->pos), root->K, root->move, root->P);
	for (int i = 0; i < root->K; i++){
		root->Q[i] = 0;
		root->N[i] = 0;
	}

	vector<int> pathi;
	vector<Node*> pathn;
	Node* present;
	int pi, x;
	double v;
	for (int ii = 0; ii < 1000; ii++){ //继续循环条件
		//cout << ii << " ";
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
		if (x >= 0){
			pathi.push_back(x);
			present->C[x] = present->genNode(x);
			//v = (1 - lemda)*value(pos2fen(&present->C[x]->pos)) + lemda*present->C[x]->playRollout();
			v = present->C[x]->playRollout();
			if (present->pos.sdPlayer == 1){
				v = 1-v;
			}
			for (int i = pathi.size() - 1; i >= 0; i--){
				pathn[i]->Q[pathi[i]] = (pathn[i]->N[pathi[i]] * pathn[i]->Q[pathi[i]] + v) / (pathn[i]->N[pathi[i]] + 1);
				pathn[i]->N[pathi[i]]++;
				v = 1-v;
				//cout << pathi[i] << " ";
			}
			//cout << endl;
			present->fullyExpanded = true;
			for (int i = 0; i < present->K; i++){
				if (present->N[i] == 0){
					present->fullyExpanded = false;
				}
			}
		}
		else{ //present是终局节点
			v = 1;
			for (int i = pathi.size() - 1; i >= 0; i--){
				pathn[i]->N[pathi[i]]++;
				pathn[i]->Q[pathi[i]] = (pathn[i]->N[pathi[i]] * pathn[i]->Q[pathi[i]] + v) / (pathn[i]->N[pathi[i]] + 1);
				v = 1 - v;
				//cout << pathi[i] << " ";
			}
			//cout << endl;
		}
	}
	int maxm;
	int max = 0;
	for (int i = 0; i < root->K; i++){
		if (root->N[i] > max){
			max = root->N[i];
			maxm = i;
		}
	}

	//output(root->move[maxm]);

	uint32_t out = MOVE_COORD(root->move[maxm]);
	printf("move %.4s\n", (const char *)&out);
	fflush(stdout);
	Search.pos.MakeMove(root->move[maxm]);
	//clearmemory
	ClearMemory(root);

}
