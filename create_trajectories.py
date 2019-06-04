###################################################################################################
# Python script used to create random trajectories for training rnn. num of samples defined below##
##################### Saves in a data.pkl file ####################################################
###################################################################################################
import numpy as np
import random
import pickle
import math

###################################################################################################
##################################Parameters for trajectories######################################
###################################################################################################

NUM_SAMPLES = 100000
NUM_TRAIN = 60000
NUM_VALIDATE = 20000
NUM_TEST = NUM_SAMPLES - NUM_TRAIN - NUM_VALIDATE

# straight, left, right, u
NUM_MANEUVERS = 4

# Seconds
TIMESTEP = 5
TURN_TIMESTEP = 10
MAX_TIMESTEP = 60

# mph
MIN_SPEED = 5
MAX_SPEED = 70
TURN_SPEED = 15
SPEED_VARIATION = 5
SPEED_ERROR = 2

# m (meter)
LOC_ERROR = 5
START_POS = (0,0)

# Distance in metre, speed in mph
SCALE_DISTANCE = 1500
SCALE_SPEED = 70

###################################################################################################
###################################################################################################


# equal probabilities for each trajectory, dependent on timesteps
PROB_RIGHT = 1/(NUM_MANEUVERS*(MAX_TIMESTEP/TIMESTEP))
PROB_LEFT = 1/(NUM_MANEUVERS*(MAX_TIMESTEP/TIMESTEP))
PROB_U = 1/(NUM_MANEUVERS*(MAX_TIMESTEP/TIMESTEP))


def mph_to_mps(speed):
	return speed*1609/3600

def get_next_location(location, speed, state):
	if state==0:
		location[0] = location[0] + mph_to_mps(speed)*TIMESTEP
	elif state==1:
		location[1] = location[1] + mph_to_mps(speed)*TIMESTEP
	elif state==2:
		location[1] = location[1] - mph_to_mps(speed)*TIMESTEP
	else:
		location[0] = location[0] - mph_to_mps(speed)*TIMESTEP
	return location

def errored_speed(speed):
	return speed + random.randint(-SPEED_ERROR,SPEED_ERROR)

def errored_position(location):
	r = random.random()*LOC_ERROR
	theta = random.random()*2*np.pi
	location[0] = location[0] + r*np.sin(theta)
	location[1] = location[1] + r*np.cos(theta)
	return location

def get_next_turn():
	'''
	turn = 0 - straight
	turn = 1 - left
	turn = 2 - right
	turn = 3 - u turn
	'''
	num = random.random()
	if num<(1 - (PROB_U + PROB_RIGHT + PROB_LEFT)):
		turn = 0
	elif num<(1 - (PROB_U + PROB_RIGHT)):
		turn = 1
	elif num<(1 - (PROB_U)):
		turn = 2
	else:
		turn = 3
	return turn

def get_next_speed(speed,t_turn):
	if t_turn>0 and t_turn<=(TURN_TIMESTEP//TIMESTEP):
		if speed <= TURN_SPEED:
			return speed
		else:
			return speed - (speed - TURN_SPEED)//(TURN_TIMESTEP//TIMESTEP + 1 - t_turn)
	elif t_turn>(TURN_TIMESTEP//TIMESTEP) and t_turn<=(2*TURN_TIMESTEP//TIMESTEP):
		return speed + (MAX_SPEED - speed)//(2*TURN_TIMESTEP//TIMESTEP + 2 - t_turn)
	return random.randint(max(MIN_SPEED,speed - SPEED_VARIATION),min(MAX_SPEED,speed + SPEED_VARIATION))

def scale_location(location):
	return [location[0]/SCALE_DISTANCE,location[1]/SCALE_DISTANCE]

def scale_speed(speed):
	return speed/SCALE_SPEED

def get_rotate_angle():
	theta = random.random()*2*np.pi
	return theta

def rotate(point,angle,origin=[0,0]):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def main():
	x_train,x_val,x_test,y_train,y_val,y_test=[],[],[],[],[],[]
	for i in range(0,NUM_SAMPLES):
		t = 0
		trajectory = []
		location = list(START_POS)
		speed = random.randint(MIN_SPEED,MAX_SPEED)
		state = 0
		turn = 0
		t_turn = 0
		theta = get_rotate_angle()
		while (t<MAX_TIMESTEP):
			# trajectory.append([t//TIMESTEP] + [scale_location(errored_position(location))] + [scale_speed(errored_speed(speed))] + [state])
			if t==0:
				trajectory.append(scale_location(rotate(location,theta)) + [scale_speed(errored_speed(speed))])
			else:
				trajectory.append(scale_location(errored_position(rotate(location,theta))) + [scale_speed(errored_speed(speed))])
			if t_turn==0:
				turn = get_next_turn()
				if turn:
					t_turn = 1
			else:
				t_turn += 1
			if t_turn>=(TURN_TIMESTEP//TIMESTEP):
				state = turn
			location = get_next_location(location,speed,state)
			speed = get_next_speed(speed,t_turn)
			t+=TIMESTEP
		if i<NUM_TRAIN:
			x_train.append(trajectory)
			y_train.append(turn)
		elif i<(NUM_VALIDATE + NUM_TRAIN):
			x_val.append(trajectory)
			y_val.append(turn)
		else:
			x_test.append(trajectory)
			y_test.append(turn)
	with open('data.pkl', 'wb') as f:
		pickle.dump([x_train,x_val,x_test,y_train,y_val,y_test],f) 
	
if __name__ == '__main__':
    main()