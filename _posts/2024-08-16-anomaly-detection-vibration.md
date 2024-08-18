
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

   Machine learning (ML) techniques offer a more adaptable solution to track
   the health of a machine. The models used in ML can represent the machine's
   time- and frequency-data using latent (internal) variables, which provide
   an abstract view of the machine's internal behavior.
   This discussion will focus on unsupervised learning, as it can be applied
   to a broad range of applications, without the need for costly manual
   training.

   - **Latent Variables:**  
     In an autoencoder, for example, the ML model is trained to compress the
     vibration data (the STFT representation in our case) into a limited set
     of latent variables, essentially creating what some marketing materials
     might call a "digital twin."

   After training, these latent variables capture the subtle interactions
   between speed, load, temperature, and the time- and frequency-domain
   components of the input signal. Think of this as a much more sophisticated
   version of the relationship between load and temperature, but in multiple
   dimensions and with greater complexity.

   While the latent variables themselves don't give us clear insight in the
   machine's health status, they do provide the foundation for estimating how
   far the the machine's current behaviour deviates from its normal operating
   point. The normal state is defined by the complex patterens captured during
   the training phase. For example, if a harmonic signal appears (or disappears
   for that matter) in the input that wasn't present during the training, or if
   a specific combination of harmonics occurs, the latent variables won't be
   optimized to accurately represent this newfound state. As a result, the
   output of the autoencoder will start to diverge from the input.

   This discrepancy between the input and the model's output is measured by a
   loss function, for example the MAE (mean absolute error), which transforms
   it into a single numerical value: the loss or so-called "anomaly level" that
   indicates how far the machine is operating from its expected behavior.

   In the next chapter, we will return to our real-world example of the
   vibratory feeder. We'll start by examining the raw data to better understand
   the signal itself, then convert that data to its STFT representation and
   feed it into the autoencoder. By the end, we'll have a clearer understanding
   of what machine learning can offer beyond the "black mystery box" that it
   may appear to many people in the field of vibration analysis.

### Real-world Vibratory Feeder Data

   In this section, we will examine the data collected from a sensor placed on
   a vibratory feeder over several months. We'll track the progression of a
   bearing fault, exploring its appearance in the spectrum, and follow its
   development over time until the bearing was eventually replaced.

#### Time Domain Data

   // Insert comparison of time domain data before and after the fault appears

   Initially, the time domain data does not reveal much due to the presence of
   process noise. The fault's energy remains buried below the noise floor until
   the very late stages, when the fault's energy becomes high enough to rise
   above the process noise. As a result, relying solely on time-domain data or
   simple RMS energy thresholds is insufficient to detect early warning signs
   and track the stability of a developing fault.

#### Frequency Domain Data

   When we convert to the frequency domain, the picture becomes clearer. The
   energy components of the vibratory process are mainly concentrated at the
   lower frequencies, as expected. Additionally, the vibration dampers suppress
   higher frequencies associated with the product processing somewhat, making
   the upper half of the spectrum the ideal candidate to focus on for fault
   detection. 

   However, setting precise thresholds for each frequency bin as would be done
   with traditional monitoring approaches, remains a tedious challenge. Also,
   the intermodulation of the drive frequencies and harmonics with the actual
   fault frequencies may even cause certain spectral components to disappear,
   which is excactly the opposite from what setting a threshold is trying to
   achieve. Without expert knowledge about the machine characteristics, the
   risk for incorrect thresholds is real. This is where the autoencoder ML
   approach becomes a valuable asset in our toolbox.

#### Spectal Heatmap

   Before we review the ML results, we make an intermediate step and introduce
   the spectral heatmap. In this plot, the horizontal x-axis represents time,
   and the vertical slices (y-axis) represents the frequency spectrum of a
   single measurement. The amplitude of the spectrum is now represented by a
   color map, with dark blue indicating the lowest magnitude and yellow the
   highest peaks in the frequency spectrum.

   On this plot, we can observe that the gross of process noise is concentrated
   around the fundamental drive frequency and multiple odd harmonics thereof.
   The higher harmonics originate from the conversion process for the sinusoidal
   movement of the feeder, which is converted to nonlinear friction on the
   processed waste by the structure of the feeder topology (ref here).
   For the remainder of this discussion, we will ignore the lower part of the
   spectrum, as this portion of the heatmap mainly contains spectral components
   of the waste processing, and we are mostly interested to detect faults of
   the feeder components. However, it does not imply that the lower part of
   the spectrum is useless, as it may contain valueable information about the
   waste processing itself.

   In the upper part of the spectrum, we can observe some early stage signs
   of an upcoming change in the behaviour of the machine. First around x weeks
   before the actual damage of the bearing, then it disappears temperorarily
   because of planned revisions and about x days before the fatal damage it
   appears again. In the final stages of the bearing damage, we can see the
   fault spectrum spread out over all frequency bands, which is the well-known
   indicator stage 4 bearing damage.
   In the next chapter we will feed this sensor data to a ML autoencoder to
   reduce the complex data in a simple loss indicator which can be used as an
   temperature-like indicator for the health status of the machine.


### Autoencoder-Based Machine Health Prediction

In the final part of this discussion, we will demonstrate how an autoencoder can be used to predict the health status of a machine, without requiring any prior knowledge about its internal components.

#### STFT Representation and Input Data

Instead of feeding the autoencoder with time- or frequency-domain data separately, as discussed earlier, we use the STFT representation. Each measurement is converted into a numeric representation similar to the spectral heatmap described previously. However, in this case, the input data is extended to three dimensions:

- **Spectrum:** Frequency-domain data.
- **Sample Time:** Time between samples within the measurement (not to be confused with the time of measurement in the heatmap).
- **Measurement Sequence:** The sequence of measurements over time.

This complex, multi-feature input signal provides a rich dataset for the autoencoder to analyze. With some additional data augmentation (beyond the scope of this text), this dataset becomes the training input for the autoencoder.

#### Autoencoder Functionality

The autoencoder attempts to compress this 3D input signal into a reduced n-dimensional latent space. Once trained, the autoencoder reconstructs each new measurement and compares it with the original STFT input. The difference between the original and reconstructed signal is calculated using a loss function, which maps this discrepancy to a single numerical value—representing the anomaly score.

#### Anomaly Detection and Visualization

// Insert figure with the anomaly output of the autoencoder here

The output of the loss function clearly shows an increase in the anomaly score at the timestamps corresponding to the issues we visually detected in the heatmap from the previous chapter. The key advantage here is that this anomaly detection is done without needing to manually set individual thresholds for each frequency bin.

#### Thresholding and False Alarm Mitigation

Since we now have a useful indicator for the anomaly score, we can implement a simple, temperature-like threshold based on historical anomaly levels. To reduce the risk of false alarms, the output of the loss detector can be smoothed using a rolling window quantile estimator before being compared to the threshold level.

This approach allows us to define multiple confidence levels for the anomaly score, taking into account the past n measurements to reduce variance and avoid false alarms. This setup strikes a balance between response time and uncertainty, providing a more reliable indication of machine health.



#### STFT and ML Autoencoders

   In the final part of this discussion, we will use an autoencoder to predict
   the health status of the machine, without any a-priori knowledge about it's
   internal components.
   We could feed the autoencoder with time- or frequency domain data, but as
   discussed before, we use the STFT representation where each measurement is
   itself is converted to the numeric representation, similar to the above
   description of a spectral heatmap, but in this case we will have 3 dimensions:
   instead of only showing the spectrum in the heatmap, a third sample-time
   dimension is added to the input (not to be confused with the time of the
   measurement in the above heatmap).
   This complex multi-feature input signal is then used (with some data
   augmentation which is out of the scope of this text) as the training data
   for the autoencoder. The autoencoder will then try to compress the 3d input
   signal to a reduced n-dimensional latent space and compare each new
   measurement with the reconstructed STFT image at the input. The difference
   is then mapped to a single numerical value by the loss function as seen
   in figure x.

   // Here comes figure with the anomaly output of the autoencoder.

   The output of the loss function clearly shows an increase in the anomaly
   score at the correct timestamps we have visually detected in the heatmap
   of the previous chapter, without requiring us to set individual thresholds
   in the frequency output. Moreover, since we now have a useful indicator
   for the anomaly score, we can set a simple temperature-like threshold based
   on the historical levels of the anomaly level. To prevent false alarms,
   the output of the loss detector can the first fed into a rolling window
   quantile estimator before being compared to the threshold level. This way
   we can define multiple confidence levels to the anomaly score, which take
   into account the past n measurements to reduce the variance on the anomaly
   score and avoid false alarms (trade-off between response time and
   incertainty).


======
   In the time domain data there is not so much to see because of the process
   noise itself. Hence, the rms energy of the fault itself will be under the
   noise floor until the very late stages of the fault, where the energy of
   the fault emerges above the process noise.

   // then we go to the time domain before and after the fault appears.

   In the frequency data, we have more luck, as the energy components of the
   shaking process appear mostly at the lower frequencies. the dampers will
   also suppress higher frequencies of the product itself so as expected it
   is very useful to look at the upper half of the frequency spectrum. however,
   still it is not clear at all how to set the thresholds for each of the
   frequency bins as would be done in the traditional approach. Now, let's
   go to the STFT spectrum and plot all data in a single plot (of course,
   in a typical machine setup we dont have this data before a particular fault
   has occurred so keep that in mind.)

   // Here comes the STFT spectrum plot

   We explain here that the horizontal axis is time and the vertical axis
   is frequency from 0Hz to 1600Hz nyquist. The colormap represents the
   magnitude of the frequency component on that date, with dark blue the
   lowest and yellow the highest amplitude.

   On the STFT plot we can now see that most of the process noise is clearly
   limited to the fundamental drive frequency, which is converted to repeated
   discontinuous (nonlinear) friction on the waste by the structure of the
   feeder topology. (ref https://www.sciencedirect.com/science/article/abs/pii/S0263224117300416)
   This part of the spectrum is less interesting for us as it contains more
   information about the process itself than about the status of the drive motor,
   the bearings and the dampers. However this does not imply that this is useless
   data, as it is a totally valid use case to monitor the continuity of the
   waste processing itself over long time.

   So we focus on the upper part of the STFT spectrum.
   In the middle we see that the first anomaly appeared weeks before the actual
   problem, went away for some time (probably maintainance) and then reappeared
   at full strength before actual intervention and replacement of the bearing.
   After that, the machine reverts to normal operation. The reader may wonder
   why the oldschool setup with thresholds would not work here well, there
   was no information about the machine itself nor the type of faults that may
   appear. Here ML takes in a lot of data and declares that the standard operating
   condition. Any deviation from that would increase the loss indicator and
   trigger an alarm. Now that we have enough data, of course we could set
   thresholds for each bin but that would bring no additional extra info
   if we would not be able to determine the type of fault. Now we can begin
   labelling and start with supervised learning to pinpoint the actual fault
   to the failed component automatically but that is already far beyond what
   the client expected from the system.
   
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
