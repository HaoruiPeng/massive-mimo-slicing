import heapq


class HuffmanTree:
    def __init__(self, node_probabilities):
        self.head = None
        self.node_queue = []
        self.pilot_sequences = [[]] * len(node_probabilities)

        # Push probabilities to priority queue
        for i in range(len(node_probabilities)):
            heapq.heappush(self.node_queue, self.__Node(i, node_probabilities[i]))

        # Create the Huffman tree
        while len(self.node_queue) > 1:
            # Extract nodes with lowest priority
            n1 = heapq.heappop(self.node_queue)
            n2 = heapq.heappop(self.node_queue)
            cn = self.__Node(0, 1 - (1 - n1.prob) * (1 - n2.prob))
            cn.right = n1
            cn.left = n2

            heapq.heappush(self.node_queue, cn)

        self.head = heapq.heappop(self.node_queue)

        # Generate pilot sequences
        self.__generate_pilot_sequences(self.head, None)
        self.__extract_pilot_sequences(self.head)

    def __generate_pilot_sequences(self, child, parent, left=True):
        if parent is None:
            child.seq = 0
        elif left:
            child.seq = parent.seq
        else:
            child.seq = parent.seq + 1

        # Tree should be balanced, so only need to check one child
        if child.left is not None:
            self.__generate_pilot_sequences(child.left, child, left=True)
            self.__generate_pilot_sequences(child.right, child, left=False)

    def __extract_pilot_sequences(self, current):
        if current.left is None:
            self.pilot_sequences[current.node].append(current.seq)
            return [current.node]
        else:
            left_node_list = self.__extract_pilot_sequences(current.left)
            right_node_list = self.__extract_pilot_sequences(current.right)
            combined_list = left_node_list + right_node_list

            for n in combined_list:
                self.pilot_sequences[n].append(current.seq)

            return combined_list

    class __Node:
        def __init__(self, i, prob):
            self.seq = 0
            self.node = i
            self.prob = prob
            self.right = None
            self.left = None

        def __lt__(self, other):
            return self.prob < other.prob
