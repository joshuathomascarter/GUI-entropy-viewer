# Hybrid Chaos Entropy Dashboard

**Live hybrid entropy dashboard for hazard-aware CPU pipelines — analog, ML, and digital signals unified in one UI.**

This repository contains a real-time monitoring dashboard designed to visualize the operational state and various hazard indicators within a conceptual CPU pipeline. It integrates simulated data from analog circuit analysis (LTSpice), a digital Finite State Machine (FSM), and machine learning predictions to provide a unified view of system health.

## Features

* **FSM State Monitoring:** Real-time display of the CPU pipeline's FSM state (OK, STALL, FLUSH, LOCK) with color-coded indicators.
* **Entropy Score Visualization:** Numeric and bar meter representation of the system's entropy score, reflecting disorder or uncertainty.
* **Override Source Indicator:** Clearly shows whether a state transition was triggered by ML predictions, analog overrides, or internal entropy logic.
* **Waveform Snapshot Viewer:** A placeholder panel intended to display live or captured waveform data from analog or digital simulations.
* **Entropy Classification Overlay:** Provides a real-time, simulated "Probability of STALL" based on the current entropy score, acting as a confidence metric for hazard prediction.

## Architecture Diagram

The dashboard operates as a visualization layer interacting with different simulation and conceptual components: