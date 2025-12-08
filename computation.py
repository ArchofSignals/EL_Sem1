import math

# --- COMPUTATION LOGIC ---
def process_data(payload, fault_threshold=15.0):
    """
    Process vibration sensor data and detect faults.
    
    Args:
        payload (str): Comma-separated accelerometer values "x,y,z"
        fault_threshold (float): Magnitude threshold above which a fault is flagged (default: 15.0 m/s^2)
    
    Returns:
        tuple: (x, y, z, magnitude, status) or None on error
    """
    try:
        # 1. Parse string "x,y,z" into floats
        parts = payload.split(',')
        x = float(parts[0])
        y = float(parts[1])
        z = float(parts[2])

        # 2. Compute Total Acceleration Vector (Pythagoras theorem)
        # Vector Magnitude = sqrt(x^2 + y^2 + z^2)
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        # 3. Simple Fault Logic
        # If the machine is still, magnitude is ~9.8 (Gravity). 
        # Strong vibration pushes this much higher.
        status = "NORMAL"
        if magnitude > fault_threshold:
            status = "CRITICAL FAULT"
            print(f"⚠️ FAULT DETECTED! Magnitude: {magnitude:.2f} m/s^2")

        return x, y, z, magnitude, status

    except Exception as e:
        print(f"Error processing data: {e}")
        return None