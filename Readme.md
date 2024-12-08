
# ChessAI: Monte Carlo vs Alpha-Beta  
  
This project sets up a chess match between two AI-driven decision-making models:  
- **Alpha-Beta Pruning Search** (White)  
- **Monte Carlo Tree Search (MCTS)** (Black, leveraging the [Lc0]([https://lczero.org/](https://lczero.org/)) engine)  
  
The code runs a series of games and saves the resulting PGN files for analysis. It uses the Python `chess` library and integrates with the [Lc0 Chess Engine]([https://lczero.org/](https://lczero.org/)).  
  
## How It Works  
  
- **Alpha-Beta Player (White):**  
Uses a traditional search algorithm enhanced with alpha-beta pruning and custom heuristic evaluations.  
  
- **Monte Carlo Player (Black):**  
Employs a Monte Carlo Tree Search (MCTS) approach, guided by Lc0 engine evaluations.  
  
Each game alternates moves between White (Alpha-Beta) and Black (MCTS). A specified number of games are automatically run and saved in `.pgn` format, allowing you to study the games.  
  
## Alpha-Beta Heuristics  
  
The Alpha-Beta Pruning algorithm in this project utilizes a set of heuristic evaluation functions to assess the strength of board positions. These heuristics are designed to evaluate various aspects of the game, such as material balance, piece activity, king safety, and more. Below is an overview of each heuristic function used:  
  
### `evaluate_board(board: chess.Board) -> int`  
  
Evaluates the overall board state by determining the phase of the game (opening, middlegame, or endgame) and applying relevant evaluations accordingly. It also incorporates castling and king safety assessments.  
  
### `evaluate_opening(board: chess.Board) -> int`  
  
Specifically evaluates the board during the opening phase. This function considers:  
- **Material Balance:** Total value of pieces for both sides.  
- **Central Control:** Influence over central squares.  
- **Piece Development:** Advancement of knights and bishops.  
- **Early Queen Move Penalty:** Discourages premature queen development.  
  
### `evaluate_middlegame(board: chess.Board) -> int`  
  
Assesses the board during the middlegame by analyzing:  
- **Material Balance:** Similar to the opening.  
- **Central Control:** Continued emphasis on central dominance.  
- **Piece Activity:** Mobility and potential threats from pieces.  
- **King Safety:** Protection of the king from threats.  
  
### `evaluate_endgame(board: chess.Board) -> int`  
  
Focuses on the endgame by evaluating:  
- **Material Balance:** Remaining pieces and their positions.  
- **King Activity:** Active participation of the king in the game.  
- **Pawn Advancement:** Progress of pawns towards promotion.  
  
### `evaluate_material(board: chess.Board) -> int | float`  
  
Calculates the material balance by assigning values to each piece type:  
- **Pawn:** 1  
- **Knight:** 3  
- **Bishop:** 3  
- **Rook:** 5  
- **Queen:** 9  
- **King:** 0 (infinite value if checkmated)  
  
It also handles special cases like checkmate and stalemate.  
  
### `evaluate_central_control(board: chess.Board, color: chess.Color) -> int`  
  
Evaluates control over central squares (`d4`, `e4`, `d5`, `e5`) by:  
- Counting pieces occupying these squares.  
- Assessing attacks on these squares by the specified color.  
  
### `evaluate_piece_development(board: chess.Board, color: chess.Color) -> int`  
  
Assesses the development of knights and bishops by checking their advancement from starting positions:  
- Knights on higher ranks are considered more developed.  
- Bishops on more active squares contribute positively.  
  
### `evaluate_activity(board: chess.Board, color: chess.Color) -> int`  
  
Measures the activity of pieces by counting the number of squares they attack:  
- Active pieces with more mobility score higher.  
  
### `evaluate_castling(board: chess.Board) -> float`  
  
Encourages castling by providing a bonus for available castling rights:  
- Adds points if kingside or queenside castling is still possible for both White and Black.  
  
### `evaluate_king_safety(board: chess.Board, color: chess.Color) -> float`  
  
Assesses the safety of the king **only after castling** by:  
- Checking the presence of friendly pawns around the king.  
- Penalizing positions where the king is inadequately protected. > Albert: ### `evaluate_king_activity(board: chess.Board, color: chess.Color) -> int | float`  
  
Evaluates the king's activity, especially useful in endgames:  
- Counts the number of squares the king attacks, promoting active king participation.  
  
### `evaluate_pawn_advancement(board: chess.Board, color: chess.Color) -> int | float`  
  
Measures the progress of pawns towards promotion:  
- Assigns higher scores to pawns that are further advanced on the board.  
  
### `evaluate_positional_heuristics(board: chess.Board, color: chess.Color) -> int | float`  
  
Analyzes pawn structure and other positional factors:  
- Penalizes isolated and backward pawns, which can be weaknesses.  
  
### `has_castled(board: chess.Board, color: chess.Color) -> bool`  
  
Checks if a player has castled by verifying the king's position:  
- Returns `True` if the king is on a castled square (`G1`, `C1`, `G8`, ``C8`), else `False``.  
  
## Monte Carlo Tree Search (MCTS)  
  
The Monte Carlo Tree Search (MCTS) player utilizes a probabilistic approach to explore possible moves and determine the most promising ones. This section outlines how MCTS operates within this project, including its integration with the Lc0 engine and the four main phases of the algorithm.  
  
### How MCTS Works  
  
MCTS is a heuristic search algorithm used for decision-making processes, particularly in game playing. It builds a search tree incrementally and uses random simulations to evaluate the potential of moves. The MCTS implementation in this project incorporates the Lc0 engine to enhance its move selection process.  
  
### Incorporating Lc0 in MCTS  
  
The integration of the Lc0 engine enhances the MCTS by providing informed evaluations of board positions. Specifically, Lc0 is used during the **selection** phase to guide the exploration of the search tree. The selection process balances two key components:  
  
- **Lc0 Evaluations:** Provide a neural-network-based assessment of board positions, offering insights into strategic advantages.  
- **UCB1 (Upper Confidence Bound):** Balances exploration and exploitation by considering both the average reward and the uncertainty in the estimates.  
  
#### Weighting Lc0 and UCB1  
  
In this project, the selection of moves within MCTS is influenced by both Lc0 evaluations and UCB1 scores. The weights assigned to each component determine their relative importance during move selection:  
  
- **Depth < 5:** Heavily relies on Lc0 evaluations to guide initial move choices.  
- **Depth ≥ 5:** Combines Lc0 evaluations and UCB1 scores equally to balance informed exploration and strategic uncertainty.  
  
### The Four Phases of MCTS  
  
MCTS operates through four main phases in each iteration of the search:  
  
1. **Selection:**  
- **Objective:** Traverse the tree from the root to a leaf node using a policy that balances exploration and exploitation.  
- **Process:** At each node, select the child with the highest UCB1 score or based on weighted Lc0 evaluations.  
- **Integration with Lc0:** During selection, moves are prioritized using a combination of Lc0 scores and UCB1 values, with 0.6 weight for Lc0 evaluation and 0.4 for UCB1 evaluation 
  
2. **Expansion:**  
- **Objective:** Expand the tree by adding one or more child nodes representing possible moves from the selected leaf node.  
- **Process:** If the selected node is not fully expanded (i.e., not all possible moves have been explored), add a new child node for an untried move.  
  
3. **Simulation (Playout):**  
- **Objective:** Simulate a random playthrough from the newly expanded node to a terminal state (win, loss, or draw).  
- **Process:** Perform random moves until the game concludes, optionally incorporating Lc0 evaluations to bias the randomness towards more promising moves.  
  
4. **Backpropagation:**  
- **Objective:** Update the statistics (e.g., visit counts and win rates) of nodes along the path from the leaf node back to the root based on the simulation result.  
- **Process:** Propagate the outcome of the simulation upwards, adjusting the win and visit counts to reflect the new information.  
  
### Example Workflow  
  
1. **Initialization:**  
- Start with the root node representing the current board state.  
- Initialize the MCTS with a specified number of simulations and maximum search depth.  
  
2. **Running Simulations:**  
- For each simulation, perform the four phases: selection, expansion, simulation, and backpropagation.  
- Use Lc0 evaluations to inform move selections and bias simulations.  
  
3. **Selecting the Best Move:**  
- After completing all simulations, select the move with the highest visit count or best win rate as the optimal move.  
  
4. **Executing the Move:**  
- Apply the selected move to the board and proceed to the next turn.  
  
## Lc0 Integration  
  
This project integrates the Lc0 engine to evaluate chess positions for the MCTS player. Lc0 (Leela Chess Zero) is a neural-network-based engine that provides strong evaluations:  
  
- [**Official Lc0 Website:**](https://lczero.org/)  
  
To run the project, ensure that you have a functioning Lc0 engine and a weights file on your local machine.  
  
## Project Structure  
  
ChessAI/  
│  
├─ src/
│   ├─ main.py
│   ├─ monte_carlo.py
│   ├─ algorithms.py
│   ├─ state_eval.py
│   └─ lc0_eval.py  
├─ .env_template
├─ README.md
├─ requirements.txt  
└─ .gitignore
    
## Example `.env` File  
  
Create a `.env` file in the root directory:  
  
```env  
ENGINE_PATH=/path/to/lc0/executable  
WEIGHTS_PATH=/path/to/weights/file  
SAVE_DIR=/path/to/save/pgn/files  
  ```
## Setup and Dependencies  
  
Prerequisites  
• Python 3.8+  
• [python-chess](https://pypi.org/project/python-chess/) library:  
  
  ```
pip install -r requirements.txt 
  ```
  
• [Lc0 Engine](https://github.com/LeelaChessZero/lc0/releases) and a compatible weights file (for the MCTS player).  
  

### Running the Project  
1. Set Up Environment Variables:  
Ensure `.env ` is correctly filled out with the paths to your Lc0 executable, weights file, and desired save directory.  
2. Run the Script:  
  
python main.py
  
  
  
This will run a game, produce output to the terminal, and save the resulting `.pgn` game in the specified save directory.  
  
