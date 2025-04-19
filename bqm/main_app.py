# main_app.py
import streamlit as st
import numpy as np
import pandas as pd
from simulation_core import run_simulation, SimulationData
from reporting import calculate_summary_stats
from optimization import optimize_servers
import distributions # Ensure functions are accessible

# --- Page Config ---
st.set_page_config(
    page_title="AIMS Basic Queue Modeler",
    page_icon="📊",
    layout="wide"
)

# --- Title ---
st.title("📊 AIMS Basic Queue Modeler V1.0")
st.markdown("""
Welcome to the **Artificial Intelligence Making Sims (AIMS)** basic queue modeler.
Define your queuing system parameters in the sidebar, run a single simulation,
or let the **AIMS AI** optimize the number of servers based on your goals.
""")

# --- Sidebar for Inputs ---
st.sidebar.header("Simulation Parameters")

# Arrival Process
st.sidebar.subheader("Arrival Process")
arrival_dist_type = st.sidebar.selectbox(
    "Arrival Distribution",
    ["Exponential (Poisson Process)", "Constant Rate", "Fixed Interval"],
    key="arrival_dist"
)
arrival_params = {}
if arrival_dist_type == "Exponential (Poisson Process)" or arrival_dist_type == "Constant Rate":
    arrival_params['arrival_rate'] = st.sidebar.number_input("Average Arrival Rate (customers/unit time)", min_value=0.01, value=5.0, step=0.1, key="arrival_rate")
else: # Fixed Interval
    arrival_params['fixed_interval'] = st.sidebar.number_input("Fixed Time Between Arrivals", min_value=0.01, value=0.2, step=0.01, key="fixed_interval")

# Service Process
st.sidebar.subheader("Service Process")
service_dist_type = st.sidebar.selectbox(
    "Service Distribution",
    ["Exponential", "Constant", "Normal"],
    key="service_dist"
)
service_params = {}
if service_dist_type == "Exponential":
    service_params['service_rate'] = st.sidebar.number_input("Average Service Rate (customers/unit time)", min_value=0.01, value=6.0, step=0.1, key="service_rate")
elif service_dist_type == "Constant":
    service_params['fixed_service_time'] = st.sidebar.number_input("Fixed Service Time", min_value=0.01, value=0.15, step=0.01, key="fixed_service_time")
else: # Normal
    service_params['mean_service_time'] = st.sidebar.number_input("Mean Service Time", min_value=0.01, value=0.15, step=0.01, key="mean_service_time")
    service_params['std_dev_service_time'] = st.sidebar.number_input("Std Dev Service Time", min_value=0.0, value=0.05, step=0.01, key="std_dev_service_time")

# Number of Servers (for single run)
num_servers_single = st.sidebar.number_input("Number of Servers", min_value=1, value=1, step=1, key="num_servers_single")

# Simulation Stop Condition
st.sidebar.subheader("Stopping Condition")
stop_condition_type = st.sidebar.selectbox(
    "Stop simulation based on:",
    ["Simulation Time", "Number of Customers"],
    key="stop_type"
)
stop_condition_value = st.sidebar.number_input(
    f"Value ({'Simulated Time Units' if stop_condition_type == 'Simulation Time' else 'Number of Customers'})",
    min_value=1, value=100 if stop_condition_type == "Number of Customers" else 100, step=1, key="stop_value"
)

# Random Seed
seed = st.sidebar.number_input("Random Seed (optional)", value=42, step=1, key="seed")
use_seed = st.sidebar.checkbox("Use Fixed Seed", value=True, key="use_seed")
final_seed = seed if use_seed else None

# --- Simulation Control ---
st.sidebar.subheader("Run Simulation")
run_button = st.sidebar.button("Run Single Simulation")

# --- Optimization Section ---
st.sidebar.subheader("Optimize Number of Servers")
optimize_button = st.sidebar.button("Run Optimization")

min_opt_servers = st.sidebar.number_input("Min Servers to Test", min_value=1, value=1, step=1, key="min_opt_servers")
max_opt_servers = st.sidebar.number_input("Max Servers to Test", min_value=min_opt_servers, value=5, step=1, key="max_opt_servers")
num_replications = st.sidebar.number_input("Replications per Configuration", min_value=1, value=5, step=1, key="num_replications")

objective = st.sidebar.selectbox(
    "Optimization Objective",
    ["Minimize Average Waiting Time", "Minimize Number of Servers", "Maximize Throughput (Avg Total Served)"],
    key="opt_objective"
)

# Constraints
st.sidebar.markdown("**Constraints (Optional):**")
use_wait_constraint = st.sidebar.checkbox("Max Average Wait Time", key="use_wait_const")
max_wait_constraint = st.sidebar.number_input("Value", min_value=0.0, value=1.0, step=0.1, disabled=not use_wait_constraint, key="max_wait_const_val")

use_util_constraint = st.sidebar.checkbox("Max Average Server Utilization (%)", key="use_util_const")
max_util_constraint = st.sidebar.number_input("Value (%)", min_value=0.0, max_value=100.0, value=95.0, step=1.0, disabled=not use_util_constraint, key="max_util_const_val")

# --- Main Area for Results ---
st.header("Results")

# Session state to store results
if 'sim_results' not in st.session_state:
    st.session_state.sim_results = None
if 'opt_results' not in st.session_state:
    st.session_state.opt_results = None
if 'opt_comparison_df' not in st.session_state:
    st.session_state.opt_comparison_df = None


# --- Handle Button Clicks ---

if run_button:
    st.session_state.opt_results = None # Clear optimization results if single run is triggered
    st.session_state.opt_comparison_df = None

    params = {
        "arrival_distribution": arrival_dist_type,
        **arrival_params,
        "service_distribution": service_dist_type,
        **service_params,
        "num_servers": num_servers_single,
        "stop_condition_type": stop_condition_type,
        "stop_condition_value": stop_condition_value,
        "seed": final_seed
    }

    try:
        with st.spinner("Running Simulation..."):
            sim_data = run_simulation(params)

            # Determine actual sim duration for reporting
            if params["stop_condition_type"] == "Simulation Time":
                sim_duration = params["stop_condition_value"]
            else:
                sim_duration = sim_data.last_event_time

            results = calculate_summary_stats(sim_data, sim_duration, params["num_servers"])
            st.session_state.sim_results = results
            st.success("Simulation Complete!")

    except ValueError as e:
        st.error(f"Input Error: {e}")
    except Exception as e:
        st.error(f"An error occurred during simulation: {e}")


if optimize_button:
    st.session_state.sim_results = None # Clear single run results

    base_params = {
        "arrival_distribution": arrival_dist_type,
        **arrival_params,
        "service_distribution": service_dist_type,
        **service_params,
        # num_servers is handled by optimization loop
        "stop_condition_type": stop_condition_type,
        "stop_condition_value": stop_condition_value,
        "seed": final_seed # Base seed for replicability
    }

    constraints = {}
    if use_wait_constraint:
        constraints["max_avg_wait_time"] = max_wait_constraint
    if use_util_constraint:
        constraints["max_avg_utilization"] = max_util_constraint

    try:
        with st.spinner("Running Optimization (this may take a while)..."):
             best_config, comparison_df = optimize_servers(
                 base_params, objective, constraints,
                 min_opt_servers, max_opt_servers, num_replications
             )
             st.session_state.opt_results = best_config
             st.session_state.opt_comparison_df = comparison_df

    except ValueError as e:
        st.error(f"Input Error during Optimization setup: {e}")
    except Exception as e:
        st.error(f"An error occurred during optimization: {e}")
        st.session_state.opt_results = None
        st.session_state.opt_comparison_df = None


# --- Display Results ---

if st.session_state.sim_results:
    st.subheader("Single Simulation Run Results")
    results = st.session_state.sim_results
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Wait Time", f"{results.get('avg_wait_time', 0):.3f}")
    col2.metric("Max Wait Time", f"{results.get('max_wait_time', 0):.3f}")
    col3.metric("Std Dev Wait Time", f"{results.get('std_dev_wait_time', 0):.3f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Avg Queue Length", f"{results.get('avg_queue_length', 0):.3f}")
    col5.metric("Max Queue Length", f"{results.get('max_queue_length', 0)}")
    col6.metric("Avg Server Utilization (%)", f"{results.get('avg_server_utilization', 0):.2f}%")

    st.metric("Total Customers Served", f"{results.get('total_served', 0)}")

    st.subheader("Charts")
    if results.get("queue_length_df") is not None and not results["queue_length_df"].empty:
        st.line_chart(results["queue_length_df"])
    else:
        st.write("Queue length data not available.")

    if results.get("wait_time_hist_df") is not None and not results["wait_time_hist_df"].empty:
         st.bar_chart(results["wait_time_hist_df"])
    else:
         st.write("Wait time histogram data not available.")


if st.session_state.opt_results:
    st.subheader("Optimization Results")
    st.write(f"**Objective:** {objective}")
    st.write(f"**Constraints:**")
    constraints_applied = False
    if use_wait_constraint:
        st.write(f"- Max Average Wait Time <= {max_wait_constraint}")
        constraints_applied = True
    if use_util_constraint:
        st.write(f"- Max Average Server Utilization <= {max_util_constraint}%")
        constraints_applied = True
    if not constraints_applied:
        st.write("- None")

    st.subheader("Recommended Configuration:")
    best = st.session_state.opt_results
    st.success(f"**Optimal Number of Servers: {best['num_servers']}**")

    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Avg Wait Time", f"{best.get('avg_wait_time', 0):.3f}")
    res_col2.metric("Avg Queue Length", f"{best.get('avg_queue_length', 0):.3f}")
    res_col3.metric("Avg Server Utilization (%)", f"{best.get('avg_server_utilization', 0):.2f}%")
    # st.metric("Avg Total Served", f"{best.get('avg_total_served', 0):.1f}") # Throughput


if st.session_state.opt_comparison_df is not None:
     st.subheader("Optimization Comparison")
     st.write("Performance across different numbers of servers (averaged over replications):")
     st.dataframe(st.session_state.opt_comparison_df.style.format({
         "avg_wait_time": "{:.3f}",
         "avg_queue_length": "{:.3f}",
         "avg_server_utilization": "{:.2f}%",
         "avg_total_served": "{:.1f}"
     }))

     # Plot comparison
     st.line_chart(st.session_state.opt_comparison_df.set_index('num_servers')[['avg_wait_time', 'avg_queue_length']])
     st.line_chart(st.session_state.opt_comparison_df.set_index('num_servers')[['avg_server_utilization']])


# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.info("AIMS - Artificial Intelligence Making Sims")