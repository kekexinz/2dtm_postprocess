import numpy as np
from scipy.spatial.transform import Rotation as R

def euler_to_rotation(psi, theta, phi, degrees=True):
    """
    Convert Euler angles (psi, theta, phi) to a Rotation object using the ZYZ convention.
    The rotations are applied in the order: 
      1. Rotation about the Z-axis by psi,
      2. Rotation about the Y-axis by theta,
      3. Rotation about the Z-axis by phi.
    
    This convention aligns with the angular annotations used in RELION and cisTEM.
    """
    return R.from_euler('ZYZ', [psi, theta, phi], degrees=degrees)

def euler_to_matrix(psi, theta, phi, degrees=True):
    return R.from_euler('ZYZ', [psi, theta, phi], degrees=degrees).as_matrix()

def geodesic_distance(ref_rot, pixel_rot):
    """
    Compute the geodesic distance (in radians) between two rotations.
    
    Parameters:
    - ref_rot: the reference Rotation object.
    - pixel_rot: the Rotation object of the pixel to compare.
    
    The geodesic distance is the magnitude of the rotation vector
    corresponding to the relative rotation between ref_rot and pixel_rot.
    """
    # Compute the relative rotation from reference to pixel
    relative_rot = ref_rot.inv() * pixel_rot
    # The magnitude of the rotation vector represents the geodesic distance
    angle = np.linalg.norm(relative_rot.as_rotvec())
    return angle