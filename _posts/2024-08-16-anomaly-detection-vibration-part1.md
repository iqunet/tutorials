---
title: "Anomaly Detection Using MEMS Vibration Sensors and Machine Learning - Part 1/3"
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
This post explores how **wireless vibration sensors** and machine learning
techniques are used for **anomaly detection** in industrial shaker screens.
By monitoring vibration data and using deep-learning models, various types of
mechanical faults can be detected at an early stage.

{: .description_3}
This is the first part in a three-part series.  
[Part 2: Anomaly Detection with Autoencoders]({{ site.baseurl }}/blog/anomaly-detection-vibration-part2)  
[Part 3: Real-world Vibratory Screen Data]({{ site.baseurl }}/blog/anomaly-detection-vibration-part3)

We cover the technical setup and data postprocessing using autoencoders
(part 2), which are the key elements for reliable and fully automated fault
detection.

Finally, based on real-world data collected during an 8-month long data
collection example from a household waste processing plant in the Benelux, the
reader will understand both the strengths and weaknesses of the system (part 3).

<img
  src="{{ site.baseurl }}/assets/images/vibration-to-anomaly.jpg"
  alt="Teaser Banner Vibration Sensors to Anomaly Score"
  width="100%"
  style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>

This read is targeted at both the vibration expert and the casual reader
interested in gaining better insight in the practical applications of machine
learning, beyond the hype that has surrounded it in recent years.

### Introduction
Waste management plants rely on long serial processing lines. Failures in any
pivotal stage may cause severe capacity loss due to the limited redundancy. This
makes some level of monitoring targeted towards machine health and predictive
maintainance crucial to avoid unplanned downtimes and the cost that inevitably
comes with it.

See "*How does the post-separation process work?*" by
<a class="external"
  href="https://www.avr.nl/en/optimal-process/nascheidingsinstallatie-nsi"
  target="_blank">AVR.nl
</a> for additional photos.

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

While **digital PLCs** are in the control of the pipeline and can already
detect the most **acute faults** in realtime, machine manufacturers treat
predictive monitoring mostly as an afterthought, leaving it to the maintanance
staff to handle unexpected random failures. However, in unhealthy environments
filled with dust, humidity, and noise, routine manual inspections are not
practical.

<img
  src="{{ site.baseurl }}/assets/images/vibration-dust.jpg"
  alt="Unhealthy Environment with Dust"
  width="500px"
/>
<figcaption>
  Figure 4: Unhealthy environment at a waste processing plant &mdash;<br />
  Accumulation of dust on the receiver module after several weeks of operation.
</figcaption>

In this blogpost, we will show that ruggedized **wireless vibration sensors**
and machine learning in the data postprocessing chain provide us with 
**consistent health updates** at a regular interval, enabling early detection
of issues. We shall cover the technical setup, the data processing, and the
machine learning which automate the anomaly detection in noisy environments.

> *Noisy, in this case, refers to the sensor signal, which is polluted with
> unwanted vibrations from the production process itself, in addition to the
> machine defects we are trying to detect here.*

---

### Monitoring Vibration Screens

Monitoring vibrating conveyor equipment in waste management plants presents
unique challenges. These plants are large, and network infrastructure or good
cellular coverage is often lacking. Installing **cabling across large sites** is
not only **expensive** but also prone to failures. This is especially true for
machines that experience significant vibrations.

One example such an is a **vibratory screen**, which pre-sorts the household
waste material on size before it undergoes optical sorting. In the optical
sorter, spectral cameras detect different materials, and pressurized air is
then used to further separate individual pieces into different output flows.

See "*SPALECK: Recycling Waste Screens*"
<a class="external"
  href="https://www.spaleck.eu/screening-machines"
  target="_blank">[spaleck.eu]
</a>.

<img
  src="{{ site.baseurl }}/assets/images/vibration-vibratory-screen.jpg"
  alt="Vibratory Screen with Vibration Sensor Location"
  width="100%"
  style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
/>
<figcaption>
  Figure 5: Vibratory Screen with the location of the Vibration Sensor
  [image credit: SPALECK].
</figcaption>

These vibratory screens, driven by a synchronous motor that powers an eccentric
axle with counterweight, pose several challenges:

- **Large Displacements:** Translational displacements of up to 10 cm make not
only the shaker itself prone to considerable stresses, but also any wired
sensor setup will be susceptible to both **connector wear and cable fatigue**
in the long term.
  
- **Regular Maintenance:** Parts of these machine are frequently disassembled
for maintenance. It is preferred that any sensors should be as non-intrusive as
possible during such manipulations. This ensures a **consistent sensor location
and orientation** and improves the accuracy of the machine learning algorithms.

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
be masked by process noise, making them ineffective for vibratory screens
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

[Part 2: Anomaly Detection with Autoencoders]({{ site.baseurl }}/blog/anomaly-detection-vibration-part2)  
