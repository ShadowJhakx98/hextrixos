class DockCategory:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)