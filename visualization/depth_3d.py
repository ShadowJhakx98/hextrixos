import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class DepthVisualizer:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
    def visualize(self, depth_map):
        h, w = depth_map.shape
        x = np.linspace(0, w, w)
        y = np.linspace(0, h, h)
        x, y = np.meshgrid(x, y)
        
        self.ax.clear()
        self.ax.plot_surface(x, y, depth_map, cmap='viridis')
        self.ax.set_zlim(np.min(depth_map), np.max(depth_map))
        plt.draw()
        plt.pause(0.001)
