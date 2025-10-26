def cm_to_steps(distance, distance_per_step):
    try:
        steps = int(round(distance / distance_per_step))
        
    except ZeroDivisionError:
        steps = 0
        
    return steps

def steps_to_cm(steps, distance_per_step):
	distance = steps * distance_per_step
      
	return distance