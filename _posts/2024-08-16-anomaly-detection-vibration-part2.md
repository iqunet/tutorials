---
title: "Anomaly Detection Using MEMS Vibration Sensors and Machine Learning - Part 2/3"
date: 2024-08-18
categories: blog
toc: true
toc_sticky: true
published: true
---

<img
  src="{{ site.baseurl }}/assets/images/recycling_plant.jpg"
  alt="Recycling Plant Artists Impression"
  width="300px"
/>

{: .description_3}
This is the second part in a three-part series.  
[Part 1: Sensors in a Waste Processing Plant]({{ site.baseurl }}/2024/08/16/anomaly-detection-vibration-part1.html)  
[Part 3: Real-world Vibratory Screen Data]({{ site.baseurl }}/2024/08/16/anomaly-detection-vibration-part3.html)

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

   In the next part, we will return to our real-world example of the
   vibratory screen. We'll start by examining the raw data to better understand
   the signal itself, then convert that data to its STFT representation and
   feed it into the autoencoder. By the end, we'll have a clearer understanding
   of what machine learning can offer beyond the "black magic box" that it
   may appear to many people in the field of vibration analysis.

---

   [Part 3: Real-world Vibratory Screen Data]({{ site.baseurl }}/2024/08/16/anomaly-detection-vibration-part3.html)
