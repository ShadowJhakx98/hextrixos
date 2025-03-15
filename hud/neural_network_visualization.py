import cairo
import math
import random
import time

class NeuralNetworkVisualization:
    def __init__(self, width, height):
        """Initialize the neural network visualization"""
        self.width = width
        self.height = height
        self.nodes = []
        self.connections = []
        self.animation_offset = 0
        self.last_resize_time = 0
        self.resize_cooldown = 0.1  # 100ms cooldown between resizes
        self.last_width = width
        self.last_height = height
        # Add missing attributes with default values
        self.pulse_speed = 0.05  # Default animation speed
        self.node_movement_chance = 0.02  # 2% chance of node movement per update
        self.movement_range = min(width, height) * 0.005  # Default movement range
        self.generate_network(30, 50)  # Generate initial network
    
    def resize(self, width, height):
        """Resize the neural network visualization with cooldown"""
        # Avoid division by zero
        if width <= 0 or height <= 0:
            return
            
        current_time = time.time()
        if current_time - self.last_resize_time > self.resize_cooldown:
            # Only resize if the change is significant (more than 1%)
            width_change = abs(self.width - width) / max(1, self.width)
            height_change = abs(self.height - height) / max(1, self.height)
            
            if width_change > 0.01 or height_change > 0.01:
                self.last_resize_time = current_time
                scale_x = width / max(1, self.width)
                scale_y = height / max(1, self.height)
                
                # Update dimensions
                self.width = width
                self.height = height
                
                # Scale node positions
                for node in self.nodes:
                    node["x"] *= scale_x
                    node["y"] *= scale_y
                    
                # Update movement range based on new dimensions
                self.movement_range = min(width, height) * 0.005
    
    def generate_network(self, num_nodes, num_connections):
        self.nodes = []
        for i in range(num_nodes):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.1, 0.8) * min(self.width, self.height) * 0.4
            center_x = self.width / 2
            center_y = self.height / 2
            x = center_x + math.cos(angle) * distance * random.uniform(0.8, 1.2)
            y = center_y + math.sin(angle) * distance * random.uniform(0.8, 1.2)
            size = random.uniform(1.5, 4)
            brightness = random.uniform(0.7, 1.0)
            activity = random.uniform(0, 1)
            pulse_offset = random.uniform(0, 2 * math.pi)
            oscillation_speed = random.uniform(0.5, 1.5)
            self.nodes.append({
                "id": i,
                "x": x, 
                "y": y, 
                "size": size,
                "brightness": brightness,
                "activity": activity,
                "pulse_offset": pulse_offset,
                "oscillation_speed": oscillation_speed
            })
        
        self.connections = []
        for _ in range(num_connections):
            start = random.randint(0, num_nodes - 1)
            end = random.randint(0, num_nodes - 1)
            if start != end:
                strength = random.uniform(0.2, 1.0)
                self.connections.append({
                    "source": start, 
                    "target": end, 
                    "strength": strength,
                    "pulse_offset": random.uniform(0, 2 * math.pi),
                    "pulse_speed": random.uniform(0.5, 1.5)
                })
    
    def update(self):
        self.animation_offset += self.pulse_speed
        if self.animation_offset > 2 * math.pi:
            self.animation_offset -= 2 * math.pi
        
        for node in self.nodes:
            if random.random() < self.node_movement_chance:
                node["x"] += random.uniform(-self.movement_range, self.movement_range)
                node["y"] += random.uniform(-self.movement_range, self.movement_range)
                margin = min(self.width, self.height) * 0.05
                node["x"] = max(margin, min(self.width - margin, node["x"]))
                node["y"] = max(margin, min(self.height - margin, node["y"]))
            node["activity"] += random.uniform(-0.05, 0.05)
            node["activity"] = max(0.3, min(1.0, node["activity"]))
    
    def draw(self, cr, width, height):
        """Draw the neural network visualization with specified width and height
        
        This method is compatible with GTK 4.0's drawing API
        """
        # Update size if needed
        if width > 0 and height > 0 and (width != self.width or height != self.height):
            self.resize(width, height)
            
        # Draw the visualization
        self.draw_network(cr)
    
    def update_pulse_speed(self, speed):
        self.pulse_speed = speed
    
    def update_node_movement_chance(self, chance):
        self.node_movement_chance = chance
    
    def update_movement_range(self, range):
        self.movement_range = range
    
    def draw_network(self, cr):
        """Draw the neural network visualization
        
        Args:
            cr: Cairo context
        """
        # Clear background with gradient
        pat = cairo.LinearGradient(0, 0, 0, self.height)
        pat.add_color_stop_rgba(0, 0.0, 0.02, 0.05, 0.9)
        pat.add_color_stop_rgba(1, 0.0, 0.0, 0.02, 0.9)
        cr.set_source(pat)
        cr.paint()
        
        # Draw connections with reduced opacity
        for conn in self.connections:
            start_node = self.nodes[conn["source"]]
            end_node = self.nodes[conn["target"]]
            conn_phase = (conn["pulse_offset"] + self.animation_offset * conn["pulse_speed"]) % (2 * math.pi)
            pulse_factor = 0.3 + 0.2 * math.sin(conn_phase)  # Reduced pulse intensity
            
            # Calculate distance and check if connection should be drawn
            dist = math.sqrt((end_node["x"] - start_node["x"])**2 + (end_node["y"] - start_node["y"])**2)
            max_dist = min(self.width, self.height) * 0.3
            if dist > max_dist:
                continue
                
            # Calculate opacity based on distance
            alpha = (1.0 - dist/max_dist) * conn["strength"] * pulse_factor * 0.3  # Reduced opacity
            alpha = max(0.05, min(0.2, alpha))  # Cap maximum opacity
            
            # Draw connection line
            avg_activity = (start_node["activity"] + end_node["activity"]) / 2
            cr.set_source_rgba(0, 0.7 + 0.3 * avg_activity, 1.0, alpha)
            cr.set_line_width(0.5 * conn["strength"] * pulse_factor)
            cr.move_to(start_node["x"], start_node["y"])
            cr.line_to(end_node["x"], end_node["y"])
            cr.stroke()
        
        # Draw nodes with reduced glow
        for node in self.nodes:
            node_phase = (node["pulse_offset"] + self.animation_offset * node["oscillation_speed"]) % (2 * math.pi)
            pulse_intensity = 0.5 + 0.2 * math.sin(node_phase)  # Reduced pulse intensity
            
            # Draw node glow
            for i in range(3, 0, -1):  # Reduced glow layers
                alpha = 0.03 * i * node["activity"]  # Reduced glow opacity
                radius = node["size"] * (1 + 0.3 * i) * pulse_intensity  # Reduced glow size
                cr.set_source_rgba(0, 0.8, 1.0, alpha)
                cr.arc(node["x"], node["y"], radius, 0, 2 * math.pi)
                cr.fill()
            
            # Draw node core
            intensity = node["brightness"] * pulse_intensity * node["activity"] * 0.8  # Reduced core brightness
            cr.set_source_rgba(0.5 * intensity, 0.8 * intensity, 1.0, 0.6)
            cr.arc(node["x"], node["y"], node["size"] * pulse_intensity, 0, 2 * math.pi)
            cr.fill()