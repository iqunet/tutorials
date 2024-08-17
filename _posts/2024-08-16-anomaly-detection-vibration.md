
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
So, having set the image of the environment, let's focus on the sorting machines.
The sorting machines are in multiple purposes and sizes, but one example is
a vibratory feeder followed by and optical sorter.
The vibratory feeder is basically a big shaker table driven by an eccentric
link with counterweight to balance and minimize the load on the bearings. At
the non-driven side the machine is attached to mechanical anti-vibration dampers
which absorb the energy that would otherwise directly be transferred to the
mounting points of the machine. The vibratory feeder will spread the material
as much as possible for the optical sorter, which then
separates on material types with the help of compressed air to alter the
direction of the material towards multiple output flows.
The best solution would be to place a wired piezo accerelometer as close to
the bearing as possible. However, this is where we meet reality, as the large
displacements of the feeder (order of 10cm) makes any wiring and contacts
prone to extreme wear and failure, especially over a long time of continuous
operation. Secondly, due to the regular maintainance intervals where part of
the drive end are disassembled and removed for maintainance, the sensor would
also have to be removed and installed multiple times over the lifetime of the
DUT, which makes it prone to human error, such as differences in installed
orientation etc. For this reason, it was preferred by the customer itself to
install the sensor as far as 40cm away from the ideal location, on the carrier
construction rather than on the drive train. This, of course, drastically
reduces the sensitivity of the system, where the ultrasonic measurements are
useless because of the multiple boundaries between materials that reflect and
attenuate these signals. On the other hand RMS sensors are on the other end
of the spectrum because they throw away all middle ground information. For
this reason, a triax MEMS-based wireless vibration sensor is the perfect fit,
not only because of the frequency band up to 1600Hz, but also because of their
excellent robustness against failure (piezo sensors must be handle carfully
because of cracks in their ceramic material renders them useless)
Still the sensors allow to easily select the most sensitive axis for anomaly
detection, and also allow to be selective on the frequency spectrum to
separate the noise of the production process from the actual faults, thus
increasing the detection period.
The goal of the customer is here to be able to detect and align the replacement
of worn out parts with the already planned standstill maintainence interval,
thus reducing excess unplanned outages to practically zero time.
A last thing is that the wireless sensors have a range between 20 and 50 meters,
totally avoiding the cabling cost in expense of the delay between two measurements
of course. For most practical applications that are not critical systems which
require immediate shutdown as is the case here, this makes the difference between
monitoring or just no monitoring at all.




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
