# Core/aerodynamics/inflatable_drag.py
import math

class InflatableDragCalculator:
    def __init__(self, config):
        self.config = config
    
    def calculate_drag(self, wind_speed):
        # Get reference area from config
        area = self.config['aerodynamics']['reference_area']
        
        # Calculate drag force
        drag_force = 0.5 * 1.225 * (wind_speed ** 2) * \
                    self.config['aerodynamics']['drag_coefficient'] * area
        
        return drag_force
    
    def update_kite_system(self, kite_system):
        # Add drag to kite system
        additional_drag = self.calculate_drag(kite_system.wind_speed)
        kite_system.total_drag += additional_drag
        return kite_system

