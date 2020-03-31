import jax.numpy as np

EPSILON = 0.1

def not_zero(x):
    if abs(x) > EPSILON:
        return x
    elif x > 0:
        return EPSILON
    else:
        return -EPSILON

def wrap_to_pi(x):
    return ((x+np.pi) % (2*np.pi)) - np.pi

def triangles_intersect(tri1, tri2):
    """
        Do two isocele triangles intersect?
        We do assume that a corner cannot go through the other triangle in a single timestep
    :param tri1: (center, length, width, angle)
    :param tri2: (center, length, width, angle)
    """

    (c1, l1, w1, a1) = tri1
    (c2, l2, w2, a2) = tri2

    c1, s1 = np.cos(a1), np.sin(a1)
    c2, s2 = np.cos(a2), np.sin(a2)

    a1x = 2.0/3.0*l1*c1
    a1y = 2.0/3.0*l1*s1
    b1x = 0.0
    b1y = 0.0
    c1x = 0.0
    c1y = 0.0

    return False # tri_tri_2d([[a1x, a1y], [b1x, b1y], [c1x, c1y]], [[a2x, a2y], [b2x, b2y], [c2x, c2y]])

def check_tri_winding(tri, allowReversed):
	trisq = np.ones((3,3))
	trisq[:,0:2] = np.array(tri)
	detTri = np.linalg.det(trisq)
	if detTri < 0.0:
		if allowReversed:
			a = trisq[2,:].copy()
			trisq[2,:] = trisq[1,:]
			trisq[1,:] = a
		else: raise ValueError("triangle has wrong winding direction")
	return trisq

def tri_tri_2d(t1, t2, eps = 0.0, allowReversed = False, onBoundary = True):
	#Triangles must be expressed anti-clockwise
	t1s = check_tri_winding(t1, allowReversed)
	t2s = check_tri_winding(t2, allowReversed)
 
	if onBoundary:
		#Points on the boundary are considered as colliding
		chkEdge = lambda x: np.linalg.det(x) < eps
	else:
		#Points on the boundary are not considered as colliding
		chkEdge = lambda x: np.linalg.det(x) <= eps
 
	#For edge E of trangle 1,
	for i in range(3):
		edge = np.roll(t1s, i, axis=0)[:2,:]
 
		#Check all points of trangle 2 lay on the external side of the edge E. If
		#they do, the triangles do not collide.
		if (chkEdge(np.vstack((edge, t2s[0]))) and
			chkEdge(np.vstack((edge, t2s[1]))) and  
			chkEdge(np.vstack((edge, t2s[2])))):
			return False
 
	#For edge E of trangle 2,
	for i in range(3):
		edge = np.roll(t2s, i, axis=0)[:2,:]
 
		#Check all points of trangle 1 lay on the external side of the edge E. If
		#they do, the triangles do not collide.
		if (chkEdge(np.vstack((edge, t1s[0]))) and
			chkEdge(np.vstack((edge, t1s[1]))) and  
			chkEdge(np.vstack((edge, t1s[2])))):
			return False
 
	#The triangles collide
	return True

def class_from_path(path):
    module_name, class_name = path.rsplit(".", 1)
    class_object = getattr(importlib.import_module(module_name), class_name)
    return class_object