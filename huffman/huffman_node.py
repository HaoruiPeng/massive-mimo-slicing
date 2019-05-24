class HuffmanNode:
    def __init__(self, node_id, prob, seq):
        self.node_id = node_id
        self.prob = prob
        self.seq = seq
        self.consumed = False
