import matplotlib.pyplot as plt
import networkx as nx

class Visualization:
    @staticmethod
    def visualize_graph(graph):
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='lightblue')
        plt.show()
