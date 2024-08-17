
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

### Monitoring Shaker Machines

Monitoring vibrating equipment in waste management plants presents it's own
challenges:

- **Facility Size:** These plants are large, and infrastructure for monitoring
systems is often not in place. Installing cabling across the site is not only
hindering expensive but also impractical, particularly for machines that
experience significant vibrations during operation.

One example is vibratory feeders, which spread household waste material before
it undergoes optical sorting. In the optical sorter, spectral cameras detect
different materials, and pressurized air is then used to separate individual
pieces of waste into different output flows. These vibratory feeders, which
ensure the even distribution of material, face several challenges:

- **Large Displacements:** Vibratory feeders experience displacements of up to
10 cm, making not only themselves prone to considerable wear but also make wired
sensors susceptible to both connector and cable failure.
  
- **Regular Maintenance:** Parts of these machine are frequently disassembled
for maintenance. It is preferred that any sensors should be as non-intrusive as
possible while also maintaining consistent location and orientation. This
stability improves the accuracy of the machine learning algorithms, as discussed
later in this post.

Due to these challenges, the customer opted for wireless sensors. In addition,
the sensors were installed 40 cm away from the ideal location, on the machine
frame instead of the motor and drive train. While this placement severely
reduces sensitivity to high-frequency bearing faults, it ensures that the
sensors generate consistant data over a long period, as they are excluded from
any part exchanges during repairs.

Other factors that need to be considered include:

- **Signal Propagation:** The sensor's placement introduces multiple material
boundaries, which attenuate and reflect high-frequency signals. This makes
measurements above 10 kHz, including ultrasonic frequencies, costly and of
limited benefit.
  
- **Unsuitability of RMS Sensors:** The amount of process noise means that
simple RMS sensors would likely mask fault signals, making them ineffective
for vibratory feeders, except for the most obvious (catastrophic) failure modes.

Given these conditions, triaxial MEMS-based wireless vibration sensors are an
ideal choice:

- **Frequency Response:** These sensors capture vibrations up to 1600 Hz in
three axes, allowing for better separation of process noise from fault detection,
allowing to tune the signal-to-noise ratio and overall sensitivity.
  
- **Robustness:** MEMS sensors are highly durable and well-suited for long-term
use in harsh environments. Piezo accelerometers are not prone to material
failures of the ceramic sensing elements and need careful handling to keep their
calibrated sensitivity.
  
- **Wireless Range:** With a range of 20 to 50 meters, wireless sensors
eliminate the need for fragile and expensive cabling. Downside is the need for
battery replacement every 20-50,000 spectral measurements.

In the following chapters, we will discuss how the sensor data is post-processed
and used to align otherwise unplanned downtime with scheduled maintenance tasks,
effectively reducing standstills to virtually 0 excess downtime.

---

### Sensor Data Processing and Machine Learning

The MEMS-based wireless vibration sensors provide detailed, day-by-day insights
into machine behavior. Each sensor captures three-axis vibration snapshots every
15 minutes (or at a configurable interval) at a sampling rate of 3200 Hz (also
configurable). Each measurement, consisting of 25,000 samples, is wirelessly
transmitted to a central edge server.

Depending on the capture settings and environment, the battery lifetime is
around 20-50,000 measurements. A battery replacement takes less than a minute.

The edge server is equipped with an embedded historian database. Up to 25GB or
historical data is retained, which corresponds to multiple years of accumulated
sensor data.
The embedded software includes a TensorFlow inference processor for machine
learning models, along with a customizable web-based dashboard, making it a
complete offline standalone solution, suitable for displaying in kiosk mode and
providing condense information for the plant operator/engineer.

For compatibility with external systems, the platform also features an OPC-UA
server and MQTT publishing client, enabling real-time data export to third-party
tools.

#### Data Processing: From Raw Data to Actionable Insights

The raw data is first used to generate spectral plots, which display the frequency components of the vibration signals. These spectral plots allow us to observe patterns in the frequency domain and identify any irregularities. However, spectral analysis alone is insufficient to capture every anomaly. For instance, short impacts or peaks in the time domain signal can be missed, as they often spread across a wide frequency band and are difficult to detect in the spectrum.

To address this, Short-Time Fourier Transform (STFT) plots are also generated. The STFT provides a time-frequency representation of the signal, allowing us to detect both spectral and temporal events. This combination is critical for identifying subtle anomalies that could indicate emerging issues, even when they aren’t immediately obvious in the spectral data.

Given that hundreds of these plots are generated each day, manual analysis becomes impractical. This is where machine learning steps in to automate the process.

#### Machine Learning for Anomaly Detection

The STFT data is fed into a machine learning model, specifically an autoencoder, which has been trained on previously captured data. The autoencoder learns the normal operating patterns of the machine and generates an anomaly score based on how well the current data matches the learned patterns.

The advantage of using this approach is that it can detect a variety of anomalies:

- **Emerging Faults:** A frequency component that suddenly appears is flagged as an anomaly.
- **Disappearing or Shifting Frequencies:** A frequency component that vanishes or shifts can also indicate an issue, even though this might decrease the overall RMS value.

The ML model accounts for variability due to temperature, speed, and load, making it robust enough to adapt to changing operating conditions. The result is an anomaly score that quantifies the deviation from the machine’s nominal operating point.

#### Simplifying Complex Data for Decision-Makers

Not every operator is a vibration expert, and in busy industrial environments, complex data needs to be presented in a simple, actionable format. The output of the autoencoder is distilled into an easy-to-understand metric. 

- **Anomaly Score:** This single number represents the degree of deviation. A stable but elevated score suggests that the fault is present but not worsening. However, a rising anomaly score signals that immediate action may be required to prevent a failure.

This data can be integrated into higher-level platforms using OPC UA or MQTT for automated reporting, enabling operators to respond in a timely manner.

#### Broader Applications Beyond Shaker Machines

This machine learning-based approach is versatile and can be applied to other types of equipment with complex operating conditions. For example, cavitation in pumps or noise in homogenizers can be detected by the same methodology. The autoencoder learns the machine’s normal behavior without needing supervised training, allowing it to identify both known and unknown failure modes.










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
