#include "BetaElephant.h"
using namespace std;

#define weightU 100
#define thread 1

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
		temp = Q[i] + weightU*P[i] / (1 + N[i]);
		//temp = Q[i] + 0.4 * sqrt(log(aa + 2) / (N[i] + 1));
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

Node* Node::genNode(int x){
	Node *newNode = new Node();
	newNode->pos = pos;
	newNode->pos.MakeMove(move[x]);
	newNode->fullyExpanded = false;
	newNode->K = genMove(&newNode->pos, newNode->move);
	psigma(newNode->pos, newNode->P);
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

Session* session;

void psigma(PositionStruct pos, double *const ps){
	//printf("phase5\n");
	Tensor self_pos(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));
	Tensor emy_pos(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));
	Tensor self_move(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));
	Tensor emy_move(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));
	Tensor self_prot(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));
	Tensor emy_prot(DT_FLOAT, TensorShape({ 1, 9, 10, 16 }));

	//printf("phase6\n");
	auto self_pos_tensor = self_pos.tensor<float, 4>();
	auto emy_pos_tensor = emy_pos.tensor<float, 4>();
	auto self_move_tensor = self_move.tensor<float, 4>();
	auto emy_move_tensor = emy_move.tensor<float, 4>();
	auto self_prot_tensor = self_prot.tensor<float, 4>();
	auto emy_prot_tensor = emy_prot.tensor<float, 4>();

	//printf("phase7\n");

	for (int i = 0; i < 9; i++){
		for (int j = 0; j < 10; j++){
			for (int k = 0; k < 16; k++){
				self_pos_tensor(0, i, j, k) = 0;
				emy_pos_tensor(0, i, j, k) = 0;
				self_move_tensor(0, i, j, k) = 0;
				emy_move_tensor(0, i, j, k) = 0;
				self_prot_tensor(0, i, j, k) = 0;
				emy_prot_tensor(0, i, j, k) = 0;
			}
		}
	}
	//printf("phase8\n");
	//set pos
	if (pos.sdPlayer == 0){
		for (int k = 0; k < 16; k++){
			int temp = pos.ucsqPieces[k + 16];
			if (temp != 0) self_pos_tensor(0, (temp & 15) - 3, 12 - (temp >> 4), k) = 1;
			//printf("%d,%d,%d\n",(temp & 15) - 3, 12 - (temp >> 4), k);
			temp = pos.ucsqPieces[k + 32];
			if (temp != 0) emy_pos_tensor(0, (temp & 15) - 3, 12 - (temp >> 4), k) = 1;
			//printf("%d,%d,%d\n",(temp & 15) - 3, 12 - (temp >> 4), k);
		}
	}
	else{
		for (int k = 0; k < 16; k++){
			int temp = pos.ucsqPieces[k + 32];
			if (temp != 0) self_pos_tensor(0, (temp & 15) - 3, 12 - (temp >> 4), k) = 1;
			//printf("%d,%d,%d\n",(temp & 15) - 3, 12 - (temp >> 4), k);
			temp = pos.ucsqPieces[k + 16];
			if (temp != 0) emy_pos_tensor(0, (temp & 15) - 3, 12 - (temp >> 4), k) = 1;
			//printf("%d,%d,%d\n",(temp & 15) - 3, 12 - (temp >> 4), k);
		}
	}
	//printf("phase9\n");
	int a[MAX_GEN_MOVES];
	int b[MAX_GEN_MOVES];
	int kk[MAX_GEN_MOVES];
	int nLegal;

	if (pos.sdPlayer == 0){
		int i, nTotal;
		MoveStruct mvs[MAX_GEN_MOVES];
		nTotal = pos.GenAllMoves(mvs);
		nLegal = 0;
		for (i = 0; i < nTotal; i++) {
			if (pos.MakeMove(mvs[i].wmv)) {
				pos.UndoMakeMove();
				kk[nLegal] = pos.ucpcSquares[mvs[i].wmv & 255] - 16;
				a[nLegal] = ((mvs[i].wmv >> 8) & 15) - 3;
				b[nLegal] = 12 - (mvs[i].wmv >> 12);
				self_move_tensor(0, a[nLegal], b[nLegal], kk[nLegal]) = 1;
				//printf("%d,%d,%d\n",a[nLegal], b[nLegal], kk[nLegal]);
				nLegal++;
			}
		}
	}
	else{
		int i, nTotal;
		MoveStruct mvs[MAX_GEN_MOVES];
		nTotal = pos.GenAllMoves(mvs);
		nLegal = 0;
		for (i = 0; i < nTotal; i++) {
			if (pos.MakeMove(mvs[i].wmv)) {
				pos.UndoMakeMove();
				kk[nLegal] = pos.ucpcSquares[mvs[i].wmv & 255] - 32;
				a[nLegal] = ((mvs[i].wmv >> 8) & 15) - 3;
				b[nLegal] = 12 - (mvs[i].wmv >> 12);
				self_move_tensor(0, a[nLegal], b[nLegal], kk[nLegal]) = 1;
				//printf("%d,%d,%d\n",a[nLegal], b[nLegal], kk[nLegal]);
				nLegal++;
			}
		}
	}

	pos.ChangeSide();
	if (pos.sdPlayer == 0){
		int i, nTotal, k;
		MoveStruct mvs[MAX_GEN_MOVES];
		nTotal = pos.GenAllMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			if (pos.MakeMove(mvs[i].wmv)) {
				pos.UndoMakeMove();
				k = pos.ucpcSquares[mvs[i].wmv & 255] - 16;
				emy_move_tensor(0, ((mvs[i].wmv >> 8) & 15) - 3, 12 - (mvs[i].wmv >> 12), k) = 1;
				//printf("%d,%d,%d\n",a[nLegal], b[nLegal], kk[nLegal]);
			}
		}
	}
	else{
		int i, nTotal, k;
		MoveStruct mvs[MAX_GEN_MOVES];
		nTotal = pos.GenAllMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			if (pos.MakeMove(mvs[i].wmv)) {
				pos.UndoMakeMove();
				k = pos.ucpcSquares[mvs[i].wmv & 255] - 32;
				emy_move_tensor(0, ((mvs[i].wmv >> 8) & 15) - 3, 12 - (mvs[i].wmv >> 12), k) = 1;
				//printf("%d,%d,%d\n",a[nLegal], b[nLegal], kk[nLegal]);
			}
		}
	}
	pos.ChangeSide();

	//printf("phase10\n");
	if (pos.sdPlayer == 0){
		int i, nTotal, k;
		int mvs[MAX_GEN_MOVES];
		nTotal = pos.GenProtMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			k = pos.ucpcSquares[mvs[i] & 255] - 16;
			self_prot_tensor(0, ((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k) = 1;
			//printf("%d,%d,%d\n",((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k);
		}
	}
	else{
		int i, nTotal, k;
		int mvs[MAX_GEN_MOVES];
		nTotal = pos.GenProtMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			k = pos.ucpcSquares[mvs[i] & 255] - 32;
			self_prot_tensor(0, ((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k) = 1;
			//printf("%d,%d,%d\n",((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k);
		}
	}

	pos.ChangeSide();
	if (pos.sdPlayer == 0){
		int i, nTotal, k;
		int mvs[MAX_GEN_MOVES];
		nTotal = pos.GenProtMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			k = pos.ucpcSquares[mvs[i] & 255] - 16;
			emy_prot_tensor(0, ((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k) = 1;
			//printf("%d,%d,%d\n",((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k);
		}
	}
	else{
		int i, nTotal, k;
		int mvs[MAX_GEN_MOVES];
		nTotal = pos.GenProtMoves(mvs);
		for (i = 0; i < nTotal; i++) {
			k = pos.ucpcSquares[mvs[i] & 255] - 32;
			emy_prot_tensor(0, ((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k) = 1;
			//printf("%d,%d,%d\n",((mvs[i] >> 8) & 15) - 3, 12 - (mvs[i] >> 12), k);
		}
	}
	pos.ChangeSide();


	//printf("phase11\n");
	std::vector<std::pair<string, tensorflow::Tensor>> inputs = {
			{ "policy/self_pos", self_pos },
			{ "policy/enemy_pos", emy_pos },
			{ "policy/self_ability", self_move },
			{ "policy/enemy_ability", emy_move },
			{ "policy/self_protect", self_prot },
			{ "policy/enemy_protect", emy_prot },
	};
	//printf("phase12\n");
	std::vector<tensorflow::Tensor> outputs;
	//printf("phase13\n");
	Status status = session->Run(inputs, { "policy/predict" }, {}, &outputs);
	//printf("phase14\n");
	if (!status.ok()) {
		std::cout << status.ToString() << "\n";
		return;
	}
	//printf("phase15\n");
	auto output_c = outputs[0].tensor<float, 4>();
	double ddd = 0;
	for (int i = 0; i < nLegal; i++){
		//ps[i] = 1.0*i / ((N - 1)*N / 2);
		ps[i] = output_c(0, a[i], b[i], kk[i]);
		ddd += ps[i];
		//printf("%d,%d,%d,%f\n",a[i], b[i], kk[i],ps[i]);
	}
}


int ppi(const char *const szFen, const int N, const int *const moves){
	return (int)(N * rand() / (RAND_MAX + 1));
}

double value(const char *const szFen){
	return 1.0;
}