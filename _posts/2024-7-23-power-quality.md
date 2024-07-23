---
title: "Monitoring Power Quality in Industrial Compressors"
date: 2024-07-12
categories: blog
toc: true
toc_sticky: true
---

### Introduction
This tutorial covers the practical application of power and current monitoring
sensors to track the power quality of industrial compressors. We demonstrate
which parameters are crucial, such as the cosine phi (displacement power factor)
and the impact of harmonic distortion, providing a detailed insight into these
power quality metrics.

The ultimate goal is to predict potential failures, such as overheating, and
offer a gateway to the optimization of industrial equipment.

---

### Technical Background and Problem
Industrial compressors, especially high-power models like the 3-phase 200kW
compressor used in this case study, can cause power quality issues such as
harmonic distortion. In the upstream transformer cabin, the presence of
higher-order harmonics increases core losses due to eddy currents, resulting
in elevated transformer temperatures. Special K-factor transformers are used
to withstand these heating problems, but the heat losses persist.

Additionally, other equipment connected to the same power grid, such as small
electronic equipment power supplies or capacitor banks, may experience a higher
failure rate due to the stresses induced by the unexpected harmonic currents
oscillating between the 200kW compressor and the passive components in their
power supplies.

---

### Sensor Deployment and Capabilities
One of our clients asked to install a power quality monitoring system at the
entry point of one of their compressor rooms. The goal of this system is to get
better insight in both the cumulative energy consumption and the possible
infrastructure improvements learned from the captured sensor data.

For this, two sensors were deployed on the compressor room electrical supply:

1. **GridMate AG1 Power Quality Monitor:** This LoRaWAN-enabled sensor measures grid voltage, RMS current, peak current, cosine phi, true power factor, and distortion power on all three phases every 10 minutes. It provides detailed data essential for identifying transient events and high-frequency harmonics.

2. **Wireless Current Waveform Sensor:** Positioned on one of the phases, this sensor captures snapshots of the current waveform and its spectrum every 10 minutes. It delivers insights into the harmonic content and helps identify sources of distortion.

These sensors' high-frequency data collection and real-time analytics enable the early detection of potential issues, ensuring better energy management and maintenance strategies.

![Example of data output from the sensors]({{ site.baseurl }}/assets/images/data-output-sensors.svg)

---

### Detection and Analysis

#### Initial Findings
Within the first week, data from the GridMate AG1 revealed a high level of distortion power approximately 40 kVArd at 250 Hz for 200 kW of real power at 50 Hz. While the cosine phi was well-corrected at around 0.98, the distortion power highlighted potential risks for the capacitor banks and wiring.

#### Waveform Analysis
The current waveform sensor identified the distortion source as a 6-pulse 3-phase rectifier with a damping choke. According to ABB's technical guide on harmonics with AC drives, such rectifiers produce harmonic currents at multiples of the fundamental frequency (e.g., 5th harmonic at 250 Hz on a 50 Hz network).

![Waveform and spectrum analysis of the current]({{ site.baseurl }}/assets/images/waveform-spectrum-analysis.svg)

#### Technical Insight
- **Harmonic Content:** The 5th harmonic was notably significant, making up about 30% of the main component current in the spectrum plot. This detailed harmonic analysis is critical for understanding and mitigating power quality issues.

---

### Results and Benefits

#### Power Quality Insights
The sensors provided detailed insights into power consumption patterns, allowing for better energy management and cost savings. The phase compensation was confirmed to be effective, but the high distortion power was identified as an area of concern.

#### Predictive Maintenance
By regularly analyzing the current spectrum, the sensors enabled early detection of potential failures in the compressor's drive rectifier. This approach can significantly reduce downtime and maintenance costs.

#### Machine Learning Applications
Using machine learning, the sensors track the current waveform to detect small variations in the operating state. These variations can predict future failures, allowing for timely interventions and preventing costly standstills.

![Example of predictive analytics dashboard]({{ site.baseurl }}/assets/images/predictive-analytics-dashboard.svg)

#### Optimized Energy Use
Regular measurements and detailed data analysis helped the client optimize energy usage, leading to cost savings and improved operational efficiency.

![Picture of the installed equipment]({{ site.baseurl }}/assets/images/installed-equipment.svg)

---

### Conclusion
This case study demonstrates the capabilities of our sensor technology in addressing power quality issues in industrial settings. By providing detailed measurements and analysis, our sensors enable precise monitoring, better energy management, and predictive maintenance strategies, ultimately enhancing operational efficiency and reducing costs.

For more detailed technical insights and support, explore our [documentation](https://iqunet.com/resources/) and [case studies](https://iqunet.com/resources/case-studies/case-study-1-international-airport/), or contact our [support team](https://iqunet.com/contact/).
