import time

class AuraSyncController:
    def __init__(self):
        """Initialize the AuraSync lighting controller."""
        self.current_color = 0x000000

    def set_color(self, color_hex):
        """
        Set the lighting color.
        Args:
            color_hex (int): Hexadecimal color value (e.g., 0xFF0000 for red).
        """
        self.current_color = color_hex
        # Simulate setting the color; replace with actual hardware control code.
        print(f"AuraSync: Set color to #{color_hex:06X}")

    def rainbow_cycle(self, duration=10, interval=0.1):
        """
        Create a rainbow lighting effect.
        Args:
            duration (float): Total time for the rainbow cycle effect in seconds.
            interval (float): Time between color transitions in seconds.
        """
        print("AuraSync: Starting rainbow cycle...")
        colors = [0xFF0000, 0xFF7F00, 0xFFFF00, 0x00FF00, 0x0000FF, 0x4B0082, 0x8B00FF]
        start_time = time.time()

        while time.time() - start_time < duration:
            for color in colors:
                self.set_color(color)
                time.sleep(interval)

        print("AuraSync: Rainbow cycle complete.")

    def turn_off(self):
        """Turn off all lights."""
        self.set_color(0x000000)
        print("AuraSync: Lights turned off.")
