# reporting.py
import statistics
import numpy as np
import pandas as pd
from simulation_core import SimulationData

def calculate_summary_stats(data: SimulationData, sim_duration: float, num_servers: int) -> dict:
    """Calculates summary statistics from simulation data (updated for individual server util)."""
    results = {}

    if data.wait_times:
        results["avg_wait_time"] = statistics.mean(data.wait_times)
        results["max_wait_time"] = max(data.wait_times)
        results["std_dev_wait_time"] = statistics.stdev(data.wait_times) if len(data.wait_times) > 1 else 0.0
    else:
        results["avg_wait_time"] = 0.0
        results["max_wait_time"] = 0.0
        results["std_dev_wait_time"] = 0.0

    # Calculate time-weighted average queue length (same as before)
    total_time_x_length = sum(interval * length for interval, length in data.queue_lengths_over_time)
    # Use the finalized simulation duration as total time
    total_recorded_time = sim_duration
    # Adjust slightly if last_event_time is negligibly different due to floating point
    if abs(data.last_event_time - sim_duration) < 1e-9:
        total_recorded_time = data.last_event_time if data.last_event_time > 0 else sim_duration


    if total_recorded_time > 1e-9: # Use tolerance
         results["avg_queue_length"] = total_time_x_length / total_recorded_time
    else:
         results["avg_queue_length"] = 0.0

    results["max_queue_length"] = max(length for _, length in data.queue_lengths_over_time) if data.queue_lengths_over_time else 0

    # --- Calculate average AND individual server utilization ---
    total_possible_server_time_per_server = sim_duration
    total_possible_system_time = sim_duration * num_servers

    # Sum busy time across all servers tracked in data.server_busy_time dictionary
    total_actual_busy_time = sum(data.server_busy_time.values())

    if total_possible_system_time > 1e-9:
        results["avg_server_utilization"] = (total_actual_busy_time / total_possible_system_time) * 100 # as percentage
    else:
        results["avg_server_utilization"] = 0.0

    # Calculate individual server utilization
    individual_utilization = {}
    for i in range(num_servers):
        busy_time = data.server_busy_time.get(i, 0.0) # Get busy time for server i, default 0
        if total_possible_server_time_per_server > 1e-9:
            util = (busy_time / total_possible_server_time_per_server) * 100
        else:
            util = 0.0
        individual_utilization[f"Server_{i}"] = util

    results["individual_server_utilization"] = individual_utilization
    results["server_customer_counts"] = dict(data.server_customer_counts) # Convert defaultdict

    results["total_served"] = data.total_served_count

    # Plotting data generation (same as before)
    # Queue length over time
    if data.queue_lengths_over_time:
        plot_times = []
        plot_lengths = []
        current_time = 0
        for interval, length in data.queue_lengths_over_time:
            plot_times.extend([current_time, current_time + interval])
            plot_lengths.extend([length, length])
            current_time += interval
        queue_df = pd.DataFrame({'Time': plot_times, 'Queue Length': plot_lengths}).set_index('Time')
        # Ensure the chart extends to the full sim_duration
        if not queue_df.empty and queue_df.index[-1] < sim_duration:
             last_len = queue_df['Queue Length'].iloc[-1]
             extra_row = pd.DataFrame({'Queue Length': [last_len]}, index=[sim_duration])
             queue_df = pd.concat([queue_df, extra_row])
        results["queue_length_df"] = queue_df
    else:
         results["queue_length_df"] = pd.DataFrame({'Time': [0, sim_duration], 'Queue Length': [0, 0]}).set_index('Time')


    # Wait time histogram data
    if data.wait_times:
        counts, bin_edges = np.histogram(data.wait_times, bins='auto')
        hist_df = pd.DataFrame({'Wait Time Interval': [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(counts))], 'Count': counts})
        hist_df = hist_df.set_index('Wait Time Interval')
        results["wait_time_hist_df"] = hist_df
    else:
        results["wait_time_hist_df"] = pd.DataFrame({'Wait Time Interval': ['N/A'], 'Count': [0]}).set_index('Wait Time Interval')

    return results