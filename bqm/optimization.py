# optimization.py
import numpy as np
import pandas as pd
from simulation_core import run_simulation, SimulationData
from reporting import calculate_summary_stats
import streamlit as st # For progress updates

def optimize_servers(base_params: dict, objective: str, constraints: dict,
                     min_servers: int, max_servers: int, num_replications: int) -> tuple:
    """
    Performs optimization by simulating different numbers of servers.
    V1: Simple iterative search over the number of servers.
    """
    results_list = []
    base_seed = base_params.get("seed", None)

    st.write(f"Optimizing number of servers from {min_servers} to {max_servers} ({num_replications} replications each)...")
    progress_bar = st.progress(0)
    total_runs = (max_servers - min_servers + 1) * num_replications

    current_run = 0
    for n_servers in range(min_servers, max_servers + 1):
        replication_results = []
        rep_wait_times = []
        rep_queue_lengths = []
        rep_utilizations = []
        rep_served = []

        current_params = base_params.copy()
        current_params["num_servers"] = n_servers

        for i in range(num_replications):
            # Generate a unique, deterministic seed for each replication
            if base_seed is not None:
                current_params["seed"] = base_seed + n_servers * num_replications + i
            else:
                 current_params["seed"] = None # Or generate a new random seed if base is None

            sim_data = run_simulation(current_params)

            # Determine actual sim duration (needed for reporting)
            if current_params["stop_condition_type"] == "Simulation Time":
                sim_duration = current_params["stop_condition_value"]
            else: # Number of customers - use the time the last event occurred
                sim_duration = sim_data.last_event_time

            stats = calculate_summary_stats(sim_data, sim_duration, n_servers)
            replication_results.append(stats)

            # Update progress
            current_run += 1
            progress_bar.progress(current_run / total_runs)


        # Average results across replications for this n_servers
        avg_wait = np.mean([res.get("avg_wait_time", float('inf')) for res in replication_results])
        avg_q_len = np.mean([res.get("avg_queue_length", float('inf')) for res in replication_results])
        avg_util = np.mean([res.get("avg_server_utilization", float('inf')) for res in replication_results])
        avg_served = np.mean([res.get("total_served", 0) for res in replication_results]) # Throughput proxy

        results_list.append({
            "num_servers": n_servers,
            "avg_wait_time": avg_wait,
            "avg_queue_length": avg_q_len,
            "avg_server_utilization": avg_util,
            "avg_total_served": avg_served
        })

    progress_bar.empty() # Remove progress bar

    # --- AI Decision Logic ---
    # Filter results based on constraints
    valid_results = []
    for res in results_list:
        passes_constraints = True
        if "max_avg_wait_time" in constraints and res["avg_wait_time"] > constraints["max_avg_wait_time"]:
            passes_constraints = False
        if "max_avg_queue_length" in constraints and res["avg_queue_length"] > constraints["max_avg_queue_length"]:
            passes_constraints = False
        if "max_avg_utilization" in constraints and res["avg_server_utilization"] > constraints["max_avg_utilization"]:
             passes_constraints = False
        # Add more constraint checks here if needed (e.g., min throughput)

        if passes_constraints:
            valid_results.append(res)

    if not valid_results:
        st.warning("No configuration met the specified constraints.")
        return None, pd.DataFrame(results_list)

    # Select best based on objective
    best_result = None
    if objective == "Minimize Average Waiting Time":
        best_result = min(valid_results, key=lambda x: x["avg_wait_time"])
    elif objective == "Minimize Number of Servers":
         # Find the minimum number of servers among valid results
         # If multiple have the same min servers, criteria needed (e.g., lowest wait time among those)
         min_valid_servers = min(res["num_servers"] for res in valid_results)
         candidates = [res for res in valid_results if res["num_servers"] == min_valid_servers]
         # Default tie-breaker: lowest wait time
         best_result = min(candidates, key=lambda x: x["avg_wait_time"])
    elif objective == "Maximize Throughput (Avg Total Served)":
         best_result = max(valid_results, key=lambda x: x["avg_total_served"])
    # Add other objectives like minimizing queue length...

    if best_result:
        st.success(f"Optimization complete. Recommended configuration found.")
        return best_result, pd.DataFrame(results_list) # Return best and all results for comparison
    else:
        # This case should ideally be covered by the "No configuration met constraints" warning
        st.error("Could not determine optimal configuration.")
        return None, pd.DataFrame(results_list)