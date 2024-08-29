---
title: "Anomaly Detection Using MEMS Vibration Sensors and Machine Learning - Part 3/3"
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
This is the third part in a three-part series.  
[Part 1: Sensors in a Waste Processing Plant]({{ site.baseurl }}/2024/08/16/anomaly-detection-vibration-part1.html)  
[Part 2: Anomaly Detection with Autoencoders]({{ site.baseurl }}/2024/08/16/anomaly-detection-vibration-part2.html)  

### Real-world Vibratory Screen Data

   Figure 23 shows the autoencoder loss of a vibratory screen, based on 4,400
   measurements (3x8192 samples/meas) collected from a triax MEMS sensor between
   February and August 2024. 

   > The monitoring period spans a period of 7 months of measurements and
   > telemetry data with an estimated 70% of remaining battery capacity.

   The historical data reveals the progression of a bearing fault over time:

   - Training set from February to March (600 measurements)
   - Signs of **initial damage** become detectable around March 24 (T-70d)
   - Further **deterioration** from May 22 onwards (T-11d)
   - **Critical damage** (stage 4 bearing fault) on June 2 (T)
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

   <img
     src="{{ site.baseurl }}/assets/images/vibration-bearing-photo.jpg"
     alt="Photo after removing the damaged bearing"
     width="480px"
     style="margin-left: 1em;"
   />
   <figcaption>
     Figure 24: Photograph of the damaged bearing upon removal on June 17.
   </figcaption>

#### Limitations of RMS-only sensors

   Figure 25 illustrates the lack of sensitivity of an RMS-only sensor for
   bearing fault detection. Due to the in-band process noise, the fault's
   energy stays undetectable until the very last stages, when it rises above
   the total integrated noise floor. Relying only on time-domain data or simple
   RMS thresholds is thus insufficient for early fault warnings.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-screen3131-rms.svg"
     alt="RMS historian plot only reveals stage-4 bearing faults"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 25: Unless specifically tuned to the specific fault frequencies,
     the RMS aggregate is only sensitive to last stage of a bearing failure.
   </figcaption>

#### Spectral Heatmap

   To review the ML results, we introduce the spectral heatmap. In this plot,
   the horizontal x-axis represents measurement date, and the vertical slices
   (y-axis) represents the frequency spectrum of 1 single measurement (z-axis).
   Similar to the STFT, the energy in the spectrum is represented by a color
   map, with dark blue indicating the lowest magnitude and yellow the highest
   peaks.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-screen3131-heatmap.svg"
     alt="Vibratory screen spectral heatmap from February to August 2024"
     width="100%"
     style="margin-left: 0em;"
   />
   <figcaption>
     Figure 24: Photograph of the damaged bearing upon removal on June 17.
   </figcaption>

   **Upper part of the spectrum**  
   In the spectrum above 300Hz (bin >1500), we can observe some early stage
   indicators of an upcoming change in the behaviour of the machine. The first
   warning ('initial damage') appears around 10 weeks before the critical damage
   of the bearing, then it disappears temperorarily because of routine
   maintainance.

   Around 11 days before the bearing failure it appears again. In the final
   stage of the bearing damage, we can see the fault spectrum spread out over
   all frequency bands, which is the well-known indicator for stage-4 bearing
   damage. 

   **Lower part of the spectrum**  
   Figure 24 also shows that most of the process noise is concentrated around
   the fundamental drive frequency and its harmonics. For example, bin 500
   (97Hz) shows the process noise modulated onto the 2nd harmonic (synchronous
   motor at mains frequency of 50Hz with 3% slip).

   In the lower part of the spectrum, the harmonics originate partially from
   the inevitable slight imbalance of the very rigid structure of the screen
   itself and partially due to the nonlinear friction of the processed waste
   on the screen's separator structures. Apart from the static load on the
   bearing, the high forces due to the rigid bearing and the dynamic imbalance
   are the main cause of a reduced service life of the eccentric shaft bearing.

   For an in-depth analysis, see
   <a href="https://www.researchgate.net/publication/373367839" target="_blank">
     [researchgate.net]
   </a>:
   <img
     src="{{ site.baseurl }}/assets/images/vibration-screen-model-paper.png"
     alt="Diagnostics of Bolted Joints in Vibrating Screens Based on a Multi-Body Dynamical Model"
     width="100%"
     style="margin-left: 0em;"
   />

   ---

#### Mitigation of False Positives

   While the spectral heatmap provides detailed insights into the operational
   behavior of the vibratory screen, visually inspecting heatmaps is impractical
   for daily machine monitoring.
   
   The key advantage of the STFT + autoencoder approach is its ability to
   project complex sensor signals onto a single numeric "anomaly score" through
   nonlinear transformation.

   The anomaly score allows the implementation of a simple, temperature-like
   threshold based on historical anomaly levels. This eliminates the need to
   manually set alarm levels for each individual frequency subrange. This is
   especially true for equipment that comes with little a-priori information,
   such as small ubiquitous equipment like pumps, conveyor belts, or fans.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-canvas-iqunet.jpg"
     alt="Screenshot of the Canvas plugin of the iQunet Edge server"
     width="100%"
     style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
   />
   <figcaption>
     Figure 25: The Canvas plugin of the iQunet edge server allows the user
     to build custom dashboards. In this screenshot, the page shows the 50%
     median rolling estimate of the autoencoder anomaly score for 4 sensors
     on the vibratory screen. <br><i>[Click image to enlarge]</i>
   </figcaption>

   To minimize false alarms, the output of the loss detector is smoothed using
   a rolling window quantile estimator before being compared to the threshold.
   A lower quantile with a larger window reduces the likelihood of false alarms
   but slows response time. Conversely, a higher quantile increases sensitivity
   at the expense of more false positives. Using multiple quantiles with a
   single threshold allows for alarms with varying severity levels.

   <img
     src="{{ site.baseurl }}/assets/images/vibration-anomaly-quantiles.png"
     alt="Anomaly score with 5%, 50% and 95% rolling window quantiles"
     width="517px"
     style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);"
   />
   <figcaption>
     Figure 26: iQunet dashboard showing the 5%, 50% and 95% rolling window
     anomaly anomaly score quantiles. The same data is also available in
     OPC-UA (/MQTT) for export to any factory SCADA (/IoT) platform.
   </figcaption>
   
   When an alarm is triggered, the anomaly score continues to provide insights
   into the stability of the anomaly. It brings an estimate of how rapidly the
   machine is deviating from its operational baseline. It provides useful data
   in how fast an intervention must be planned.

   ---

### Conclusion

   Wireless vibration sensors combined with machine learning provide a powerful
   solution for the day-to-day anomaly detection in industrial screens. By
   continuously monitoring machine behavior and processing data through
   deep-learning ML models, emerging random faults can be detected before they
   become catastrophic, by leveraging the strength of big data to balance the
   reduced sensitivity/bandwidth compared to piezo sensor technology.

   This predictive approach minimizes unplanned downtime, and allows to align
   repairs with the scheduled maintenance. The ability to automatically
   detect complex issues without relying on manual inspections or preset
   thresholds highlights the potential of integrating machine learning into
   industrial maintenance strategies, bringing the required level of
   understanding from expert vibration analist to anyone with a good technical
   background.

   <video width="90%" controls loop autoplay muted style="margin-left: 1em;">
     <source src="{{ site.baseurl }}/assets/videos/vibration-iqunet-ads.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

---

For more detailed technical insights and support, explore our
[documentation](https://iqunet.com/resources/) and
[case studies](https://iqunet.com/resources/case-studies/case-study-1-international-airport/),
or contact our [support team](https://iqunet.com/contact/).
