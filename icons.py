#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_icon(name, size, draw_func):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_func(draw, size)
    img.save(name)

def draw_vline(draw, size):
    color = (0, 255, 255, 255)  # Cyan
    center = size // 2
    draw.line([(center, 0), (center, size)], fill=color, width=2)

def draw_branch_more(draw, size):
    color = (0, 255, 255, 255)  # Cyan
    center = size // 2
    draw.line([(center, 0), (center, size)], fill=color, width=2)
    draw.line([(center, center), (size, center)], fill=color, width=2)

def draw_branch_end(draw, size):
    color = (0, 255, 255, 255)  # Cyan
    center = size // 2
    draw.line([(center, 0), (center, center)], fill=color, width=2)
    draw.line([(center, center), (size, center)], fill=color, width=2)

def draw_branch_closed(draw, size):
    color = (0, 255, 255, 255)  # Cyan
    padding = 4
    # Draw triangle pointing right
    points = [
        (padding, padding),
        (size - padding, size // 2),
        (padding, size - padding)
    ]
    draw.polygon(points, outline=color, fill=None, width=2)

def draw_branch_open(draw, size):
    color = (0, 255, 255, 255)  # Cyan
    padding = 4
    # Draw triangle pointing down
    points = [
        (padding, padding),
        (size - padding, padding),
        (size // 2, size - padding)
    ]
    draw.polygon(points, outline=color, fill=None, width=2)

def main():
    size = 16
    icons = {
        'vline.png': draw_vline,
        'branch-more.png': draw_branch_more,
        'branch-end.png': draw_branch_end,
        'branch-closed.png': draw_branch_closed,
        'branch-open.png': draw_branch_open
    }
    
    for name, draw_func in icons.items():
        create_icon(name, size, draw_func)
        print(f"Created {name}")

if __name__ == "__main__":
    main() 