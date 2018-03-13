from sys import argv
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np
import random
import pickle

num = 0
flowtype = " "
polygon = None
area = None
length = None
energy = None
time = None
iso = None
patch = None
ax = None

#sets the poylgon to whatever the parameter is
def set_poly(poly):
	global polygon, num
	polygon = poly
	num = len(polygon)-1

#prompts the user to manually input a polygon with n vertices 
def prompt(n):
	global polygon
	global num
	polygon = np.zeros((n+1, 2))
	for i in range (0,n):
		print "point %d" %i
		polygon[i,0] = raw_input("x value: ")
		polygon[i,1] = raw_input("y value: ")
	polygon[n] = polygon[0]
	num = n
	return polygon

#generates a random polygon with n vertices that may not be simple
def rand_poly(n):
	global polygon
	global num
	polygon = np.zeros((n+1,2))
	for i in range(0,n):
		polygon[i,0] = random.uniform(-5,5)
		polygon[i,1] = random.uniform(-5,5)
	polygon[n] = polygon[0]
	num = n
	return polygon

#This should get a velocity vector for each point in the polygon.  
#It should also be able to do different kinds of flow such as glickenstein or curvature
def get_velocity(flow):
	if(flow == 'curvature'):
		return curv_flow()
	elif(flow == 'glickenstein'):
		return glick_flow()
	elif(flow == 'renormglick'):
		return renorm_glick()
	elif(flow == 'tangent'):
		return tangent_flow()
	elif(flow == 'translation'):
		return translation_flow()
	elif(flow == 'rscg'):
		return rscg()
	elif(flow == 'modified'):
		return mod_curv()
	else:
		print('You didn\'t type the flow name right or something')

#returns the left vector field of polygon
def left_field():
	left = np.zeros((num, 2))
	left[0] = polygon[num-1] - polygon[0]
	for i in range(1, num):
		left[i] = polygon[i-1] - polygon[i]
	return left

#returns the right vector field of polygon
def right_field():
	right = np.zeros((num, 2))
	right[num-1] = polygon[0] - polygon[num-1]
	for i in range(0, num-1):
		right[i] = polygon[i+1] - polygon[i]
	return right

#gets the vector field for the curvature flow
def curv_flow():
	L = left_field()
	R = right_field()
	K = np.zeros((num, 2))
	for i in range(0, num):
		magL = magnitude(L[i])**2.			
		magR = magnitude(R[i])**2.
		magLR= magnitude(L[i] - R[i])**2.
		K[i] = (((magL-magR+magLR)/(magL*magLR))*L[i])
		K[i] += (((magR-magL+magLR)/(magR*magLR))*R[i])
	return K

# does paul's tangential flow
def tangent_flow():
	T = np.zeros((num,2))
	K = curv_flow()
	Kperp = np.zeros((num,2))
	for i in range(0, num):
		Kperp[i] = [K[i,1], -K[i,0]]
	R = right_field()
	L = left_field()
	for i in range(0, num):
		T[i] = K[i]-projection(L[i]+R[i], Kperp[i])
	return T

#does mack's hopefully better tangent flow (it doesn't actually fix the problem)
def tangent_flow2():
	L = left_field()
	R = right_field()
	K = curv_flow()
	T = np.zeros((num,2))
	for i in range(0, num):
		T[i] = projection(L[i]+R[i], K[i])
	return T
	
#does mack's first version of the tangential flow that isn't really tangential
def old_tangent_flow():
	L = left_field()
	R = right_field()
	T = np.zeros((num,2))
	for i in range(0, num):
		if magnitude(L[i]) > magnitude(R[i]):
			T[i] = L[i] * (1/magnitude(L[i])) * (magnitude(L[i])-magnitude(R[i]))
		elif magnitude(R[i]) > magnitude(L[i]):
			T[i] = R[i] * (1/magnitude(R[i])) * (magnitude(R[i])-magnitude(L[i]))
	return T+curv_flow()	

#does the glickenstein flow	
def glick_flow():
	flow = right_field()+left_field()
	return flow

#does the renormalized cg flow
def renorm_glick():
	glick = glick_flow()
	flow = np.zeros((num,2))
	ybar = np.zeros((1,2))
	for i in range(0,num):
		ybar+=polygon[i]
	ybar = ybar/num
	for i in range(0,num):
		flow[i]=glick[i] + (2-2*np.cos(2*np.pi/num))*(polygon[i]-ybar)
	return flow

#does the RSCG flow
def rscg():
	glick = glick_flow()
	for i in range(0,num):
		glick[i] = glick[i] * magnitude(glick[i])
	flow = np.zeros((num,2))
	ybar = np.zeros((1,2))
	for i in range(0,num):
		ybar+=polygon[i]
	ybar = ybar/num
	for i in range(0,num):
		flow[i]=glick[i] + ((2-2*np.cos(2*np.pi/num))**2.)*(polygon[i]-ybar)
	return flow

#returns the vector field for the modified curvature flow
def mod_curv():
	left = left_field()
	right = right_field()
	glick = glick_flow()
	ybar = 0
	for i in range(0,num):
		ybar+=polygon[i]
	ybar = ybar/num
	for i in range(0,num):
		glick[i] = glick[i]/(magnitude(left[i]-right[i])**2) 
	return glick

#move the polygon to the right WOOHOO
def translation_flow():
	flow = np.zeros((num,2))
	for i in range(0,num):
		flow[i][0] = 1
	return flow

#This will return how much we want the time to change at each step
def get_delta():
	if flowtype == 'curvature' or flowtype == 'tangent' or flowtype =='modified':
		return 0.05 * cross_area()
	else:
		return 0.05

def magnitude(vector):
	return (vector[0]**2. + vector[1]**2.)**0.5

def projection(vector1, vector2):
	return (np.vdot(vector1, vector2)/(magnitude(vector2)**2.))*vector2

#returns the area of polygon. does not work for complex polygons
def cross_area():
	area = 0
	for i in range (1, num-1):
		V = polygon[0] - polygon[i]
		W = polygon[0] - polygon[i+1]
		area += 0.5*scalar_cross(V, W)
	return np.absolute(area)

#returns the perimeter of polygon
def get_length():
	length = 0.0
	left = left_field()
	for i in range(0,num):
		length += magnitude(left[i])
	return length

#returns the energy of the polygon
def get_energy():
	energy = 0.0
	left = left_field()
	for i in range(0,num):
		energy += magnitude(left[i])**2.
	return 0.5*energy

def scalar_cross(V, W):	
	return V[0]*W[1]-W[0]*V[1]

#this method is used for animation it basically sets up all the objects needed for the animation
def setup(flow):
	#all these globals are no fun
	global area, time, length, energy, iso, patch, ax, flowtype
	flowtype = flow
	codes = np.ones(num+1)
	codes[num] = Path.CLOSEPOLY
	codes[0] = Path.MOVETO
	codes[1:num] = Path.LINETO
	path = Path(polygon,codes)
	fig, ax = plt.subplots()
	patch = patches.PathPatch(path, facecolor = 'None', lw = 1)
	#This bit puts the circles over the vertices
	for i in range (0, num):
		patch2 = patches.Circle(polygon[i], radius = 0.05)
		ax.add_patch(patch2)
	ax.add_patch(patch)
	#here are the height and width of the plot
	ax.set_ylim(-5,5)
	ax.set_xlim(-5,5)
	#these initialize lists that are used for the post-animation graphs
	area = [cross_area()]
	time = [0]
	length = [get_length()]
	energy = [get_energy()]
	iso = [(length[0]**2.)/area[0]]
	return fig

#updates the polygon and the isoperimetric list
def animate(i):
	delta = get_delta()
	time.append(time[len(time)-1] + delta) 
	velocity  = np.zeros((num,2))
	if i!=0:
		velocity = get_velocity(flowtype)
	change = velocity * delta
	for j in range(0,num):
		polygon[j] = polygon[j] + change[j]
	megapatch = [patch]
	for k in range(0,num):
		patch2 = patches.Circle(polygon[k], radius = 0.05)
		ax.add_patch(patch2)
		megapatch.append(patch2)
	area.append(cross_area())
	length.append(get_length())
	energy.append(get_energy())
	iso.append(length[len(length)-1]**2./area[len(area)-1])	
	return megapatch

#plots the isoperimatric ratio over time
def iso_plot():
	del time[0:3]
	for i in range(1, len(time)):
		time[i] -= time[0]
	time[0] =0
	del iso[0:3]
	plt.plot(time, iso, 'ro')
	plt.show()

