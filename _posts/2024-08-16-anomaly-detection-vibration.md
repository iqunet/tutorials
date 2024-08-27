---
title: "Anomaly Detection Using MEMS Vibration Sensors and Machine Learning"
date: 2024-08-18
categories: blog
toc: true
toc_sticky: true
published: true
---

<img
  src="{{ site.baseurl }}/assets/images/recycling_plant.jpg"
  alt="Recycling Plant Artists Impression"
  width="500px"
/>

### Scope and TL;DR
This blog post explores how wireless vibration sensors and machine learning
techniques are used for anomaly detection in industrial shaker machines. By
monitoring vibration data and using deep-learning models, various types of
mechanical faults can be detected at an early stage. We cover the technical
setup and data postprocessing using autoencoders, which are the key elements
for reliable and fully automated fault detection.

<img
  src="{{ site.baseurl }}/assets/images/vibration-to-anomaly.jpg"
  alt="Teaser Banner Vibration Sensors to Anomaly Score"
  width="100%"
  style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>

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

See "*How does the post-separation process work?*"
<a class="external"
  href="https://www.avr.nl/en/optimal-process/nascheidingsinstallatie-nsi"
  target="_blank">AVR.nl
</a>.

<img
  src="{{ site.baseurl }}/assets/images/vibration-avr-separation.svg"
  alt="Schematic Representation of the AVR Separation Plant"
  width="100%"
  style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>
<figcaption>
  Figure 3: Overview of the Household Waste Separation Process
  (click to enlarge) [credits: AVR].
</figcaption>

While digital PLCs are in the control of the pipeline and can already detect
the most acute faults in realtime, machine manufacturers treat predictive
monitoring mostly as an afterthought, leaving it to the customers to handle
unexpected random failures. However, in unhealthy environments filled with dust,
humidity, and noise, daily manual inspections are not practical.

<img
  src="{{ site.baseurl }}/assets/images/vibration-dust.jpg"
  alt="Unhealthy Environment with Dust"
  width="500px"
/>
<figcaption>
  Figure 4: Unhealthy environment at a waste processing plant &mdash;<br />
  Accumulation of dust on the receiver module after several weeks of operation.
</figcaption>

In this blogpost, we will explore how ruggedized wireless vibration sensors
and machine learning in the data postprocessing chain provide us with consistent
regular health updates, enabling early detection of issues. We shall cover the
technical setup, the data processing, and the machine learning which automate
the anomaly detection in noisy environments.

> *Noisy, in this case, refers to the sensor signal, which is polluted with
> unwanted vibrations from the production process itself, in addition to the
> machine defects we are trying to detect here.*

---

### Monitoring Shaker Conveyors

Monitoring vibrating equipment in waste management plants presents unique
challenges. These plants are large, and network infrastructure is often
lacking. Installing cabling across such large sites is not only expensive but
also prone to failures. This is especially true for machines that experience
significant vibrations.

One example is vibratory feeders, which spread the household waste material
before it undergoes optical sorting. In the optical sorter, spectral cameras
detect different materials, and pressurized air is then used to separate
individual pieces of waste into different output flows.

See "*SPALECK: Recycling Waste Screens*"
<a class="external"
  href="https://www.spaleck.eu/screening-machines"
  target="_blank">[spaleck.eu]
</a>.

<img
  src="{{ site.baseurl }}/assets/images/vibration-vibratory-feeder.jpg"
  alt="Vibratory Feeder with Vibration Sensor Location"
  width="100%"
  style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>
<figcaption>
  Figure 5: Vibratory Feeder with the location of the Vibration Sensor
  [image credit: SPALECK].
</figcaption>

These vibratory feeders, which ensure the even distribution of material, pose
several challenges:

- **Large Displacements:** Vibratory feeders experience translational
displacements of up to 10 cm, making not only themselves prone to considerable
stresses but also make wired sensors susceptible to both connector wear and
cable fatigue in the long term.
  
- **Regular Maintenance:** Parts of these machine are frequently disassembled
for maintenance. It is preferred that any sensors should be as non-intrusive as
possible during such manipulations while also maintaining consistent location
and orientation. This stability improves the accuracy of the machine learning
algorithms, as discussed later in this post.

Given the challenges of monitoring shaker machines, the customer here opted
for wireless sensors to avoid the above issues.

<video width="300px" controls loop autoplay muted style="margin-left: 1em;">
  <source src="{{ site.baseurl }}/assets/videos/vibration-screen-render.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
<figcaption>figure 6: Video Demonstrating Sensor Placement and the Challenging
  Conditions on a Shaker Screen in a Waste Processing Plant.</figcaption>

Also, to ensure that routine maintenance tasks can be performed without
disturbing the sensors, they were installed 40 cm away from the ideal location.
This placement on the machine frame, rather than directly on the motor and
drive train, drastically reduces the sensitivity to high-frequency bearing
faults but ensures consistent data collection over a long period, even after
part replacements. This highlights the gap between ideal lab conditions and
a typical installation.

Other factors that need to be considered include:

- **Signal Propagation:** The sensor's non-ideal placement introduces multiple
wave propagation boundaries (i.e. transitions between materials), which
attenuate and reflect high-frequency signals. This makes measurements above
10 kHz, including ultrasonic frequencies, costly and of limited benefit.
  
- **Unsuitability of RMS Sensors:** In simple RMS sensors, fault signals will
be masked by process noise, making them ineffective for vibratory feeders
except for the most obvious late-stage catastrophic failures.

---

### MEMS Accelerometers

Given the above prerequisites, triaxial MEMS-based wireless vibration sensors
are an ideal choice.

<img
  src="{{ site.baseurl }}/assets/images/vibration-mems-die.jpg"
  alt="Microphotograph of a MEMS Accelerometer Die"
  width="500px"
  style="margin-left: 1em;"
/>
<figcaption>
  Figure 7: Microphotograph (2x2mm) of a MEMS Accelerometer (without ASIC processor).
  <br /> Hollocher et al., "A Very Low Cost, 3-axis, MEMS Accelerometer for
  Consumer Applications," 2009. 
  <a class="external"
    href="https://www.researchgate.net/publication/224107749"
    target="_blank">[researchgate.net]
  </a>.
</figcaption>

Fully integrated MEMS (micro-electromechanical system) vibration sensors detect
acceleration by measuring changes in capacitance (distance) between a fixed
electrode and a suspended on-chip proof mass. The variations in capacitance are
then digitized by the ASIC postprocessor embedded in the same
<a class="external"
  href="https://en.wikipedia.org/wiki/System_in_a_package"
  target="_blank">SiP package
</a>
and converted into their corresponding acceleration values.

- **Robustness:** MEMS sensors are highly durable and well-suited for long-term
use in harsh environments. Piezo accelerometers on the other hand, have superior
noise characteristics but are more prone to material failures of the ceramic
sensing elements and need more careful handling to maintain their calibrated
sensitivity.

- **Frequency Response:** MEMS sensors capture vibrations up to a few kHz(\*) in
three axes. This allows for spectral separation of process noise and fault
frequencies, so we can tune for the optimal the signal-to-noise ratio and
fault sensitivity.  
(\* the installed sensors have a Nyquist -3dB bandwidth of +/-1KHz)

<img
  src="{{ site.baseurl }}/assets/images/vibration-IVIB161010-ACC3-016-RBW-performance.png"
  alt="Noise Performance of the iQunet IVIB161010-ACC3-016 Accelerometer"
  width="90%"
  style="margin-left: 1em; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>
<figcaption>
  Figure 8: Peak and Noise Performance of the iQunet IVIB161010-ACC3-016
  Accelerometer.
  <br />Detailed background on Frequency Response and RBW performance figures
  <a class="external"
    href="https://www.analog.com/media/en/analog-dialogue/volume-51/number-3/articles/mems-vibration-monitoring-acceleration-to-velocity.pdf"
    target="_blank">here
  </a>.
</figcaption>

- **Wireless Range:** With a range of 20 to 50 meters, wireless sensors
eliminate the need for fragile and expensive cabling. Downside is the need for
battery replacement every 20-50,000 spectral measurements.

- **Cost:** Each vibratory screen is equipped with 4 triaxial sensors.
Switching to piezoelectric sensors would significantly increase costs, tripling
the expense for the sensor elements alone compared to the total cost of the
complete wireless MEMS-based system.

<img
  src="{{ site.baseurl }}/assets/images/vibration-wired-bridge.jpg"
  alt="Wireless Bridge for IEPE Vibration Sensors"
  width="90%"
  style="margin-left: 1em; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>
<figcaption>
  Figure 9: Despite offering better sensitivity, a wireless IEPE bridge, with
  its additional cabling, is not a viable alternative to the existing 4x
  wireless MEMS triax sensors on the vibratory screen.
</figcaption>

In the next chapters, we will discuss how the sensor data is post-processed
and used to align otherwise unplanned downtime with scheduled maintenance tasks,
effectively reducing standstills to virtually 0 excess downtime.

---

### Sensor Data Processing and Machine Learning

The MEMS-based wireless vibration sensors (IVIB161010-ACC3-016) gather detailed,
day-to-day insights into machine behavior. Each sensor captures three-axis
vibration snapshots every 20 minutes (configurable) at a sampling rate of 3200Hz
(also configurable).
A measurement, consisting of up to 25,000 samples, is wirelessly transferred
to a central edge server equipped with an embedded historian database.

<img
  src="{{ site.baseurl }}/assets/images/vibration-opcua-historian.png"
  alt="OPC-UA client showing historian vibration data."
  width="95%"
  style="margin-left: 1em;"
/>
<figcaption>
  Figure 10: Up to 25GB of raw vibration data is stored in the OPC-UA historian
  database, which is used to train a deep learning model of the machine's
  behavior across different operating conditions.
  <br /><i>(image: UaExpert OPC-UA client.
  <a class="external"
    href="https://www.unified-automation.com/products/development-tools/uaexpert.html"
    target="_blank">[link]</a>)</i>
</figcaption>

The edge server includes a TensorFlow processor for machine learning inference,
along with a customizable dashboard, making it a complete standalone solution.
For compatibility with third-party applications, the software also comes with
an OPC-UA server and MQTT publishing client, enabling real-time visualization
on the most common SCADA platforms (Kepware, Ignition, Siemens SIMATIC, etc.)
and cloud-based IoT systems.

<img
  src="{{ site.baseurl }}/assets/images/vibration-dashboard-322-9944.png"
  alt="Screenshot of the embedded web interface of the edge server."
  width="95%"
  style="margin-left: 1em;"
/>
<figcaption>
  Figure 11: The edge server comes with an embedded web interface and supports
  third-party software integration through OPC-UA, MQTT, and GraphQL. Both
  raw vibration data and post-processed derived metrics such as RMS, velocity
  and ML anomaly levels are exposed by all interfaces.
  [image: iQunet] <br /><i>(click to enlarge)</i>.
</figcaption>

### From Raw Data to Actionable Insights

The raw vibration data (i.e. acceleration time series vectors) collected by the
sensors undergoes several preprocessing steps to extract several aggregate and
more complex signal transformations.

#### Prefiltering, Data Streams and Domains

**Prefiltering**  
   Certain types of piezo sensors can generate high dynamic range velocity
   signals at very low frequencies using a charge-mode amplifier. However,
   MEMS sensor data is acceleration based and must be prefiltered to remove
   any near-DC components before the conversion to velocity.

   > **Expert Insights**  
   > Filtering is a complex mathematical process, similar to the preamp
   > stabilization time in piezo sensors. It is important to ensure that the
   > high rejection ratio of a highpass filter does not introduce ripple or
   > phase errors, as these can distort the time-domain signal and cause
   > significant drift when integrating from acceleration to velocity. Linear
   > phase-filters, such as multi-stage digital FIR filters, are typically
   > used to address these challenges.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-linear-phase-filter.jpg"
     alt="Removing the DC-offset with a linear-phase filter."
     width="95%"
     style="margin-left: 1em;"
   />
   <figcaption>
     Figure 12: To integrate acceleration data into a velocity signal, the DC
     offset must be removed to avoid drift in the integrated output. A
     linear-phase higpass filter, such as a Biquad FIR filter, is essential to
     preserve signal integrity during this process. In contrast, a
     nonlinear-phase filter, like the Chebyshev IIR filter, introduces severe
     phase distortion.
   </figcaption>

**Data Streams**  
   Once the DC-offset is removed, the data is converted into several useful
   information streams in the edge server, including:

   - **Acceleration and velocity**
   - **RMS and Kurtosis aggregate values**
   - **Time and frequency domain views**

   These are some of the basic tools used by vibration experts to determine
   the state of the machine, and in more advance cases, also the origin of a
   fault, such as a loose mount or a bearing fault.

<img
  src="{{ site.baseurl }}/assets/images/vibration_processing_flow.png"
  alt="Processing flow of vibration data in the edge server."
  width="95%"
  style="margin-left: 1em;"
/>
<figcaption>
  Figure 13: Raw vibration data post-processing flows in the edge server. RMS
  data is the least sensitive for fault detection. Frequency plots and heatmaps
  are the preferred methods for experts. Machine learning-based anomaly
  detection combines the simplicity of RMS thresholds with the sensitivity
  of manual time/frequency domain analysis.
</figcaption>

   Other tools, such as enveloping demodulation, further postprocess the signal,
   primarily to represent the same data in a format or domain that is more
   easily understood by the human eye.

   However, this blog post focuses on the automated detection of anomalies and
   faults using machine learning techniques. It's important to understand that
   the specific formats in which vibration data is represented are less critical
   for deep-learning models, as these tools will 'learn' the optimal latent
   representation of the data during the training phase.

**Time and Frequency Domain**  
   So why would a vibration expert use both the time and frequency views?
   Although they represent the same underlying information, each domain has its
   advantages when it comes to detecting specific signal patterns.

   For instance, one-time or repetitive transient events in the signal (e.g. a
   mechanical impulse or a bearing failure) are easily identified in the time
   domain, where their energy is concentrated in a short interval. However, in
   the frequency domain, the same short event merely appear as a slight raise
   in the noise floor, making them difficult to detect.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-pulse-timedomain.png"
     alt="Impulse response from a bearing defect in time and frequency domains"
     width="90%"
     style="margin-left: 1em;"
   />
   <figcaption>
     Figure 14: Example of a bearing fault. Impulse responses are easily
     detectable in the time domain but spread across a broad frequency range,
     particularly in variable-speed machines or for non-repetitive events.
   </figcaption>

   Early-stage bearing faults (stage 1/2) are most effectively detected at
   ultrasonic frequencies, where the noise floor is more favorable. However,
   practical constraints may dictate the use of MEMS sensors, which offer a
   cost-effective solution in real-world applications.

   For repetitive impulses, energy concentrates around key fault frequencies(\*),
   such as BPFI and BPFO (stage 2/3), which are well within the capabilities
   of modern MEMS sensors. Nevertheless, capturing sufficient impulses to rise
   above the noise floor is essential. Extended measurements, however, may pose
   challenges for wireless sensors due to their data and battery constraints.  
   (\*) More info here:
   <a class="external"
     href="https://www.reliabilityconnect.com/bearing-problems-fault-frequency-and-artificial-intelligence-based-methods/"
     target="_blank">[reliabilityconnect.com]
   </a>.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-pulse-repetitive.png"
     alt="Repetitive bearing fault defect in time and frequency domains"
     width="90%"
     style="margin-left: 1em;"
   />
   <figcaption>
     Figure 15: Example of a repetitive impact fault. This one is easily
     detected above the noise in the frequency domain as the energy from
     multiple impacts concentrates around the repetition frequency.
   </figcaption>
   
   The above consideration is crucial for understanding why we use the
   Short-Time Fourier Transform (STFT) when feeding data into the machine
   learning algorithm. The STFT allows us to represent the sensor signal in
   both the time- and frequency-domain simultaneously. By doing so, we capture
   all relevant information (for the sake of simplicity, we exclude phase
   information here) and ensure that the signal power of various fault patterns,
   whether time-based or frequency-based, remains concentrated and is more
   easily detected.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-pulse-stft.jpg"
     alt="STFT heatmap representation of a repetitive impact fault"
     width="90%"
     style="margin-left: 1em;"
   />
   <figcaption>
     Figure 16: The STFT provides simultaneous time and frequency resolution,
     enabling machine learning algorithms to detect faults that manifest in
     either domain. The trade-off between time and frequency resolution is a
     fundamental limitation of the STFT
     <a class="external"
       href="https://sigproc.mit.edu/_static/fall20/lectures/lec09a_slides.pdf"
       target="_blank">[mit.edu]
     </a>.
   </figcaption>

   While is very possible for a machine learning algorithm to perform domain
   transforms internally, this approach would require a significant portion of
   the model structure (specifically, the convolutional layers) to handle these
   transformations. This would unnecessarily complicate the training phase
   as it would also take considerable time to tune the ML model parameters to
   'invent' these transforms.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-autoencoder-latent.png"
     alt="Repetitive bearing fault defect in time and frequency domains"
     width="95%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 17: STFT data is stacked into a third dimension, then split into
     training, validation, and test sets. Each set is further divided into
     mini-batches to train the autoencoder model. When an unseen vibration
     pattern occurs, the latent space fails to represent it accurately, leading
     to a loss value (i.e. anomaly) proportional to the deviation from the
     machine's normal operating point.
     Image based on
     <a class="external"
       href="https://en.wikipedia.org/wiki/Autoencoder"
       target="_blank">[wikipedia.org]
     </a>.
   </figcaption>

   By using the STFT as a fixed preprocessing step, we effectively offload this
   task and provide the ML algorithm with a rich feature input that combines
   the strengths of both domains. In this sense, the STFT acts as a pre-trained,
   fixed component of the machine learning model itself, simplifying the
   detection process and reducing the training time.

---
#### Challenges with Manual Analysis and Traditional Methods

   Linking specific fault patterns to their root cause typically requires expert
   knowledge. Diagnosing issues like bearing faults or other machine-specific
   anomalies demands experience and regular inspections.

   However, these manual methods depend on understanding of the machine's
   internal dynamics and require the measurements to be done in a constant
   operating point to accurately track fault progression over time.

   <div style="padding: 0 2em 0.5em 1em">
   <iframe
     width="560"
     height="315"
     src="https://www.youtube.com/embed/67Et4vbKhOM?si=kcDpT6cfHer5wFOe"
     title="YouTube video player"
     frameborder="0"
     allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
     referrerpolicy="strict-origin-when-cross-origin"
     allowfullscreen
   >
   </iframe>
   </div>
   <figcaption>
     Figure 18: Traditional vibration analysis using conventional methods
     requires expert knowledge and is typically not performed on non-critical
     assets due to cost restrictions.
     <br /><i>Credits: Mobius Institute
     <a class="external"
       href="https://www.mobiusinstitute.com/learn"
       target="_blank">[mobiusinstitute.com]
     </a></i>.
   </figcaption>

   Relying solely on specialists is costly, and the extended intervals between
   inspections can result in missed random faults. Oftentimes, the plant
   operator just wants to be alerted in time about an upcoming problem,
   then follows the fault progress over the next days more closely and will
   replace the faulty component without the need for an expensive detailed
   report about the fault.

   For online monitoring, the sheer volume of data --hundreds of plots
   generated daily-- makes manual analysis impractical. Automated analysis
   tools are essential here. 

   <img
     src="{{ site.baseurl }}/assets/images/vibration-thresholds.png"
     alt="Repetitive bearing fault defect in time and frequency domains"
     width="95%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 19: Automated alarm systems often mirror the approach of a
     vibration expert in software, requiring order tracking and manual
     threshold tuning. False alarms may lead operators to ignore alerts
     altogether, including valid warnings.
     <br /><i>Image: AMC VIBRO
     <a class="external"
       href="https://amcvibro.com/publications/10-alarm-thresholds/"
       target="_blank">[amcvibro.com]
     </a></i>.
   </figcaption>

   Traditional automated methods, such as frequency binning and manually
   setting thresholds for each bin, have widely proven their value but come
   with inherent limitations.

   - **Dependency on Expertise:** Setting accurate thresholds requires good
     understanding of the machine's internals.

   - **Operating point variability:** Threshold-based frequency band or
     enveloping alarms are most effective when a machine operates under stable
     speeds and loads. In environments with varying conditions, thresholds often
     need to be relaxed to avoid false positives, which significantly reduces
     the sensitivity of the monitoring system.

---
#### Enter the Power of Machine Learning

   Machine learning (ML) techniques offer a more flexible solution to track
   the health of a machine. The models used in ML can represent the machine's
   time and frequency vibration data using latent (internal) variables, which
   provide an abstract view of the machine's internal state.

   > **Latent Variables:**  
   >  In an autoencoder, for example, the ML model is trained to compress the
   >  vibration data (the STFT representation in our case) into a compact set
   >  of latent variables, essentially creating what some marketing materials
   >  might call a "digital twin."

   <img
     src="{{ site.baseurl }}/assets/images/vibration-vae.png"
     alt="autoencoder banner"
     width="90%"
     style="margin-left: 1em;"
   />

   This discussion will focus on unsupervised learning and **autoencoders** in
   particular, as they can be applied to a broad range of topics, without the
   need for costly manual training.

   <div style="max-width: 20em;">
   <iframe
     width="560"
     height="315"
     src="https://www.youtube.com/embed/JoR5HCs0n0s"
     title="YouTube video player"
     frameborder="0"
     allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
     referrerpolicy="strict-origin-when-cross-origin"
     allowfullscreen
   >
   </iframe>
   </div>
   <figcaption>
     Figure 20: Introduction to Autoencoders.
     <a class="external" href="https://www.youtube.com/sentdex"
       target="_blank">[youtube.com/Sentdex]
     </a>
   </figcaption>

   After the training phase, these latent variables capture the subtle
   interactions between speed, load, temperature, and the time and frequency
   domain components of the input signal. Think of this as a more sophisticated
   version of the relationship between machine load and temperature, but in
   multiple dimensions, with more variables and with greater complexity.

   > "Oftentimes, the neural network will discover complex features which are
   > very useful for predicting the output but may be difficult for a human
   > to understand or interpret."  
   > <small>Andrew Ng. CS229 Lecture Notes: Deep Learning, Chapter II. Stanford
   > University, June 2023.
   > <br/> Retrieved from
   >  <a class="external" href="https://cs229.stanford.edu/main_notes.pdf"
   >    target="_blank">[stanford.edu]
   >  </a>
   > </small>

   While the latent variables themselves won't give us direct insight in the
   machine's health status, they do provide the foundation for estimating how
   far the the machine's current behaviour deviates from its normal operating
   point. The normal state is defined by a cluster of complex patterns captured
   from the thousands of measurements during the training phase.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-t-sne.svg"
     alt="t-SNE visualization of the latent space of machine operating point"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 21: t-SNE visualization of the L-dimensional latent space reveals
     clusters corresponding to different machine operating points. t-SNE is a
     nonlinear transformation that reduces high-dimensional data to 2D or 3D
     for visualization. It keeps similar data points close together in the
     lower-dimensional space.
     <br /><i>More info:
     <a class="external" href="https://www.youtube.com/watch?v=wvsE8jm1GzE"
       target="_blank">[youtube.com/GoogleDevelopers]
     </a></i>
   </figcaption>

   For example, if a harmonic component appears (or disappears for that matter)
   in the STFT that wasn't present during the training (e.g. a bearing fault),
   or if a specific unexpected combination of harmonics occurs, the latent
   variables won't be optimized to accurately represent this newfound state.
   As a result, the output of the autoencoder will start to diverge from the
   input.

   <img
     src="{{ site.baseurl }}/assets/images/vibraton-encode-decode-loss.svg"
     alt="t-SNE visualization of the latent space of machine operating point"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 22: Autoencoder-based anomaly detection using STFT spectrograms.
     The input is compressed into a latent space and decoded again; anomalies
     introduce reconstruction errors, leading to divergence and increased values
     in the loss history plot.
   </figcaption>

   This discrepancy between the input and the model's output is measured by a
   loss function, for example the LogCosh (log of the cosh of the prediction
   error), which transforms it into a single numerical value: the loss value
   or so-called "anomaly level" that indicates how good the model can represent
   the current measurement and thus indirectly how far the machine is operating
   from its pre-trained cluster of behavioural states.

   In the next chapter, we will return to our real-world example of the
   vibratory feeder. We'll start by examining the raw data to better understand
   the signal itself, then convert that data to its STFT representation and
   feed it into the autoencoder. By the end, we'll have a clearer understanding
   of what machine learning can offer beyond the "black magic box" that it
   may appear to many people in the field of vibration analysis.

### Real-world Vibratory Feeder Data

   Figure 23 shows the autoencoder loss of a vibratory screen, based on 4,400
   measurements (8192 samples) collected from a triaxial MEMS sensor between
   February and August 2024. 

   The historical data reveals the progression of a bearing fault over time:

   - Training set from February to March (600 measurements)
   - Signs of **initial damage** become detectable around March 24 (T-70d)
   - Further **deterioration** from May 22 onwards (T-11d)
   - **Critical damage** (stage 5 bearing fault) on June 2 (T)
   - The bearing was **replaced** on June 17 (T+15d)

   <img
     src="{{ site.baseurl }}/assets/images/vibration-screen3131-losses.svg"
     alt="Autoencoder loss history graph showing bearing fault progress"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 23: Autoencoder loss (anomaly) showing the progression of a bearing
     fault in a vibratory screen. While unsupervised learning does not reveal
     the root cause, it provides an early detection system and allows to track
     the fault progression hour-by-hour with little effort.
   </figcaption>

   Beyond the bearing failure, the data also shows a new increase in the anomaly
   level on August 8 (far right side fig. 23). This rise has been confirmed to
   be caused by a bent shaft, which was scheduled for replacement during the
   upcoming maintenance cycle.

#### Time Domain RMS Data

   <img
     src="{{ site.baseurl }}/assets/images/vibration-screen3131-rms.svg"
     alt="RMS historian plot only reveals stage-5 bearing faults"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 24: Unless tuned to the specific fault frequencies, the RMS history
     only reveals the last stage of a bearing failure.
   </figcaption>

   // Insert comparison of time domain data before and after the fault appears

   Initially, the time domain data does not reveal much due to the presence of
   process noise. The fault's energy remains buried below the noise floor until
   the very late stages, when the fault's energy becomes high enough to rise
   above the process noise. As a result, relying solely on time-domain data or
   simple RMS power thresholds is insufficient to detect early warning signs
   and track the stability of a developing fault.

#### Frequency Domain Data

   When we convert to the frequency domain, the picture becomes clearer. The
   energy components of the vibratory feeder process are mainly concentrated
   at the lower frequencies, as expected. Additionally, the vibration dampers
   absorb higher frequencies associated with the product processing somewhat,
   making the upper half of the spectrum the ideal candidate to focus on for
   anomaly detection. 

   In most cases, there is no a-priori information about the machine provided
   by the customer, simply because it does not exist. Setting precise thresholds
   for each frequency bin as would be done with traditional threshold-based
   band alarm approaches, remains a tedious challenge. Without expert knowledge
   about the machine characteristics, the risk for incorrect thresholds is real.

   For example, the intermodulation of the drive train frequencies and harmonics
   with the actual fault frequencies may cause certain spectral components to
   disappear when a fault occurs, which is excactly the opposite from what
   setting a threshold is trying to achieve. This is where the autoencoder ML
   approach becomes a valuable asset in our toolbox.

#### Spectal Heatmap

   Before we review the ML results, we make an intermediate stop and introduce
   the spectral heatmap. In this plot, the horizontal x-axis represents time,
   and the vertical slices (y-axis) represents the frequency spectrum of a
   single measurement. The amplitude of the spectrum is now represented by a
   color map, with dark blue indicating the lowest magnitude and yellow the
   highest peaks in the frequency spectrum.

   On this plot, we can observe that the gross of process noise is concentrated
   around the fundamental drive frequency and multiple odd harmonics thereof.
   The higher harmonics originate from the conversion process of the sinusoidal
   movement of the feeder to the nonlinear friction on the processed waste by
   the structure of the feeder topology (ref here).

   For the remainder of this discussion, we will ignore the lower part of the
   spectrum, as this portion of the heatmap mainly contains spectral components
   of the waste processing, and we are mostly interested to detect faults in
   the feeder drive train. However, it does not imply that the lower part of
   the spectrum is useless, as it may contain valueable information about the
   waste processing itself.

   In the upper part of the spectrum, we can observe some early stage
   indicators of an upcoming change in the behaviour of the machine. First signs
   are around x weeks before the critical damage of the bearing, then it
   disappears temperorarily because of routine maintainance and about x days
   before the fatal damage it appears again. In the final stages of the bearing
   damage, we can see the fault spectrum spread out over all frequency bands,
   which is the well-known indicator for stage-4 bearing damage.

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
measurement is converted into a numeric matrix similar to the spectral
heatmap described previously. However, in this case, the input data is
extended to three dimensions.

- **Time domain:** The 3x8192 samples within each single measurement.
- **Spectrum:** Frequency-domain data of above time domain.
- **Measurement Index:** The stack of measurements over time
  (dates in the heatmap).

While this complex input signal is difficult for the human brain to understand
or analyse, this multi-feature input provides a rich dataset for the autoencoder
so it can be trained on both events in the time domain (sudden shocks) and in
the frequency domain (bearing faults, imbalance, etc).

With some additional data augmentation and mini batches (beyond the scope of
this text), this dataset becomes the training input for the autoencoder. Please
keep in mind that only the first month of data was used to train the ML model,
and the full spectral heatmap of the previous chapter was only captured in the
next months. However we use all data here to help the reader to understand and
observe the emerging bearing failure.

#### Autoencoder Functionality

The autoencoder attempts to compress this NxMx3 input signal into a reduced
L-dimensional latent space. Once trained, the autoencoder reconstructs each
new (i.e. unseen) measurement and compares it with the original STFT input.
The difference between the original and reconstructed signal is quantified
using a loss function (MAE, MSE, logCosh, ...), which maps this discrepancy
to a single numerical value representing the anomaly score as shown in the
figure below.

// Insert figure with the anomaly output of the autoencoder here

#### Anomaly Detection and Visualization

The output of the loss function (i.e. the loss value over the historical
measurements) clearly shows an increase in the anomaly score at the very same
timestamps corresponding to the events we had already visually detected in the
heatmap from the previous chapter. However, the key advantage here is that this
anomaly detection is done without needing to visually inspect a heatmap or to
manually set individual thresholds for each frequency bin.

In addition, the level of the anomaly score will gain us useful insight in the
stability of the anomaly, and give a good estimate about the rate in which
the machine is deviating from that operating point (i.e. how soon an inspection
or intervention must be planned).

#### Thresholding and False Alarm Mitigation

Since we now have a useful indicator for the anomaly score, we can implement
a simple, temperature-like threshold based on historical anomaly levels. To
reduce the risk of false alarms, the output of the loss detector is first
smoothed using a rolling window quantile estimator before being compared to
the threshold level.

The rolling estimator allows us to define multiple confidence levels for the
anomaly score, taking into account the past n measurements to reduce variance
and avoid false alarms.

### Dashboard and Integration with Other Systems
The iQunet Edge system provides all functionality for the above described
signal processing functions in one edge device. This edge device contains
not only the controller for up to more than 100 (vibration) sensors in a single
device, but also all postprocessing functionality for the conversion to RMS,
spectral plots, historical trends, machine learning inference and
thresholding-based alarms.

The visualization can be done using the built-in fully customizable dashboard
and raw or postprocessed data can be exported to any third-party tools that
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
expert vibration analist to anyone with a good technical background.

For more detailed technical insights and support, explore our [documentation](https://iqunet.com/resources/) and [case studies](https://iqunet.com/resources/case-studies/case-study-1-international-airport/), or contact our [support team](https://iqunet.com/contact/).
