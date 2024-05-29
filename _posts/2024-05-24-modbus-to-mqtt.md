---
title: "Modbus to MQTT"
date: 2024-05-24 12:06:19 +0200
categories: blog
toc: true
toc_sticky: true
---
### Mission: Publish Modbus over MQTT, plot in Python

![LoRaWAN to OPC UA]({{ site.baseurl }}/assets/images/modbus-mqtt-python.svg)

<span style="background-color: #ffff0054">
**Note:** This tutorial uses the iQunet Industrial Edge Server
[[link](https://iqunet.com/products/servers/)].
<br>A demo gateway endpoint is provided for the purpose of this guide.
</span>

> **Modbus** is a wired communication protocol for industrial automation
> and data exchange between devices like sensors and PLC controllers.
> Visit [modbus.org](https://modbus.org).
>
> - **Modbus-RTU:** Uses serial wired communication (RS-232/RS-485) for
>   short-distance, point-to-point, or multi-drop connections.
> - **Modbus-TCP:** Runs over Ethernet, using TCP/IP for integration with
>   modern IT systems. A gateway is used to convert between Modbus-RTU and -TCP.

> **MQTT** (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe
> network protocol designed for resource-constrained devices and low-bandwidth,
> high-latency networks. It is widely used in internet-oriented services,
> particularly for IoT applications. In contrast to OPC-UA, the payload format
> is not part of the specification. Visit [mqtt.org](https://mqtt.org).

In this tutorial, you will learn how to:
- Connect a **Modbus-RTU** motor drive to the iQunet Industrial Edge Server.
- Understand the steps how sensor data is stored in the **local OPC-UA database**.
- Next, publish this sensor data in realtime to an **MQTT broker**.
- Subscribe to the MQTT broker using **Python** for post-processing and visualization.
<br>
<hr>

### Typical Modbus-to-MQTT Information Flow

In a typical Modbus/MQTT monitoring setup, an industrial device,
<span>&mdash;&nbsp;</span>such as a **motor drive**<span>&nbsp;&mdash;</span>
is connected to a **Modbus-TCP gateway** via an RS-485 serial interface.
The gateway converts between the synchronous Modbus-RTU protocol and the
asynchronous Modbus-TCP ethernet network protocol. This allows the use of
standard networking equipment. Some devices natively support Modbus-TCP,
which eliminates the need for a gateway.

![Typical LoRaWAN setup]({{ site.baseurl }}/assets/images/typical-modbus.svg)
<figcaption>figure 1: Typical Modbus to MQTT information flow</figcaption>

A **Modbus-TCP master** actively polls connected devices to extract data, which
is subsequently decoded from binary to a user-friendly format, typically
JSON. This JSON data is then published to an MQTT platform, either on-premise
or cloud-based, such as the HiveMQ **MQTT broker**.

An **MQTT subscriber** retrieves the data from the broker and stores it in a database.
This database then serves as a data source for real-time or historical operational
dashboards, providing the user with insight into emerging faults, predictive
maintenance or energy efficiency.

{: .notice}
*Configuring the Modbus-TCP master and decoding data demand deep understanding of
each device's register map, requiring significant expertise and effort with every
new device integration.<br>
An example of such a manual setup procedure can be found here 
[hivemq.com <i style="margin: 0.2em; font-size: 0.7em" class="fa-solid fa-arrow-up-right-from-square"></i>](https://www.hivemq.com/blog/modbus-mqtt-integration-c-sharp-gateway-hivemq-mqtt-client/).
<br>
<br>
The required expertise and effort may lead to a higher TCO and project delays
than initially projected, making a ready-to-use solution an attractive and efficient
alternative.*

<hr>

### A Single-Board Modbus-to-MQTT Setup

The Modbus-TCP gateway, Modbus master and MQTT publisher can all be integrated in
a single board computer (SBC), such as is the case for the iQunet Edge Server
[[link](https://iqunet.com/products/servers/)].
Data collected via Modbus is first decoded and stored in the on-board **OPC-UA historian
database**.
<br>
This data can be routed (LAN/VPN) and accessed with the embedded dashboard
webserver or via various protocols, including OPC-UA, GraphQL or CSV. In a
second step, realtime updates in the OPC-UA server can be linked to the
onboard MQTT publisher for integration with third-party IoT platforms.
<br>

![iQunet LoRaWAN setup]({{ site.baseurl }}/assets/images/iqunet-modbus.svg)
<figcaption>figure 2: iQunet single-server Modbus/MQTT gateway setup.</figcaption>

In this tutorial, the **<span style="background-color:#ff9494">red route</span>**
indicated in figure 2 will be used. The motor drive is connected via an FTDI-232R
galvanically isolated interface to the iQunet Server, which polls the drive at a
configurable interval. The payload is then decoded, unpacked and written to the
**built-in database**.

### Publishing to MQTT
When a new measurement is written into the database, the OPC-UA server triggers
a callback that activates the MQTT publisher. The new measurement is first
converted into **JSON format** and published to the MQTT broker.<br>
The **topic of the MQTT message** is derived from the path of the corresponding
data point in the OPC-UA tree (figure 3).

![iQunet OPC-UA]({{ site.baseurl }}/assets/images/iqunet-opcua-mqtt.svg)
<figcaption>figure 3: iQunet embedded OPC-UA server API</figcaption>

In this tutorial, a Python program will then subscribe to the specified topic
on the MQTT broker and display the incoming data on a real-time updated graph.
<hr>

### Motor Drive + Modbus Hardware Setup

Figure 4 shows the minimal setup required to publish real-time motor drive data
via MQTT. This configuration includes the **inverter drive** itself, an Ethernet
**network switch**, the **iQunet server**, and an (optional) 4G mobile
**access point** (AP), which serves as a temporary placeholder for, for example,
a company VLAN. The Modbus-RTU to TCP gateway is omitted because the drive
depicted in Figure 4 is equipped with a Modbus-TCP communication module.

With this setup, MQTT data can be transmitted to either a private or a public
internet-based MQTT broker.

![Modbus Example Hardware Setup]({{ site.baseurl }}/assets/images/iqunet-setup.svg)
<figcaption>figure 4: The setup with motor drive, iQunet server and access point.
</figcaption>

For the remainder of this tutorial, the Invertek Optidrive E3 will be used.
The Optidrive inverter supports both Modbus-RTU and Modbus-TCP via an additional
module. However, because the Profinet IO module occupies the sole available slot
for PLC drive control, the on-board Modbus-RTU is used. A separate RS-485 to USB
converter is used for **monitoring** the drive parameters in **read-only mode**.
<br>

![Profinet Control and Modbus Monitor loop]({{ site.baseurl }}/assets/images/modbus-monitor-loop.svg)
<figcaption>figure 5: Optidrive E3 - PLC control via Profinet and monitoring via Modbus-RTU.
</figcaption>
<hr>

### Scanning for Modbus Devices
After the hardware is connected and powered up as shown in figure 4, the
Optidrive E3 must be added to the list of monitored devices in the iQunet
server software.

The first step involves activating both the Modbus-TCP and the Modbus-RTU modules
in the dashboard of the iQunet server. For this, click on the Config button
<i style="margin: 0.2em; font-size: 0.7em" class="fa-solid fa-wrench"></i> in
the menu bar, as shown in Figure 6:

![iQunet Enable Modbus in Dashboard]({{ site.baseurl }}/assets/images/iqunet-modbus-enable.svg)
<figcaption>figure 6: Enable the Modbus-TCP master and the Modbus-RTU gateway.</figcaption>

- The **Modbus-TCP module** provides **Modbus master** functionality, which
includes probing the connected devices at regular intervals and forwarding data
to the OPC-UA historian database.
- The **Modbus-RTU module** enables the drivers for the FTDI FT232R USB-to-serial
interface and serves as a **gateway** for the Modbus master to communicate with
RTU devices.

After both Modbus modules are enabled, the Home menu <i class="fa-solid fa-home"></i>
will display a new Modbus Master and Gateway node in the OPC-UA device list.

The Modbus Master allows **scanning a single IP or subnet** for known devices
(figure 7):

![iQunet Modbus TCP Scanner]({{ site.baseurl }}/assets/images/iqunet-modbus-tcp-scan.svg)
<figcaption>figure 7: Scanning a LAN subnet for Modbus-TCP devices.</figcaption>

The scanner is also capable of scanning not only for **Modbus slave devices** on
the **local network** (Ethernet or WiFi) but also for **remote devices** via any
configured **Wireguard VPN** endpoint on the iQunet server.

The **Modbus-RTU gateway** operates similarly, scanning all **slave Unit IDs**
within the configured range, as illustrated in Figure 8. Because Modbus-RTU is a
synchronous **serial protocol**, parallel scanning is not feasible. Therefore,
probing the full range of all slave IDs from 1 to 247 may take a minute or two.

![iQunet Modbus RTU Scanner]({{ site.baseurl }}/assets/images/iqunet-modbus-rtu-scan.svg)
<figcaption>figure 7: Scanning all Unit IDs of a Modbus-RTU network.</figcaption>
<hr>

### Auto-Detection of Modbus Devices
When the iQunet server detects a Modbus slave device on the network, it attempts
to identify the specifics of the slave for auto-configuration purposes. This
process serves two main objectives:
- **Device Identification**: A unique device MAC address is derived from the
  device serial number. This allows for flexible remapping of IP addresses or
  slave unit IDs, with monitoring data **tied to the device serial** rather than
  the location in the network or the MAC address of the Modbus network card.
- **Device Type Detection**: This is crucial for **automatic payload decoding**.
  iQunet provides customized payload decoders upon request. The configuration
  for the end-user is limited to basic parameters such as the polling interval
  and the selection of data to be published to MQTT. This **simplifies the
  commissioning** of new devices in the field, reducing the setup time to a
  matter of minutes.

In Figure 8 below, the **Optidrive E3** inverter is detected on the local
**Modbus-RTU gateway** at **Unit ID 1**. The dashboard automatically adapts to
the device specifics and displays the most important configuration highlights
of the device, such as the serial number, hardware model, and current
configuration (e.g., closed-loop **vector control** mode):

<img src="{{ site.baseurl }}/assets/images/iqunet-optidrive-eco-status.svg" alt="iQunet Optidrive Eco dashboard">
<figcaption>figure 8: Auto-detection and configuration of the Modbus payload decoder.</figcaption>

In addition to the static configuration, **real-time drive** and
**historical parameters** are also available in the dashboard. The generic motor
drive section (Figure 9) displays the most common parameters.

<img src="{{ site.baseurl }}/assets/images/iqunet-optidrive-eco-monitor.svg" alt="iQunet Generic Motor drive monitor">
<figcaption>figure 9: Displaying real-time and historical drive parameters.</figcaption>

While the dashboard provides a graphical summary of the drive status, much more
detailed information about drive parameters and historical logs can be accessed
by directly **browsing the OPC-UA node tree** of the internal OPC-UA server. To
do this, click on the OPC-UA icon in the left menu:

<img src="{{ site.baseurl }}/assets/images/iqunet-optidrive-eco-opcua-dashboard.svg" alt="iQunet OPC-UA browser">
<figcaption>figure 10: Accessing and exporting drive parameters via the OPC-UA browser.</figcaption>

The built-in OPC-UA browser allows immediate export to **Google Sheets** or a
plain **CSV file**. Additionally, as shown in Figure 10, any variable node of the
OPC-UA tree can be enabled for **publication via MQTT** to an external broker.
<hr>

### Direct Access of Modbus Data via OPC-UA
All **historical Modbus data** is stored in the **OPC-UA database** of the iQunet
server. It can either be browsed via the dashboard of the web interface, or through
**third-party OPC-UA clients** such as UaExpert, a popular OPC-UA client developed
by Unified Automation
[[unified-automation.com](https://www.unified-automation.com/products/development-tools/uaexpert.html)].

Figure 11 shows the configuration of UaExpert to connect to the iQunet OPC-UA
server at address 192.168.10.101, port 4840. Both encrypted and non-encrypted
connections are supported.

![UaExpert Setup]({{ site.baseurl }}/assets/images/uaexpert-setup.svg)
<figcaption>figure 11: Unified Automation UaExpert OPC-UA client connection setup.</figcaption>

When the **UaExpert client** is successfully connected to the **iQunet OPC-UA server**,
direct access is provided to all real-time motor drive parameters, metadata and
historical values as stored in the local database.

<img src="{{ site.baseurl }}/assets/images/iqunet-optidrive-eco-opcua-uaexpert.svg" alt="UaExpert OPC-UA browser">
<figcaption>figure 12: Accessing historical data with the UaExpert OPC-UA client.</figcaption>
<hr>

<div class="notice" markdown="1">
### OPC-UA vs MQTT: Payload Format and Data Types
**MQTT** is a widely used protocol for large-scale, **multi-site IoT deployments**.
However, it does not define a specific data format. **JSON** is commonly used
as the payload encoding, but it lacks data type definitions for the payload,
and thus needs careful manual coordination between data publishers and
subscribers to ensure mutual compatibility.

On the other hand, **OPC-UA** is highly suitable for low latency networks,
real-time data exchange, and has **well-defined object type formatting**.
It allows OPC-UA clients to autonomously resolve data type definitions without
user intervention. However, the protocol is currently not widely used in
internet-oriented big data platforms.

For maximum flexibility, the iQunet server supports both protocols and employs
the following strategy to link the OPC-UA core system to the MQTT subsystem:

- The OPC-UA node **tree path is used as the topic** for publishing data via MQTT.
  A user-definable "Root/" can be prepended to the path (default: server name).
- The **JSON payload** consists of a dictionary dump, which includes the
  **numerical, string, or array data**, and the **source-** and **serverTimestamp**
  in ISO-8601 format.
</div>

### Enabling the MQTT Subsystem for the iQunet Server
Enabling the MQTT subsystem for the iQunet server is straightforward.

- Click on the **MQTT icon** in the left-hand menu.
- Fill in the **MQTT broker host details** and credentials.<br>
  Optionally, set a custom **Client ID** (also serves as the root of the topics).
- If supported by the broker, select the **TLS** encryption option.<br>
  Finally, toggle the button "MQTT OFF" to **"MQTT ON"**.
- If the <span style="background-color: #abffab">**ONLINE**</span> icon is
  highlighted, the setup is complete and operational.

![iQunet Server MQTT Configuration Menu]({{ site.baseurl }}/assets/images/iqunet-mqtt-configuration.svg)
<figcaption>figure 13: MQTT Configuration Menu in the iQunet Dashboard.</figcaption>

The MQTT setup menu also displays a list of all published nodes and their
respective topics. To add a node to this list, browse to the desired node in
the OPC-UA tree and click the **MQTT "publish"** button.

![iQunet Server MQTT Add Published Node]({{ site.baseurl }}/assets/images/iqunet-mqtt-addnode.svg)
<figcaption>figure 14: Publish a new node via MQTT in the iQunet Dashboard.</figcaption>

### Testing the MQTT Setup
To verify the MQTT setup, a **web-based MQTT client** will be connected to the
broker to subscribe to the published data. Since browsers do not support raw
TCP sockets, the Websocket port of the broker will be used.

First, open the **HiveMQ MQTT Client**
[[hivemq.com](https://www.hivemq.com/demos/websocket-client/)], and setup the
broker host and TLS Websocket port as below. Then click connect.
- **host**: broker.hivemq.com
- **port**: 8884 (wss://)

![Connecting the HiveMQ MQTT demo client]({{ site.baseurl }}/assets/images/hivemq-mqtt-client.svg)
<figcaption>figure 15: Connect the HiveMQ MQTT client to wss://broker.hivemq.com.
</figcaption>

Next, click **"Add New Topic Subscription"** and choose the topic to
subscribe to. Use a multilevel wildcard (#) to subscribe to all topics at once.
More info here [[hivemq.com](https://www.hivemq.com/blog/mqtt-essentials-part-5-mqtt-topics-best-practices/)]

For example, if the topic published to by the iQunet Server is<br>
`SERN-dca632xxxxxx/Objects/b1:dd:1f:e9/inverterTemperature`,
then subscribe to<br>
`SERN-dca632xxxxxx/#` to capture all messages from this server.

![Subscribing the HiveMQ client to a topic]({{ site.baseurl }}/assets/images/hivemq-mqtt-subscribe.svg)
<figcaption>Figure 16: Subscribing to a topic and viewing incoming JSON data.</figcaption>

If the configuration is correct, JSON packets will start arriving as soon as
they are published by the iQunet Server!
<hr>

### Subscribing to MQTT and Plotting with Python
This section provides Python boilerplate code to demonstrate how to subscribe
to the MQTT broker, receive data from the iQunet server, and visualize this
data in real-time.

<video width="640" height="360" controls loop autoplay muted>
  <source src="{{ site.baseurl }}/assets/videos/test3.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

The [Paho MQTT client](https://pypi.org/project/paho-mqtt/) is used for handling
MQTT communication, and [Matplotlib](https://pypi.org/project/matplotlib/)
is used for plotting the data.

- **MQTT Client Configuration**: The Paho MQTT client connects to the HiveMQ
   broker at `broker.hivemq.com` on TCP/TLS port `8883` and subscribes to the
   specified topic where the iQunet server publishes data.

- **Message Handling**: When a message is received, the `on_message` callback
   parses the JSON payload and appends the data to an in-memory `cache`.
   The `data_event` signals to the plotting thread that new data is available.

- **Plotting**: The `update_plot` function retrieves data from the cache,
   extracts timestamps and values, and updates the plot. The `FuncAnimation`
   class from Matplotlib refreshes the plot every second.

```python
from collections import deque
from datetime import datetime
from functools import partial
import json
import threading
import time

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import paho.mqtt.client as mqtt

# MQTT setup
BROKER = 'broker.hivemq.com'
PORT = 8883
TOPIC = 'SERN-dca632c03aee/Objects/b1:dd:1f:e9/inverterTemperature'

# In-memory storage
cache = deque(maxlen=1024)

# Event to trigger plot updates
data_event = threading.Event()

def on_connect(client, userdata, flags, rc, properties):
    print(f'Connected with result code {rc}')
    assert rc == 0
    client.subscribe(TOPIC)

def on_message(client, userdata, message):
    payload = json.loads(message.payload)
    cache.append(payload)
    data_event.set()

def start_mqtt_loop():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    return client

def update_plot(frame, ax):
    if not data_event.is_set():
        time.sleep(1)
        return
    c = list(cache)
    x = [datetime.fromisoformat(pl['SourceTimestamp']) for pl in c]
    y = [pl['Value'] for pl in c]

    ax.clear()
    ax.plot(x, y, marker='o')
    ax.set_ylim(20, 70)
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Inverter Temperature')
    plt.xlabel('Timestamp')
    plt.ylabel('degC')
    data_event.clear()

if __name__ == '__main__':
    client = start_mqtt_loop()
    try:
        fig, ax = plt.subplots()
        func = partial(update_plot, ax=ax)
        ani = FuncAnimation(fig, func, interval=1000, cache_frame_data=False)
        plt.show()
    finally:
        client.disconnect()
```

<hr>

### Conclusion
Throughout this tutorial, we've demonstrated how to integrate a LoRaWAN sensor
with the iQunet Industrial Edge Server, store sensor data in a local OPC-UA
database, and visualize the data using Python. By following these steps, you
have successfully set up a **private LoRaWAN network** and accessed **real-time
and historical data** through the embedded OPC-UA server.

Beyond the basics covered in this guide, iQunet offers extensive capabilities
for more advanced data processing tasks. These include handling complex datasets
like vibration data, implementing machine learning techniques for predictive
maintenance, and enabling custom software adaptations for specific industrial
needs.

<span style="background-color: #ffff0054">
For further exploration and support, check out our
[**documentation**](https://iqunet.com/resources/), get new ideas from some
[**case studies**](https://iqunet.com/resources/case-studies/case-study-1-international-airport/)
or reach out to our [**support team**](https://iqunet.com/contact/).
Happy data monitoring!
</span>
