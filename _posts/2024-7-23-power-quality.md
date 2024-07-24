---
title: "Monitoring Power Quality in Industrial Compressors"
date: 2024-07-12
categories: blog
toc: true
toc_sticky: true
---

<img src="{{ site.baseurl }}/assets/images/power-compressor.png" alt="Air Compressor Illustration" width="500"/>

### Introduction
This tutorial covers the practical application of power and current monitoring
sensors to track the power quality of industrial compressors. We demonstrate
which parameters are crucial, such as the cosine &phi; (displacement power factor)
and the impact of harmonic distortion, providing a detailed insight into these
power quality metrics.

<img src="{{ site.baseurl }}/assets/images/power-cosphi-distortion.png" alt="Displacement and Distortion" width="95%"/>
<figcaption>figure 1: Displacement (cos &phi;) and Distortion.</figcaption>

The ultimate goal is to predict potential failures, such as overheating, and
offer a gateway to the optimization of industrial equipment.

---

### Technical Background and Problem
Industrial compressors, especially high-power models like the 3-phase 200kW
compressor used in this case study, can cause power quality issues such as
harmonic distortion. In the upstream transformer cabin, the presence of
higher-order harmonics increases core losses due to eddy currents, resulting
in elevated transformer temperatures. Special K-factor transformers are used
to withstand these heating problems, but the heat losses persist.

<img src="{{ site.baseurl }}/assets/images/power-eddycurrents.jpg"
  alt="FLIR thermal image of eddy currents" width="320"/>
<figcaption>figure 2: Eddy currents cause energy losses, such as
  <a class="external" href="https://cr4.globalspec.com/thread/119132/CT-Heating-Problem"
  target="_blank">here</a> resulting in thermal tripping of a generator.
</figcaption>

Additionally, other equipment connected to the same power grid, such as small
electronic equipment power supplies or capacitor banks, may experience a higher
failure rate due to the stresses induced by the unexpected harmonic currents
oscillating between the 200kW compressor and the passive components in their
power supplies.

---

### Sensor Deployment and Capabilities
One of our clients asked to install a power quality monitoring system at the
entry point of one of their compressor rooms. The goal of this monitoring
system is to gain insight in both the cumulative energy consumption and also
the possible infrastructure improvements learned from the captured sensor data.

For this, two sensors were deployed on the compressor room electrical supply,
each with their specific focus:

**GridMate AG1 Power Quality Monitor:** This LoRaWAN-enabled sensor measures
aggregate data such as average grid voltage, RMS and peak current, cosine &phi;,
true power factor (TPF) and distortion power (THD) on all three phases on a 10
minute base interval. This provides us the long-term data essential for the
total energy usage as well as the amount of displacement power and the harmonic
contents.

<img src="{{ site.baseurl }}/assets/images/power-gridmate.jpg"
  alt="GridMate AG1 LoRaWAN Power Monitor"/>
<figcaption>figure 3: GridMate AG1 LoRaWAN Power Monitor.</figcaption>

**Wireless Current Waveform Sensor:** Positioned on one of the phases, this
sensor captures high-speed snapshots (4kS/s) of the current waveform and its
spectrum every 10 minutes. It delivers detailed insights into the time-domain
and harmonic spectrum and helps to identify the various sources of distortion
and intermittent spike events (such as the upstart of the compressor).

<img src="{{ site.baseurl }}/assets/images/power-bridge.jpg"
  alt="iQunet ADMOD-CURR wireless current clamp"/>
<figcaption>figure 4: iQunet wireless current clamp [model ADMOD-CURR].</figcaption>

The combination of these sensors allows for not only real-time analytics but
also provides the historical data necessary for the early detection of potential
faults. In the next chapter, we will delve into this aspect further.

---

### Initial Findings
Within the first few hours, initial data from the GridMate AG1 revealed a high
level of distortion power (approximately 40 kVArd at 250 Hz) compared to 200 kW
of active power at 50 Hz. Although the cosine &phi; seemed to be well-corrected
at around 0.98, the distortion power was the main factor reducing the true power
factor to around TPF=0.65.

#### Waveform Analysis and Root Cause
The current waveform sensor also identified high harmonic distortion as seen in
the system's spectral footprint, with significant spectral components at the 5th
(250 Hz) and 7th (350 Hz) harmonics of the fundamental (50 Hz).

Additionally, the time-domain waveform revealed the characteristic ripple caused
by a 6-pulse 3-phase rectifier at the DB-bus stage of the compressor VFD.

![Waveform and spectrum analysis of the current]({{ site.baseurl }}/assets/images/waveform-spectrum-analysis.svg)

### In-depth Technical Audit
The 5th harmonic was notably significant, making up about 30% of the main
component current in the spectrum plot. From the ratios of the harmonics, it
was determined that a damping choke is used to "just" comply with the IEEE 519
standard when operating at the nominal power of the compressor.

At lower power levels, however, it is observed that the tuning mismatch of the
damping choke results in much worse THD performance characteristic, leading to
non-compliance with even the minimal regulatory requirements.

---

### Results and Benefits

#### Insights
The two sensors provided immediate, detailed insights into power consumption
patterns, enabling better energy management and a deeper understanding of the
root causes of heat losses. While phase compensation with capacitor banks offers
only marginal improvements, the high distortion power is one of the primary
issues that must be addressed.

The customer must now calculate whether the cost of a more advanced VFD (with
extra points of failure) is justified compared to the current situation. This
includes not only the heat losses in the upstream transformer cabin but also
the impact of harmonics on the reduced lifespan of nearby electrical and
mechanical components, such as parasitic bearing currents in equipment connected
to the same grid.

#### Predictive Maintenance
By regularly analyzing the current spectrum, the sensors enable the early
detection of changes in the electronic or mechanical behavior of the compressor.
This proactive approach can significantly reduce downtime and maintenance costs.

#### Machine Learning Applications
Additionally, iQunet offers an optional service to automate anomaly detection.
Small variations in the machine's operating state cause related changes in the
spectral footprint of electical current or mechanical vibrations. While these
changes are difficult to detect with the naked eye, a custom-trained machine
learning model can provide a reliable early warning system for the most
critical assets.

![Example of predictive analytics dashboard]({{ site.baseurl }}/assets/images/predictive-analytics-dashboard.svg)

---

### Conclusion
This case study has demonstrated the capabilities of modern sensor technology
in tackling power quality issues in industrial settings.

By providing detailed measurements, the combination of the appropriate sensors
enables precise registration of energy usage, along with the identification of
the root causes of energy losses. For the experienced user, it offers profound
insights into the installed equipment, including the ability to determine the
VFD characteristics of attached machinery through black-box analysis.

Finally, armed with this knowledge, the customer can take informed steps to
implement future operational improvements and after that continue to monitor
emerging anomalies as a foundation for predictive maintenance.

For more detailed technical insights and support, explore our [documentation](https://iqunet.com/resources/) and [case studies](https://iqunet.com/resources/case-studies/case-study-1-international-airport/), or contact our [support team](https://iqunet.com/contact/).
