# simulation_core.py
import simpy
import numpy as np
from distributions import get_interarrival_time, get_service_time
import time # To track wall-clock time if needed
import statistics
from collections import defaultdict # Useful for per-server data

class Customer:
    """Minimal customer representation"""
    def __init__(self, customer_id, arrival_time):
        self.id = customer_id
        self.arrival_time = arrival_time
        self.service_start_time = -1.0
        self.service_end_time = -1.0
        self.server_id_used = None # Track which server was used

class SimulationData:
    """Collects data during the simulation run (modified for individual server tracking)"""
    def __init__(self, num_servers):
        self.num_servers = num_servers
        self.wait_times = []
        self.system_times = []
        # Track busy time per server
        self.server_busy_time = defaultdict(float)
        self.server_busy_start_times = {} # key: server_id, value: last busy start time
        self.total_served_count = 0
        self.server_customer_counts = defaultdict(int) # Track customers served per server
        self.queue_lengths_over_time = [] # List of tuples (timestamp, queue_length)
        self.last_event_time = 0.0
        self.current_queue_length = 0

    def record_queue_length(self, timestamp):
        """Records the queue length just before it changes."""
        time_interval = timestamp - self.last_event_time
        # Prevent recording zero-duration intervals excessively if events happen at the same time
        if time_interval > 1e-9: # Use a small tolerance instead of > 0
            self.queue_lengths_over_time.append((time_interval, self.current_queue_length))
            self.last_event_time = timestamp
        # If multiple events happen "simultaneously", ensure last_event_time updates
        elif time_interval == 0:
            self.last_event_time = timestamp


    def add_customer_served(self, customer: Customer, env_now: float):
        wait_time = customer.service_start_time - customer.arrival_time
        system_time = env_now - customer.arrival_time
        self.wait_times.append(wait_time)
        self.system_times.append(system_time)
        self.total_served_count += 1
        if customer.server_id_used is not None:
            self.server_customer_counts[customer.server_id_used] += 1

    def record_server_start_busy(self, server_id, timestamp):
        # Should not already be busy, but check defensively
        if server_id not in self.server_busy_start_times:
            self.server_busy_start_times[server_id] = timestamp
        # else: print(f"Warning: Server {server_id} started busy at {timestamp} but was already marked busy.") # Debugging line

    def record_server_end_busy(self, server_id, timestamp):
        if server_id in self.server_busy_start_times:
            start_time = self.server_busy_start_times[server_id]
            busy_duration = timestamp - start_time
            if busy_duration > 0: # Avoid adding zero duration if start/end are same instant
                 self.server_busy_time[server_id] += busy_duration
            del self.server_busy_start_times[server_id] # Mark server as idle for tracking
        # else: print(f"Warning: Server {server_id} ended busy at {timestamp} but wasn't marked busy.") # Debugging line


    def finalize(self, env_now):
         """Finalize calculations at the end of simulation."""
         # Ensure any ongoing busy time is accounted for per server
         servers_still_busy = list(self.server_busy_start_times.keys())
         for server_id in servers_still_busy:
             start_time = self.server_busy_start_times[server_id]
             busy_duration = env_now - start_time
             if busy_duration > 0:
                  self.server_busy_time[server_id] += busy_duration
             del self.server_busy_start_times[server_id] # Clear ongoing busy status

         # Record final queue length interval
         self.record_queue_length(env_now)

# --- customer_process needs significant changes ---
def customer_process(env, customer_id, server_pool, arrival_params, service_params, data, rng, arrival_dist, service_dist):
    """Process defining a customer's journey (using simpy.Store)."""
    customer = Customer(customer_id, env.now)

    # Record queue length change on arrival
    data.record_queue_length(env.now)
    data.current_queue_length += 1

    # Request a server object from the store
    # Server objects are just integers representing IDs in this case
    server_id = yield server_pool.get()
    customer.server_id_used = server_id # Store which server was used

    # Got a server
    customer.service_start_time = env.now

    # Record queue length change on service start
    data.record_queue_length(env.now)
    data.current_queue_length -= 1

    # Record that this specific server is now busy
    data.record_server_start_busy(server_id, customer.service_start_time)

    # Perform service
    service_time = get_service_time(service_dist, service_params, rng)
    yield env.timeout(service_time) # Undergo service

    # Service finished
    customer.service_end_time = env.now

    # Record that this specific server is now free
    data.record_server_end_busy(server_id, customer.service_end_time)

    # Add customer stats to overall data
    data.add_customer_served(customer, customer.service_end_time)

    # Release the server object back to the store
    yield server_pool.put(server_id)


# --- customer_source needs to pass server_pool ---
def customer_source(env, server_pool, arrival_params, service_params, data, rng, stop_condition_type, stop_condition_value, arrival_dist, service_dist):
    """Generates customers based on arrival distribution."""
    customer_id = 0
    while True:
        # Generate next arrival time
        interarrival = get_interarrival_time(arrival_dist, arrival_params, rng)
        yield env.timeout(interarrival) # Wait for next arrival

        customer_id += 1
        # Pass server_pool instead of servers resource
        env.process(customer_process(env, customer_id, server_pool, arrival_params, service_params, data, rng, arrival_dist, service_dist))

        # Check stopping condition (same logic as before)
        if stop_condition_type == "Number of Customers" and data.total_served_count >= stop_condition_value:
            break
        if stop_condition_type == "Simulation Time" and env.now >= stop_condition_value:
            break

# --- run_simulation needs to initialize Store and Data correctly ---
def run_simulation(params: dict) -> SimulationData:
    """Sets up and runs a single simulation instance (using simpy.Store)."""
    start_time = time.time() # Wall-clock time

    seed = params.get("seed", None)
    rng = np.random.default_rng(seed)
    num_servers = params["num_servers"] # Get number of servers

    env = simpy.Environment()
    # Use a Store for individual server tracking
    server_pool = simpy.Store(env, capacity=num_servers)
    # Initialize the store with server IDs (0 to N-1)
    server_pool.items.extend(range(num_servers))

    # Pass num_servers to SimulationData constructor
    data = SimulationData(num_servers=num_servers)

    arrival_dist = params["arrival_distribution"]
    service_dist = params["service_distribution"]
    arrival_p = {k: v for k, v in params.items() if k.startswith('arrival_')}
    service_p = {k: v for k, v in params.items() if k.startswith('service_') or k.startswith('fixed_') or k.startswith('mean_') or k.startswith('std_dev_')}

    # Pass server_pool to the source
    env.process(customer_source(env, server_pool, arrival_p, service_p, data, rng,
                                params["stop_condition_type"], params["stop_condition_value"],
                                arrival_dist, service_dist))

    # Run simulation (same logic as before)
    if params["stop_condition_type"] == "Simulation Time":
        env.run(until=params["stop_condition_value"])
    elif params["stop_condition_type"] == "Number of Customers":
         try:
            env.run() # Run until no more events or source stops generation based on count
         except Exception as e:
             print(f"Simulation run interrupted potentially by stopping condition: {e}")
    else:
        raise ValueError("Invalid stop condition type")

    # Finalize data collection
    data.finalize(env.now)
    # print(f"Simulation run (seed {seed}) took {time.time() - start_time:.2f} s wall clock time.")
    return data