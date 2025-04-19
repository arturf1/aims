# distributions.py
import numpy as np
import math

def get_interarrival_time(dist_type: str, params: dict, rng: np.random.Generator) -> float:
    """Generates interarrival time based on distribution type."""
    if dist_type == "Exponential (Poisson Process)":
        # params['arrival_rate'] = arrivals per unit time
        # mean interarrival time = 1 / arrival_rate
        if params['arrival_rate'] <= 0:
             raise ValueError("Arrival rate must be positive for Exponential distribution.")
        mean_interarrival = 1.0 / params['arrival_rate']
        return rng.exponential(mean_interarrival)
    elif dist_type == "Constant Rate":
         if params['arrival_rate'] <= 0:
             raise ValueError("Arrival rate must be positive for Constant Rate.")
         return 1.0 / params['arrival_rate'] # Fixed time between arrivals
    elif dist_type == "Fixed Interval":
        if params['fixed_interval'] <= 0:
            raise ValueError("Fixed interval must be positive.")
        return params['fixed_interval']
    else:
        raise ValueError(f"Unknown arrival distribution type: {dist_type}")

def get_service_time(dist_type: str, params: dict, rng: np.random.Generator) -> float:
    """Generates service time based on distribution type."""
    if dist_type == "Exponential":
        # params['service_rate'] = services per unit time
        # mean service time = 1 / service_rate
        if params['service_rate'] <= 0:
            raise ValueError("Service rate must be positive for Exponential distribution.")
        mean_service_time = 1.0 / params['service_rate']
        return rng.exponential(mean_service_time)
    elif dist_type == "Constant":
        if params['fixed_service_time'] <= 0:
            raise ValueError("Fixed service time must be positive.")
        return params['fixed_service_time']
    elif dist_type == "Normal":
        mean = params['mean_service_time']
        std_dev = params['std_dev_service_time']
        if mean <= 0 or std_dev < 0:
            raise ValueError("Mean service time must be positive and standard deviation non-negative for Normal distribution.")
        # Ensure non-negative service time
        return max(0, rng.normal(mean, std_dev))
    else:
        raise ValueError(f"Unknown service distribution type: {dist_type}")