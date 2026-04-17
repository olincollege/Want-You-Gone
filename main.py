"""
Contains the Main class.
"""

from level import Level
from view import View

def main():
    """ 
    Run the physics simulator, take player input,
    and display the state of the game to a window.
    """
    fps = 60
    dt = 1 / fps
    level = Level('level1/')
    view = View(level)
    view.refresh(dt)

if __name__ == '__main__':
    main()
