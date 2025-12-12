# Importing Entity
from src.scenes.scene_entity import Scene

# Importing systems
from src.systems.inputs_sys import InputHandling 

class GameRunning(Scene):
    '''
    
    '''
    def __init__(self, scene_system):
        super().__init__(scene_system)
        
        self.handle_input = InputHandling()
    
    
