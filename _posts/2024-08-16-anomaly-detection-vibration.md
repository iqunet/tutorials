
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

### Data Processing: From Raw Data to Actionable Insights

The raw data collected by the sensors undergoes several processing steps to
extract several aggregate parameters and complex parameters.

#### Prefiltering, Data Streams and Domains

1. **Prefiltering:**  
   Certain types of piezo sensors can generate high dynamic range velocity
   signals at very low frequencies using a charge amplifier. However, MEMS
   sensor data is acceleration based and must be prefiltered to remove any
   near-DC components before the conversion to velocity. This is a
   non-straighforward mathematical process similar to the stabilization time
   in piezo sensors, and it must be ensured that the high rejection ratio
   linear-phase filter does not introduce ripple near the LPF cut-off frequency,
   which would cause severe drift when integrating from acceleration to velocity.
   
2. **Data Streams:**  
   Once the DC-offset is removed, the data is converted into several useful
   streams in the edge server, including:
   - **Acceleration**
   - **Velocity**
   - **RMS values**
   - **Kurtosis**
   - **Time domain view**
   - **Frequency domain**
   
   These are the basic tools used by vibration experts to determine the state
   of the machine, and in more advance cases, also the origin of the fault,
   such as a loose mount or a bearing fault. Other tools exist that will
   further postprocess the signal, such as enveloping demodulation, but they
   are mostly focused towards representing the data in a format which is
   easily understandable by the human eye. We will ignore these cases since
   this blogpost is focused towards the automated detection of faults using
   machine learning techniques.

3. **Spectral Plots:**  
   Why do we use both the time and frequency domains? Although they represent
   the same underlying data, each domain has unique advantages when it comes to
   detecting specific signal patterns. For instance, one-time transient events
   in the signal (e.g. a mechanical shock) are easily identified in the time
   domain, where their energy is concentrated in a short interval. However, in
   the frequency domain, these events merely appear as a slight increase in the
   noise floor, making them difficult to detect, both for humans and automated
   systems.

   The above consideration is crucial for understanding why we use the
   Short-Time Fourier Transform (STFT) when feeding data into the machine
   learning algorithm. The STFT allows us to represent the sensor signal in
   both the time- and frequency-domain simultaneously. By doing so, we capture
   all relevant information (for the sake of simplicity, we exclude phase
   information here) and ensure that the signal power of various fault patterns,
   whether time-based or frequency-based, remains concentrated and is more
   easily detected.

   While is very doable for a machine learning algorithm to perform domain
   transforms internally, this approach would require a significant portion of
   the model structure (specifically, the convolutional layers) to handle these
   transformations. This would unnecessarily complicate the training phase
   as it would also take considerable time to tune the ML model parameters to
   'reinvent' these transforms. By using the STFT as a fixed preprocessing step,
   we effectively offload this task and provide the ML algorithm with a rich
   input that combines the strengths of both domains. In this sense, the STFT
   acts as a pre-trained, fixed component of the machine learning model itself,
   simplifying the detection process and reducing the training cost.

#### Challenges with Manual Analysis and Traditional Methods

   Linking specific fault patterns to particular machine components typically
   requires expert knowledge. Diagnosing issues like bearing faults or other
   machine-specific anomalies demands experience and regular inspections.
   However, relying solely on specialists is costly, and the extended intervals
   between inspections can result in missed random faults.

   Moreover, the sheer volume of data --hundreds of plots generated daily-- 
   makes manual analysis impractical. Traditional automated methods, such as
   frequency binning and manually setting thresholds for each bin, are widely
   accepted but come with inherent limitations:

   - **Dependency on Expertise:** Setting accurate thresholds requires good
     understanding of the machine's internals.

   - **Operating point variability:** Traditional threshold-based methods are
     most effective when machines operate under constant speeds and loads. In
     environments with varying conditions, thresholds often need to be relaxed
     to avoid false positives, which significantly reduces the sensitivity of
     the monitoring system.

#### Enter the Power of Machine Learning

Machine learning (ML) techniques offer a more adaptable solution. These models can represent the machine’s time and frequency data using latent variables, which provide a more abstract yet comprehensive view of the machine’s behavior.

- **Latent Variables:**  
  In autoencoder models, for example, the system is trained to distill the machine’s vibration data into a limited set of latent variables, which encapsulate its typical behavior.

- **STFT (Short-Time Fourier Transform):**  
  The sensor data is first transformed using the STFT, which combines time and frequency domain information. This approach enables the detection of both:
  - **Wideband Anomalies:** Sudden clicks or impacts.
  - **Spectral Anomalies:** Changes in frequency components, such as those caused by imbalances or wear.

By training the model on real-world data—across varying temperatures, loads, and conditions—the ML model develops a more comprehensive understanding of the machine’s expected behavior, effectively creating a "digital twin."

#### Turning Detection into Actionable Insights

When faults arise, such as imbalances or bearing issues, the ML model detects deviations from the normal patterns it has learned. These deviations are quantified through a loss function, producing an anomaly score that indicates how far the machine’s current operation deviates from its expected performance.

- **Simplified Metric:**  
  The anomaly score serves as a straightforward "health indicator" for the machine. Similar to a temperature gauge, this score gives a numerical value representing the machine's condition. Even non-experts can track this number over time to identify when something seems off.

- **Thresholds and Alarms:**  
  Since the model condenses 25,000 data points into a single anomaly score, it’s easy to set thresholds that trigger alarms in the SCADA system. This real-time monitoring allows operators to detect emerging issues early, order replacement parts, and plan repairs during scheduled maintenance, minimizing unexpected downtime.


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
