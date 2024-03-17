# Board Games with Reinforcement Learning
This is a repository for training an AI agent to play Tic-tac-toe and Checkers using reinforcement learning. Q-Learning, SARSA, Monte Carlo Off-Policy, and Monte Carlo On-Policy are implemented. A user may teach the agent themself by playing against it or apply an automated teacher agent. 

## Sources/Contributions

This project is based off/builds on similar projects by Sam Rasgusa and Reuben Feinman. 
Thank you to both of them, their repositories were essential in creating this project. 

Feinman's repository makes up a significant portion of the tictactoe section, providing 
much of the game.py and play.py code, a version of the total rewards graph, and the 
Q-Learning and SARSA agents. This project also served as the model for much of the
checkers portion of the project.

Rasgusa's repository provided much of the checkers environment that is used for each
agent as well as key tools for obtaining board state information. His alpha-beta AI 
also was the basis for the checkers teacher algorithm.

You can find both these projects here:

https://github.com/rfeinman/tictactoe-reinforcement-learning/tree/master
https://github.com/SamRagusa/Checkers-Reinforcement-Learning

## Code Structure

#### Source Code

This project contains four total RL agents to play tictactoe/checkers:
Q-Learning, SARSA, Monte Carlo Off-Policy, and Monte Carlo On-Policy.
These agents are trained by a teacher agent that knows the optimal or near-optimal
strategy; however, the teacher only follows this strategy with a given probability
p at each turn. The rest of the time this teacher chooses randomly from the moves 
that are available, so that the agents are able to win on occasion and learn from 
these wins. To initialize the learning agent Q values, I make use of default 
dictionaries with default values of 0 such that the value for every state-action pair 
is initialized to 0 for tictactoe, and initialize a state's state-action pairs when a
new state is encountered for checkers.

The agents are implemented in `agent.py`.
Each of the four learning agents inherit from a parent learner class; Each pair of on/off-policy 
algorithms (Q-Learning/SARSA and Monte Carlo On/Off-Policy) differ in their Q-value update function. 
The Monte Carlo agents differ from the other two because MC stores the entire trajectory/set of 
moves made over the course of the game and updates every move's state-action pair at the end of the
game, whereas Q/SARSA values are updated on a move-by-move basis.

The Teacher agent used by the training program in tictactoe is implemented in `dictteacher.py`, and the checkers teacher is implemented in `teacher.py`. 
The teacher knows the optimal (or nearly optimal) policy for each state presented; however, this agent only takes the optimal choice with a set probability. The tictactoe teacher knows the optimal policy through a pre-calculated dict of every possible board state the teacher could see, which was calculated by `tictactoeexpand.py` and `minimaxteacher.py`. Because the number of possible checkers games is exponentially larger than the total number of possible tictactoe games, the checkers teacher uses the minmax algorithm directly rather than calculating results ahead of time. It does use some optimizations to speed this process up: 
1. Alpha-beta pruning (see https://en.wikipedia.org/wiki/Alpha–beta_pruning)
2. Dynamic depth adjustment - the teacher's minmax depth limit will dynamically increase as training goes on, beginning at 1 and increasing to 5 for every 1/5 of total training episodes. (This does not apply to test cycles, where the teacher always uses depth=5)
3. Runtime move storage - while the teacher can't pre-calculate every move, each depth level stores the state-action pairs it calculates in a dictionary (saved to a pickle file) that it first checks before calculating a move, and uses the stored move if the board state is already in the dictionary.

In `game.py`, the main game class is found. 
The Game class holds the state of each particular game instance, and it contains the majority of the main game functionality. 
The main game loop can be found in the class's function playGame().

#### Game Script

To play the game (see "Running the Program" below for instructions) you will use the script called `play.py`.
The GameLearner class holds the state of the current game sequence, which will continue until the player choses to stop or the teacher has finished the designated number of episodes. Every 100 episodes during training, a "test cycle" occurs where the current agent is tested against an optimal agent and a random agent. The results of these are saved separately from the training and does not affect the training process. In tictactoe, a test cycle includes 100 games against a random opponent and 100 games against an optimal opponent, while checkers uses 100 games against a random opponent and 20 games against an optimal opponent to keep training time more reasonable.
See instructions below on how to use this script.

## Running the Training Program

#### Train a new agent manually
To initialize a new agent and begin a game loop, simply run:

    python play.py -a q                (Q-learner)
    python play.py -a s                (SARSA-learner)
    python play.py -a mcoff            (Monte Carlo Off-Policy-learner)
    python play.py -a mcon             (Monte Carlo On-Policy-learner)

This will initialize the game and allow you to train the agent manually by playing against the agent yourself. In the process of playing, you will be storing the new agent state with each game iteration. Use the argument `-p` to specify a path where the agent pickle should be saved:


    python play.py -a q -p my_agent_path.pkl


When unspecified, the path is set to either "q_agent.pkl", "sarsa_agent.pkl", "mcoff_agent.pkl", or "mcon_agent.pkl" depending on agent type. If the file already exists, you'll be asked to overwrite.

#### Train a new agent automatically via teacher
To initialize a new RL agent and train it automatically with a teacher agent, use the flag `-t` followed by the number of game iterations you would like to train for:

    python play.py -a q -t 5000

Again, specify the pickle save path with the `-p` option.

#### Load an existing agent and continue training
To load an existing agent and continue training, use the `-l` flag:

    python play.py -a q -l             (load agent and train manually)
    python play.py -a q -l -t 5000     (load agent and train via teacher)

The agent will continue to learn and its pickle file will be overwritten. 

For this use case, the argument `-a` is only used to define a default agent path (if not specified by `-p`); otherwise, the agent type is determined by the contents of the loaded pickle.


## Viewing Test Results
There are a number of test results/comparisons between agents that can be accessed through `plot_agent_reward.py`. 
#### Reward history of agent (Line chart)
To view a plot of an agent's cumulative reward history (line chart):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning"

You can also view multiple (up to 4) reward histories at once:

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -p2 sarsa_agent.pkl -n2 "SARSA" -p3 mcon_agent.pkl -n3 "MC On-Policy" -p4 mcoff_agent.pkl -n4 "MC Off-Policy"

#### Win/Loss/Draw vs Random Opponent
To view a plot of an agent's performance throughout training against a random opponent (line chart):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -t rand

To view the total results across 4 agents (currently only works with exactly 4 agents):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -p2 sarsa_agent.pkl -n2 "SARSA" -p3 mcon_agent.pkl -n3 "MC On-Policy" -p4 mcoff_agent.pkl -n4 "MC Off-Policy" -t -totalrand

#### Win/Loss/Draw vs Optimal Opponent
*NOTE: For tictactoe, only losses/draws are displayed because the agent cannot win vs the optimal opponent

To view a plot of an agent's performance throughout training against an optimal opponent (line chart):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -t opt

To view the total draws/losses across 4 agents (currently only works with exactly 4 agents):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -p2 sarsa_agent.pkl -n2 "SARSA" -p3 mcon_agent.pkl -n3 "MC On-Policy" -p4 mcoff_agent.pkl -n4 "MC Off-Policy" -t -totalopt

#### Results vs Random and Optimal Opponents
To get both above plots for a single agent simultaneously:

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -t all

#### Time to train 4 agents
To view the total time to train each agent (currently only works with exactly 4 agents):

    python plot_agent_reward.py -p q_agent.pkl -n "Q-Learning" -p2 sarsa_agent.pkl -n2 "SARSA" -p3 mcon_agent.pkl -n3 "MC On-Policy" -p4 mcoff_agent.pkl -n4 "MC Off-Policy" -t time
