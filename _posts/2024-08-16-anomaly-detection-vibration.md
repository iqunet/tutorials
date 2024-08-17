
---
title: "Real-Time Anomaly Detection in Industrial Shaker Machines Using Wireless Vibration Sensors and Machine Learning"
date: 2024-XX-XX
categories: blog
toc: true
toc_sticky: true
---

### Introduction
Waste management plants rely on serial processing lines where failures cause
significant capacity loss due to limited redundancy. This makes some level of
predictive maintainance monitoring critical to prevent unplanned downtime.

While digital PLCs are in the control of the pipeline, machine manufacturers
treat health monitoring mostly as an afterthought, leaving it to the customers
to handle failures. In unhealthy environments filled with dust, humidity, and
noise, daily manual inspections are not practical.

In this blogpost, we will explore how ruggedized wireless vibration sensors
and machine learning provide regular health updates, enabling early detection
of issues. We shall cover the technical setup, the data processing, and the
machine learning which automate the anomaly detection in noisy environments.
Noisy, in this case, refers to the sensor signal, which is polluted with
unwanted vibrations from the production process itself, in addition to the
machine defects we are trying to detect here.

---

### Challenges in Monitoring Shaker Machines

Monitoring vibrating equipment in waste management plants is not straightforward
for the following reasons. The facilities are large, and traditional monitoring
systems are often not in place. Installing cabling across the site is not only
expensive but also impractical, because the machines most prone to breakage
experience large vibrations during operation.

A good example is vibratory feeders, which play a role in spreading the material
before optical sorting. These machines face several challenges:

- **Large Displacements:** Vibratory feeders experience displacements of up to
10 cm, making wired sensors vulnerable to wear and failure both in the connector
and in the wire itself.

- **Regular Maintenance:** When parts of the machine are disassembled for
maintainance, any sensor installation would be part of the handling. However,
we want the sensors to be as non-intrusive as possible while maintaining a
consistent location and orientation. This makes the machine learning algorithms
more sensitive as discussed later.

Due to these challenges, the customer has opted for wireless sensors. However,
these sensors are installed 40 cm away from the ideal location, on the machine
frame instead of the motor/drive train. While this evidently reduces sensitivity
for high-frequency bearing faults, this ensures consistent operation of the
sensors over a long period.

Other factors also must be taken into account:

- **Signal Propagation:** Due to the placement of the sensor, there are multiple
material boundaries which would attenuate/reflect high-frequency signals. For
this reason, measurements of >10KHz up to the ultrasonic spectrum would not only
be costly but also provide very marginal advantages.
- **Unsuitability of RMS:** Due to the amount of processing noise, simple RMS
sensors will see the fault signals simply be covered by the process noise itself.

For this reason, triaxial MEMS-based wireless vibration sensors are ideal:

- **Frequency Response:** capture vibrations up to 1600 Hz in 3 axes, which
allows to separate process noise from the fault detection, which increases the
SNR and the sensitivity.
- **Robustness:** MEMS sensors are highly durable and well-suited for long-term
use in harsh environments.
- **Wireless:** With a range of 20 to 50 meters, these sensors eliminate the
need for fragile and expensive cabling.

In the next chapters, we will discuss how the sensors data is processed and
used to align unplanned downtime to the scheduled maintainance, effectively
eliminating costly standstills.

---

### Sensor Setup and Data Collection
Detail the technical setup of the wireless vibration sensors. Discuss the sensor specs, sampling rate, and the practical limitations of sensor placement on large shaker machines.

- Sensor type: 3-axis MEMS vibration sensors.
- Sampling rate and interval: 3200Hz sampling rate with a 15-minute interval.
- Data collection: Mention the 25k data points per measurement and how they are transmitted to a central receiver.

---

### Advanced Data Analysis: Spectral and Temporal Insights
Explain the importance of both spectral and temporal data in detecting anomalies. Dive into the specifics of using STFT plots to capture short, impactful events that might go unnoticed in traditional spectral analysis.

- Spectral plots: Their role in monitoring frequency components.
- STFT plots: How they help detect short, temporal events like clicks or peaks.
- Real-world benefits: Mention that this combination allows for more accurate and comprehensive monitoring of machines beyond just spectral data.

---

### Machine Learning for Anomaly Detection
Discuss how the STFT data is fed into an ML autoencoder for anomaly detection. Explain how this process works, what an anomaly score represents, and how it simplifies complex vibration data into actionable insights.

- Autoencoder explanation: Briefly explain how the ML model learns from previous data and flags deviations.
- Anomaly score: Describe how it quantifies deviations and what the scores mean for operational decisions.
- ML advantages: The system is easy for non-experts to use, similar to reading a simple dial, yet powerful enough to detect complex issues.

---

### Broader Applications Beyond Shaker Machines
Expand on how this technology can be applied to other types of industrial machinery with similar challenges. Mention examples like pumps experiencing cavitation or homogenizers with high background noise.

- Flexibility of ML models: Discuss how the same approach can be adapted to different machines and processes.
- Avoiding overfitting: Touch on the importance of correctly configuring the ML model for diverse applications.

---

### Dashboard and Integration with Other Systems
Explain how the collected data and anomaly scores can be integrated into higher-level systems like OPC UA or MQTT for automated reporting. Also, mention how smaller companies can use the iQunet system as a stand-alone platform for monitoring and analysis.

- Data integration: Mention how the data can be sent to higher-level platforms.
- Customizable dashboards: Discuss the iQunet dashboard capabilities for displaying trends, spectral plots, and anomaly data in a user-friendly way.

---

### Conclusion
Summarize the key takeaways of the post. Highlight the benefits of using wireless sensors combined with machine learning to detect anomalies in real-time. Emphasize how this approach can prevent costly downtime and improve the efficiency of industrial processes.

- Recap the advantages of real-time monitoring with ML.
- Future potential: Mention possible advancements or future applications.
