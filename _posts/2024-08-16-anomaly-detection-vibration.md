---
title: "Anomaly Detection Using MEMS Vibration Sensors and Machine Learning"
date: 2024-08-18
categories: blog
toc: true
toc_sticky: true
published: true
---

### Scope and TL;DR
This blog post explores how wireless vibration sensors and machine learning
techniques are used for anomaly detection in industrial shaker machines. By
monitoring vibration data and using deep-learning models, various types of
mechanical faults can be detected at an early stage. We cover the technical
setup and data postprocessing using autoencoders, which are the key elements
for reliable and fully automated fault detection.

Based on real-world data from a household waste processing plant in the Benelux,
this post examines both the strengths and weaknesses of the system. It is
targeted at both the vibration expert and the casual reader interested in
gaining better insight in the practical applications of machine learning,
beyond the hype that has surrounded it in recent years.

### Introduction
Waste management plants rely on long serial processing lines. Failures in any
pivotal stage may cause severe capacity loss due to the limited redundancy. This
makes some level of monitoring targeted towards machine health and predictive
maintainance crucial to avoid unplanned downtimes and the cost that inevitably
comes with it.

While digital PLCs are in the control of the pipeline and can already detect
the most acute faults in realtime, machine manufacturers treat health monitoring
mostly as an afterthought, leaving it to the customers to handle unexpected
random failures. However, in unhealthy environments filled with dust, humidity,
and noise, daily manual inspections are not practical.

In this blogpost, we will explore how ruggedized wireless vibration sensors
and machine learning in the data postprocessing chain provide us with consistent
regular health updates, enabling early detection of issues. We shall cover the
technical setup, the data processing, and the machine learning which automate
the anomaly detection in noisy environments. Noisy, in this case, refers to
the sensor signal, which is polluted with unwanted vibrations from the
production process itself, in addition to the machine defects we are trying to
detect here.

---

### Monitoring Shaker Machines

Monitoring vibrating equipment in waste management plants presents unique
challenges. These plants are large, and network infrastructure is often
lacking. Installing cabling across such large sites is not only expensive but
also impractical. This is especially true for machines that experience
significant vibrations during operation.

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

Given the challenges of monitoring shaker machines, the customer opted for
wireless sensors to avoid issues related to cable and connector fatigue.
In addition, to ensure that regular maintenance tasks could be performed
without disturbing the sensors, they were installed 40 cm away from the ideal
location. This placement on the machine frame, rather than directly on the
motor and drive train, reduces the sensitivity to high-frequency bearing faults
but ensures consistent data collection over a long period, even after part
replacements.

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

In the final part of this discussion, we will demonstrate with real-world data
how the autoencoder was used to successfully predict the health status of the
vibratory feeder, without requiring any a-priori knowledge about its internal
components.

#### STFT Representation and Input Data

Instead of feeding the autoencoder with time- or frequency-domain data
separately, as discussed earlier, we use the STFT representation. Each
measurement is converted into a numeric representation similar to the spectral
heatmap described previously. However, in this case, the input data is extended
to three dimensions.

- **Time domain:** Time between 3x8192 samples within the measurement
- **Spectrum:** Frequency-domain data of above time domain.
- **Measurement Index:** The sequence of measurements over time.
  (x-axis/dates in the heatmap).

While this complex input signal is difficult for the human brain to understand
or analyse, this multi-feature input provides a rich dataset for the autoencoder
so it can detect both events in the time domain (sudden shocks) as in the
frequency domain (bearing faults, imbalance, etc). With some additional data
augmentation (beyond the scope of this text), this dataset becomes the training
input for the autoencoder. Please keep in mind that only the first month of
data was used to train the ML model, and the full spectral heatmap of the
previous chapter was only captured in the next months. However we use all data
here to help the reader to understand.

#### Autoencoder Functionality

The autoencoder attempts to compress this Nx3 input signal into a reduced
l-dimensional latent space. Once trained, the autoencoder reconstructs each
new measurement and compares it with the original STFT input. The difference
between the original and reconstructed signal is quantified using a loss
function (MAE, MSE, logCosh, ...), which maps this discrepancy to a single
numerical value representing the anomaly score as shown in the figure below.

// Insert figure with the anomaly output of the autoencoder here

#### Anomaly Detection and Visualization

The output of the loss function clearly shows an increase in the anomaly score
at the very same timestamps corresponding to the issues we visually detected
in the heatmap from the previous chapter. However, the key advantage here is
that this anomaly detection is done without needing to visually inspect a
heatmap or to manually set individual thresholds for each frequency bin. In
addition, the level of the anomaly score will gain us useful insight in the
stability of the anomaly, and give a good estimate about the rate in which
the machine is deviating from that operating point (i.e. how fast an
intervention must be planned)

#### Thresholding and False Alarm Mitigation

Since we now have a useful indicator for the anomaly score, we can implement
a simple, temperature-like threshold based on historical anomaly levels. To
reduce the risk of false alarms, the output of the loss detector is first
smoothed using a rolling window quantile estimator before being compared to
the threshold level.

This allows us to define multiple confidence levels for the anomaly score,
taking into account the past n measurements to reduce variance and avoid false
alarms.

### Dashboard and Integration with Other Systems
The iQunet Edge system provides all functionality for the above described
signal processing functions in one edge device. This edge device contains
not only the controller for up to more than 100 vibration sensors in a single
device, but also all postprocessing functionality for the conversion to RMS,
spectral plots, historical trends, machine learning inference and
thresholding-based alarms.

The visualization can be done using the built-in fully customizable dashboard
or raw or postprocessed data can be exported to any third-party tools that
support OPC-UA, GraphQL or the MQTT protocols. Below is such an example of a
customized multi-page dashboard for the plant-operator. No external tools except
for a browser in kiosk mode is required to get started.

---

### Conclusion
Wireless vibration sensors combined with machine learning provide a powerful
solution for the day-to-day anomaly detection in industrial shaker machines.
By continuously monitoring machine behavior and processing data through
advanced ML models, emerging random faults can be detected before they become
catastrophic. This predictive approach minimizes unplanned downtime, and allows
to align repairs with the scheduled maintenance. The ability to automatically
detect complex issues without relying on manual inspections or preset thresholds
highlights the potential of integrating machine learning into industrial
maintenance strategies, bringing the required level of understanding from
expert level to anyone with some technical background.

For more detailed technical insights and support, explore our [documentation](https://iqunet.com/resources/) and [case studies](https://iqunet.com/resources/case-studies/case-study-1-international-airport/), or contact our [support team](https://iqunet.com/contact/).
