ORBIT

OS Real-time Behavioral Inspection Tool

📌 Project Overview

ORBIT is an Operating System–level malware detection system designed to identify malicious processes based on runtime behavior rather than static signatures.
The system continuously monitors process activity, builds behavioral baselines, detects anomalies in real time, and visualizes alerts through an interactive dashboard.

Unlike traditional antivirus solutions, ORBIT focuses on how a process behaves during execution, enabling detection of disguised or previously unknown malware.

🎯 Objectives

Monitor operating system processes in real time

Build normal behavior profiles for legitimate applications

Detect anomalous behavior at runtime

Classify suspicious and malicious processes

Provide a clear visual dashboard for analysis and response

🧠 Problem Addressed

Traditional malware detection systems rely heavily on known signatures and predefined rules.
Modern malware often disguises itself as legitimate processes and bypasses these mechanisms.

ORBIT addresses this gap by:

Observing runtime process behavior

Comparing activity against baseline behavioral profiles

Detecting threats even when binaries appear legitimate

🏗️ System Architecture (High Level)

ORBIT is designed using a layered modular architecture:

Monitoring Layer (Module 1)

Collects real-time OS process telemetry

CPU usage, memory usage, threads, system calls

Generates a live event stream

Behavior Profiling Layer (Module 2)

Builds baseline profiles from normal system behavior

Learns expected resource usage patterns

Analysis Layer (Module 3)

Computes anomaly scores

Applies security rules

Classifies processes as Clean / Suspicious / Malicious

Presentation & Control Layer (Module 4)

PyQt-based dashboard

Real-time visualization

Alerts, reports, and analyst actions

🧩 Modules Description
🔹 Module 1 – Real-Time Monitoring

Tracks live process behavior using OS-level telemetry

Produces normalized event logs for downstream analysis

🔹 Module 2 – Behavior Profiling

Learns baseline behavior of legitimate applications

Stores profiles for comparison during runtime

🔹 Module 3 – Anomaly Detection & Malware Identification

Calculates deviation scores based on CPU and memory usage

Applies rule-based logic for risk classification

Generates anomaly scores and detection results

🔹 Module 4 – Dashboard & Alerting

Central UI for ORBIT

Displays active processes, risk levels, alerts

Supports:

Real-time monitoring

Benchmark (baseline) scanning

Incident reporting

⚙️ Technologies Used
Software

Python 3.10+

PyQt5 – GUI and dashboard

psutil – OS process monitoring

JSON – Data storage and profiling

Git & GitHub – Version control

Hardware Requirements

Processor: Dual-core or higher

RAM: Minimum 4 GB (8 GB recommended)

Storage: 1–2 GB free disk space

🚀 How to Run

From the project root:

python -m module4.main


The application launches from a single entry point as required.

📊 Key Features

Real-time behavioral monitoring

Baseline vs live behavior comparison

Anomaly scoring

Malware classification

Interactive SOC-style dashboard

Modular and extensible design

📈 Performance Considerations

Lightweight monitoring with configurable sampling intervals

Real-time detection without blocking system execution

Designed for academic and prototype-level evaluation

🔮 Future Enhancements

Kernel-level system call tracing

Machine learning–based anomaly detection

Network traffic correlation

Automated response actions

Cloud-based telemetry aggregation

👥 Team Structure

Module 1: Real-Time Monitoring

Module 2: Behavior Profiling

Module 3: Detection & Risk Analysis

Module 4: Dashboard & Alerting
