import math
import random
import chess
from lc0_eval import get_lc0_evaluations


class MCTSNode:
    def __init__(self, board, depth, is_black = False, move = None, parent = None):
        self.board = board
        self.move = move
        self.depth = depth
        self.parent = parent
        self.children = []
        self.visits = 0
        self.win = 0
        self.is_black = is_black

    def ucb1(self):
        dd = dict()
        for child in self.children:
            if child.visits <= 0:
                dd[child.move] = 100
            elif self.visits <= 0:
                dd[child.move] = 100
            else:
                dd[child.move] = (child.win/child.visits) / math.sqrt(2) * math.sqrt(math.log(self.visits) / child.visits)

        return dd 

    def add_child(self, move):
        temp_board = self.board.copy()
        temp_board.push(move)
        new_child = MCTSNode(temp_board,  self.depth + 1, not self.is_black, move, self)
        self.children.append(new_child)
        return new_child    
    
    def find_child(self, board, move =None):
        for child in self.children:
            if child.board == board:
                return child
        return self.add_child(move)

    def has_child(self, board):
        for child in self.children:
            if child.board == board:
                return True
        return False
    
    def is_fully_expanded(self):
        legal_moves = list(self.board.legal_moves)
        for i in self.children:
            if i.move not in legal_moves:
                return False
        return True

def softmax_dict(input_dict):
    values = list(input_dict.values())
    max_value = max(values)
    exp_values = [math.exp(v - max_value) for v in values]
    sum_exp_values = sum(exp_values)
    softmax_values = [v / sum_exp_values for v in exp_values]
    
    return {key: softmax_values[i] for i, key in enumerate(input_dict.keys())}


class MCTS:
    def __init__(self, board: chess.Board, simulations, lc0_engine, max_depth = 50, ) -> None:
        self.root = MCTSNode(board, 0)
        self.current_node = self.root
        self.max_depth = max_depth
        self.simulations = simulations
        self.engine = lc0_engine

    def update_current_node(self, board: chess.Board, move = None):
        for child in self.current_node.children:
            if child.board == board:
                self.current_node = child
                return child
        self.current_node  = self.current_node.add_child(move)
        self.expand(self.current_node)
        return self.current_node

    def select(self):
        self.expand(self.current_node)
        lco_evaluations = softmax_dict(get_lc0_evaluations(self.engine, self.current_node.board))
        ucb1_evaluations = softmax_dict(self.current_node.ucb1())
        total_evaluations = dict()

        for move in lco_evaluations.keys():
            if self.current_node.depth < 5:
                total_evaluations[move] = lco_evaluations[move]
            else:
                total_evaluations[move] = 0.7 * lco_evaluations[move] + 0.3 * ucb1_evaluations[move]

        sorted_moves = sorted(total_evaluations.items(), key=lambda x: x[1], reverse=True)
        top_moves = sorted_moves[:2]
        moves = [move for move, score in top_moves]
        selected_move = random.choice(moves)
        return selected_move
    
    def simulate(self, node: MCTSNode):
        depth = 0
        temporary_board = node.board.copy()
        current_node = node
        while not temporary_board.is_game_over() and depth < self.max_depth: 
            depth += 1
            legal_moves = list(temporary_board.legal_moves)
            move = random.choice(legal_moves)
            temporary_board.push(move)
            current_node = current_node.find_child(temporary_board, move)
        result = temporary_board.result()
        
        if result == '1-0':
            return current_node, -1
        elif result == '0-1':
            return current_node, 1
        else:
            return current_node, 0 
        
    def backpropagation(self, node: MCTSNode, reward: int) -> None:
        while node != self.current_node:
            if node.is_black:
                node.win += reward
            else:
                node.win -= reward
            node.visits += 1
            node = node.parent

    def expand(self, node):
        for move in list(node.board.legal_moves):
            child_board = node.board.copy()
            child_board.push(move)
            if not node.has_child(child_board):
                node.add_child(move)

    def run(self):
        temporary_board = self.current_node.board.copy()
        move = self.select()
        temporary_board.push(move)
        node = self.current_node.find_child(temporary_board, move)
        for _ in range(self.simulations):
            if not temporary_board.is_game_over():
                node, reward = self.simulate(node)
            else:
                tem_board = self.current_node.board.copy()
                tem_board.push(move)
                self.update_current_node(tem_board, move)
                return move
            self.backpropagation(node, reward)

        tem_board = self.current_node.board.copy()
        tem_board.push(move)
        self.update_current_node(tem_board, move)
        return move