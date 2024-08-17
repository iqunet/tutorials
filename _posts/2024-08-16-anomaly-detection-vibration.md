
---
title: "Real-Time Anomaly Detection in Industrial Shaker Machines Using Wireless Vibration Sensors and Machine Learning"
date: 2024-XX-XX
categories: blog
toc: true
toc_sticky: true
published: false
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

The MEMS-based wireless vibration sensors provide detailed, day-to-day insights
into machine behavior. Each sensor captures three-axis vibration snapshots every
15 minutes (or at a configurable interval) at a sampling rate of 3200 Hz (also
configurable). A measurement, consisting of 25,000 samples, is wirelessly
transmitted to a central edge server equipped with an embedded historian database.

The system includes a TensorFlow inference processor for machine learning, along
with a customizable dashboard, making it a complete standalone solution. For
compatibility with third-party applications, the platform also includes an
OPC-UA server and MQTT publishing client, enabling real-time visualization on
modern SCADA platforms (Kepware, Ignition, Siemens SIMATIC, etc.).


#### Data Processing: From Raw Data to Actionable Insights

The raw data is first prefiltered to remove DC components from the signal. From
there on, several separate streams of processed data are generated, such as
acceleration, velocity and rms values. The data is also transformed to spectral
plots, which allows us to observe fault patterns and irregulatities in the
the frequency domain. While the time domain is useful to detect short impacts
or peaks, such information in not visible in the frequency domain. In addition,
making the link between the actual fault pattern and the machine component
often requires expert-level knowledge (both about for example bearing faults
and the specifics of the machine) and regular investigation of the measurement
data. Such experts are quite expensive and therefore the inspection interval
is too large to catch random machine faults.
Given that hundreds of these plots are generated each day, manual analysis
becomes impractical. For this purpose, we must rely on automated fault detection
techniques. Accepted ways for this automated systems
are for example frequency binning and setting thresholds for each bin based on
which alarms can be generated. Again, this requires careful knowledge of the
internals of the machine and is mostly used for equipment which operates under
constant speed and loads. When this comfort zone is left behind, and we are
talking about unknown interals, variable speed drives, varying loads and process
noise, these somewhat dated techniques start to fall apart.
Enter the fairly recent field op deep learning and machine learning techniques,
where we can train mathematical models to represent the time and frequency
data from the sensor in so-called latent variables. Latent variables can be
seen as an abstracted representation of a machine's behaviour. For example,
in the autoencoder (one ot the types of ML), we train the model to represent
the machine's time- and frequency domain data with a limited set of latent
variables. In more understandable terms, a STFT representation is first generated
which is a combination of both the time and frequency representation of the
sensor data, just transformed to another domain. The STFT allows us to detect
both wideband anomalies (think short clicks or sudden events) and also
anomalies in the spectrum. For the shaker for example imbalance due to worn out
dampers will cause even harmonics to appear. Anyways this is not relevant here
It contains the same data as the raw sensor data, only transformed to another
orthogonal domain. This is the input of the machine learning thing. Then, we
force the ML algorithm to abstract the machine's behaviour in a few variables.
Think about, when the machine is running under x load and x speed, I expect to
see a pattern of these frequencies with these relative amplitudes. By training
the model on all types of real-world data, temperature, loads, the model can
represent a much more complex representation (marketing term digital twin) of
the actual machine than a human being can do. When a certain fault appears, for
example imbalance or a bearing fault which suddenly causes a frequency component
to appear (or even disappear under certain conditions!), the trained model will
suddenly start to deviate from the data that we had trained on before. This
deviation, called the loss function in expert terms, is a number (or even an
output which indicates a particular fault if trained for this matter), which can
be used to indicate how far the machine is operating from any normal condition
that it was trained before. Think like just a temperature gauge, but instead
of degrees celcius, we have a number that represents the "anomaly level"
(loss function). If we plot this number over time, even for an untrained
personnel this can be grasped that something is off with the machine and
closer inspection is needed. Also, since we have collapsed the 25.000 point
measurement data in a single number now, we can easily set a threshold to 
generate some kind of alarm upstream in the SCADA system. Since this system
runs 24/7 in case of the waste production plant we can early detect emerging
faults, order replacement parts and have everything ready for the next
planned maintainance.


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
