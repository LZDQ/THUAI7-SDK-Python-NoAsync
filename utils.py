import os
import constants as C 
import socket

def get_firearm_id(s: str) -> int:
    return C._firearms.index(s)

def get_item_id(s: str) -> int:
    return C._items.index(s)

def get_supply_id(s: str) -> int:
    return C._supplies.index(s)

def get_medicine_id(s: str) -> int:
    return C._medicines.index(s)

def dist(p, q) -> float:
    return ((p[0]-q[0])**2 + (p[1]-q[1])**2) ** 0.5

saiblo = os.environ.get("SAIBLO")

def get_ip_address(service_name):
    try:
        # Get the host name to IP resolution
        ip_address = socket.gethostbyname(service_name)
        return ip_address
    except socket.gaierror:
        return f"Failed to get IP address for {service_name}"

def get_inv_weight(inv_cnt) -> int:
    return sum(cnt * weight for cnt, weight in zip(inv_cnt, C._item_weight))

# by GPT-4
def ray_intersects_box(sx, sy, tx, ty, bx, by):
    """
    Check if a ray intersects a box. The box is defined by its bottom-left corner (bx, by) and top-right corner (bx+1, by+1).
    The ray starts at (sx, sy) and ends at (tx, ty).
    """
    # Directions of the ray
    dx = tx - sx
    dy = ty - sy
    
    # Inverse of directions
    inv_dx = 1.0 / dx if dx != 0 else float('inf')
    inv_dy = 1.0 / dy if dy != 0 else float('inf')
    
    # Calculating parameters tmin and tmax for intersection
    tmin = min((bx - sx) * inv_dx, (bx + 1 - sx) * inv_dx)
    tmax = max((bx - sx) * inv_dx, (bx + 1 - sx) * inv_dx)
    tymin = min((by - sy) * inv_dy, (by + 1 - sy) * inv_dy)
    tymax = max((by - sy) * inv_dy, (by + 1 - sy) * inv_dy)
    
    # Updating tmin and tmax to include y parameters
    tmin = max(tmin, tymin)
    tmax = min(tmax, tymax)
    
    # If tmax >= 0 and tmax >= tmin, there is an intersection
    return tmax >= max(0, tmin)
