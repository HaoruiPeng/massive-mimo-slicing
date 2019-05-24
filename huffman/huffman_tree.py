import heapq


class HuffmanTree:
    def __init__(self, node_probabilities):
        self.pilot_sequences = [[]] * len(node_probabilities)

        node_queue = []
        head = None

        # Push probabilities to priority queue
        for i in range(len(node_probabilities)):
            heapq.heappush(node_queue, self.__Node(i, node_probabilities[i]))

        # Create the Huffman tree
        while len(node_queue) > 1:
            # Extract nodes with lowest priority
            n1 = heapq.heappop(node_queue)
            n2 = heapq.heappop(node_queue)
            cn = self.__Node(0, 1 - (1 - n1.prob) * (1 - n2.prob))
            cn.left = n2
            cn.right = n1

            heapq.heappush(node_queue, cn)

        head = heapq.heappop(node_queue)

        # Generate pilot sequences
        self.__generate_pilot_sequences(head, None)
        self.__extract_pilot_sequences(head)

        # Reverse the sequences
        for seq in self.pilot_sequences:
            seq.reverse()

    def __generate_pilot_sequences(self, child, parent, left=True):
        if parent is None:
            child.seq = 0
        elif left:
            child.seq = 2 * parent.seq
        else:
            child.seq = 2 * parent.seq + 1

        # Tree should be balanced, so only need to check one child
        if child.left is not None:
            self.__generate_pilot_sequences(child.left, child, left=True)
            self.__generate_pilot_sequences(child.right, child, left=False)

    def __extract_pilot_sequences(self, current):
        if current.left is None:
            self.pilot_sequences[current.node] = [current.seq]
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
