Requirements for the **AIMS Basic Queue Modeler (Version 1.0)**. This list aims to be specific enough for the AIMS AI agents to begin the design, development, and optimization process autonomously.

**1. Product Goal:**

* To provide users with a simple, web-based tool to model and optimize basic single-queue, multiple-server queuing systems.
* To showcase AIMS's capability to autonomously design, develop, and optimize simulation models based on user inputs and goals.

**2. Core User Roles:**

* **Basic User:** Defines system parameters, runs simulations, views results.
* **Optimizer User:** Defines optimization goals and lets the AI find optimal parameters.

**3. Functional Requirements:**

    **3.1. User Interface (UI) & User Experience (UX):**
        * FR-UI-01: The application shall provide a clean, intuitive web-based interface.
        * FR-UI-02: The interface shall be divided into logical sections: Input Parameters, Simulation Control, Optimization Goals (Optional), and Results Display.
        * FR-UI-03: Input fields shall have clear labels and provide tooltips or help text explaining the parameter.
        * FR-UI-04: Provide sensible default values for all input parameters.
        * FR-UI-05: Visual feedback shall be provided during simulation runs and optimization processes (e.g., progress bar, status indicator).

    **3.2. Input Parameters:**
        * FR-IN-01: User must be able to define the **Arrival Process**:
            * Select distribution type: [Must: Exponential Inter-arrival (Poisson Process), Constant Rate]. [Should: Allow specifying fixed inter-arrival time].
            * Specify parameters (e.g., Average Arrival Rate λ). Input units should be clear (e.g., customers per hour).
        * FR-IN-02: User must be able to define the **Service Process**:
            * Select distribution type: [Must: Exponential, Constant]. [Should: Normal (specify mean and std dev)].
            * Specify parameters (e.g., Average Service Rate μ or Average Service Time 1/μ). Input units should be clear (e.g., customers per hour or minutes per customer).
        * FR-IN-03: User must be able to define the **Number of Servers** (Identical parallel servers). Input must be a positive integer.
        * FR-IN-04: User must be able to define the **Simulation Stopping Condition**:
            * Select condition: [Must: Run for a specific simulated time duration, Process a specific number of customers].
            * Specify value for the chosen condition (e.g., 480 simulated minutes, 1000 customers).
        * FR-IN-05: [Should] User should be able to set a **Random Number Seed** for reproducibility. If not set, use a default or time-based seed.

    **3.3. Simulation Core Logic (To be autonomously generated/managed by AIMS AI):**
        * FR-SIM-01: Implement a discrete-event simulation engine.
        * FR-SIM-02: Generate customer arrivals according to the specified arrival process and parameters.
        * FR-SIM-03: Manage a single queue with **FIFO (First-In, First-Out)** discipline.
        * FR-SIM-04: Assign arriving customers to the first available idle server. If all servers are busy, customer joins the queue.
        * FR-SIM-05: Simulate service times for each customer according to the specified service process and parameters.
        * FR-SIM-06: Track server status (idle/busy).
        * FR-SIM-07: Collect key performance indicators (KPIs) during the simulation run.
        * FR-SIM-08: Handle simulation start, stop, and reset based on user controls and defined stopping conditions.
        * FR-SIM-09: Ensure proper use of the specified random number seed for all stochastic elements (arrivals, service times).

    **3.4. Simulation Control:**
        * FR-CTRL-01: Provide buttons to 'Run Simulation', 'Stop Simulation', 'Reset Parameters'.

    **3.5. Output & Results Display:**
        * FR-OUT-01: After a simulation run completes, display summary statistics:
            * [Must] Average Waiting Time in Queue
            * [Must] Maximum Waiting Time in Queue
            * [Must] Average Queue Length
            * [Must] Maximum Queue Length
            * [Must] Average Server Utilization (percentage)
            * [Must] Total Number of Customers Served (Throughput)
            * [Should] Average Time in System (Wait + Service)
            * [Should] Standard Deviation of Waiting Time
        * FR-OUT-02: [Should] Provide basic visualizations:
            * A chart showing queue length over simulated time.
            * A histogram showing the distribution of customer waiting times.
        * FR-OUT-03: [Could] Provide a simple, real-time animation visualizing customers arriving, queuing, and being served.

    **3.6. AI Optimization Engine (Core AIMS Feature):**
        * FR-AI-01: Provide an interface section for defining optimization goals.
        * FR-AI-02: User must be able to select an optimization **Objective**:
            * [Must] Minimize Average Waiting Time.
            * [Must] Maximize Throughput (given constraints).
            * [Must] Minimize Number of Servers (subject to constraints).
        * FR-AI-03: User must be able to define **Constraints** relevant to the objective (e.g., "Keep average server utilization below 90%", "Keep average wait time below 5 minutes", "Achieve a service level of 95% customers waiting less than X minutes").
        * FR-AI-04: The AIMS AI agent shall identify the **Optimization Parameter Space**. For V1.0, this MUST be limited to the **Number of Servers**.
        * FR-AI-05: The AIMS AI agent shall autonomously **design and execute an optimization strategy** (e.g., iterative simulation runs, search algorithms) by varying the Number of Servers within a reasonable range.
        * FR-AI-06: The AI agent must run multiple simulation replications for each parameter set being tested to account for stochastic variability.
        * FR-AI-07: Provide clear feedback on the optimization process progress.
        * FR-AI-08: Upon completion, the AI agent shall present the **Recommended Configuration** (optimal Number of Servers) and its corresponding performance metrics based on the user's objective and constraints.
        * FR-AI-09: [Should] Display a comparison of the tested configurations and their performance against the optimization goal.

**4. Non-Functional Requirements:**

* **NFR-PERF-01:** Single simulation runs for typical parameters (e.g., <20 servers, <5000 customers) should complete within 60 seconds.
* **NFR-PERF-02:** Optimization runs should provide progress updates and complete within a reasonable timeframe (e.g., a few minutes for the V1 scope).
* **NFR-USAB-01:** The interface must be usable by individuals with basic knowledge of queuing concepts but potentially no simulation software experience.
* **NFR-REL-01:** The simulation must produce statistically valid and reproducible results (given the same inputs and random seed).
* **NFR-REL-02:** The application should handle invalid user inputs gracefully (e.g., non-positive numbers for rates/servers) with clear error messages.
* **NFR-SEC-01:** As a web application, basic security practices should be followed (though no sensitive PII is stored in V1).
* **NFR-MAINT-01:** The code and models generated by the AIMS AI should adhere to defined internal quality/style standards to facilitate potential debugging or future extensions.

**5. AI's Role Explicit Summary:**

* **Design/Develop:** Autonomously generates the underlying discrete-event simulation model code, the queuing logic, data collectors, and potentially basic visualization components based on user parameter choices.
* **Optimize:** Autonomously understands the user's optimization goal, defines the search space (number of servers), executes multiple simulation runs varying the parameter, analyzes results, and recommends the optimal configuration.

This requirements list provides a solid foundation for the AIMS AI agents to build the Basic Queue Modeler V1.0.