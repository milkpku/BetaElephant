# BetaElephant
Chinese Chess Xboard engine using MCTS and DNN

## Introduction
AlphaGo has achieved a high winning rate against other Go programs and
defeated the top human player Lee Sedol from South Korean. This inspired
us to design BetaElephant, a Chinese Chess AI, (to confirm whether the
framework of AlphaGo can be properly applied to other domains.

BetaElephant is mainly a combination of Monte Carlo Tree Search and
several Deep Neutral Networks. MCTS finds the move with the highest
winning rate by expanding the search tree, while Policy and Value DNN
provide MCTS with prior probabilities of each move and the valuation of
board position. In each circulation of MCTS, it determines a path by prior
probabilities and previous searching results, adds a new leaf node, and
updates the path by the board valuation and a playing-through result. The
DNNs are trained by a novel combination of supervised learning and
reinforcement learning, taking data from human expert games and self-play
results.

## Compile & Run

- <b>mcts-xboard/</b> contains the c++ code of the main program. 	To compile BetaElephant, run <code>./compile </code> 

- <b>util/</b> contains some most used functions such as dataset and tensorflow models

- <b>policy_experiments/</b> records all the trial we conducted to find optimal policy network

- <b>train_policy/</b> is the optimized policy network, run 
<code>python3 model.py && tensorboard --logdir . </code> 
to open tensorboard http server, and you can see the architecture of our policy network

- <b>rl_train/</b> contains the unfinished reinforcement learning framework.

- <b>export_nets/</b> provide tools to export trained models, which will be loaded in main program by tensorflow c++ api

- <b>chess_rule/</b> contains the python package which take FEN as input and return legal moves


