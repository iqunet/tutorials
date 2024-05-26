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
a callback that activates the MQTT publisher. The new measurement is then
converted into **JSON format** and published to the MQTT broker.<br>
The **topic of the MQTT message** is derived from the path of the corresponding
data point in the OPC-UA tree (figure 3).

![iQunet OPC-UA]({{ site.baseurl }}/assets/images/iqunet-opcua-mqtt.svg)
<figcaption>figure 3: iQunet embedded OPC-UA server API</figcaption>

For this tutorial, a Python program will subscribe to the specified topic on
the MQTT broker and display the incoming data on a real-time updated graph.
<hr>

### LoRaWAN Hardware Setup

Figure 4 shows a modular setup for a **private LoRaWAN network**. It consists
of an **SX1302 LoRa Radio** receiver, an iQunet Edge SBC (database and OPC-UA
server) and an (optional) 4G mobile router. The router is the temporary
placeholder for -for example- a company VLAN.

![iQunet Base Setup]({{ site.baseurl }}/assets/images/iqunet-setup.svg)
<figcaption>figure 4: The setup with SX1302 concentrator module,
OPC-UA server and mobile network</figcaption>

For the purpose of this tutorial, the Dragino LSN50v2-S31 temperature and
humidity LoRaWAN sensor will be used. Both the LSN50 and the iQunet server
understand the OTAA (over-the-air activation) protocol v1.0.4. OTAA allows to
automatically generate and exchange the network and application security keys
between sensor and the target application.
<br>

<img src="{{ site.baseurl }}/assets/images/lsn50v2-s31.svg" alt="Dragino LSN50v2-S31" width="400"/>
<figcaption>figure 5: Dragino LSN50v2-S31 LoRaWAN temperature and humidity sensor.</figcaption>
<hr>

### Connecting a new LoRaWAN sensor
After the battery of the Dragino LSN50 sensor is inserted, the configuration
dashboard of the iQunet server shall display a new LoRaWAN device under the LoRa
Radio Module. The devEUI found on the LSN50 sensor should match the devEUI as
displayed in the dashboard.

![iQunet Dashboard new LoRaWAN]({{ site.baseurl }}/assets/images/iqunet-new-lorawan.svg)
<figcaption>figure 6: The LoRaWAN sensor is detected and a new device LoRaWAN
device is created in the sensor tree.</figcaption>

Communication with the sensor will not start until the encryption key is
set up. For this, click on the "Edit" button next to the **Application Key**
and fill in the 32-character key that comes with the Dragino Device.
The AppKey (also known as the JOIN key) is only used once during the setup of
the device.
<br>

![iQunet LoRaWAN AppKey]({{ site.baseurl }}/assets/images/iqunet-key-lorawan.svg)
<figcaption>figure 7: Setup of the LoRaWAN Application Key in the dashboard.</figcaption>

If the **Application Key** is correct, the sensor and the iQunet server will
generate 2 new session keys:
- The **Network Session Key** (NwkSKey) is used for all communications related to
  the LoRaWAN protocol (e.g. regional parameters and frequencies).
- The **Application Session Key** (AppSKey) is used for the exchange of sensor
  data, in this particular case temperature and humidity.
<br>

![iQunet LoRaWAN Session Keys]({{ site.baseurl }}/assets/images/iqunet-sessionkeys-lorawan.svg)
<figcaption>figure 8: Secure Session keys are calculated from the Application Key.</figcaption>

After all OTAA keys have been successfully set up, the actual **uplink of
sensor data** starts. The iQunet Server automatically detects the sensor model
and selects the corresponding **payload decoder** module. Binary sensor data is
now unpacked into the appropriate fields in the OPC-UA tree. The dashboard will
adjust and display all relevant information. For example, the LSN50v2-S31 will
transmit temperature, humidity and battery power, as shown in figure 9:
<br>

![iQunet custom dashboard]({{ site.baseurl }}/assets/images/iqunet-lsn50.svg)
<figcaption>figure 9: Dashboard will adjust to the sensor type.</figcaption>

When available, sensor settings can be adjusted via the **LoRaWAN downlink**
channel. For example, the LSN50 allows the on-the-fly setup of the measurement
interval. The configuration can be adjusted not only in the dashboard but also
programmatically via the OPC-UA, MQTT, or GraphQL interface. This allows for
**automated provisioning** of multiple sensors.
<hr>

### Embedded OPC-UA Client
At this point, the sensor has successfully joined the private LoRaWAN network
and incoming measurements are stored into the **local database**. Historical
data can be retrieved via the OPC-UA "**historical access**" extension.

Click the OPC-UA tab in the dashboard to open the embedded OPC-UA browser,
as shown in figure 10:

![iQunet OPC-UA browser]({{ site.baseurl }}/assets/images/iqunet-dashboard-opcua.svg)
<figcaption>figure 10: Embedded OPC-UA client and browser.</figcaption>
<hr>

### UaExpert OPC-UA Client
The server listens on all network interfaces (LAN, WLAN, wireguard VPN) at **port 4840**.

For example, when the ethernet cable is connected to LAN network 192.168.10.0/24:
<br>

| Service             | URL                                      |
|---------------------|------------------------------------------|
| WebServer           | http://192.168.10.101:8000/dashboard     |
| GraphQL server      | http://192.168.10.101:8000/graphql       |
| **OPC-UA server**   | **opc.tcp://192.168.10.101:4840**        |

The OPC-UA server is also accessible by all third-party client software, such
as UaExpert, a popular OPC-UA client developed by Unified Automation
[[unified-automation.com](https://www.unified-automation.com/products/development-tools/uaexpert.html)].

Figure 11 shows the configuration of UaExpert to connect to the iQunet OPC-UA
server at address 192.168.10.101, port 4840. Both encrypted and non-encrypted
connections are supported.

![UaExpert Setup]({{ site.baseurl }}/assets/images/uaexpert-setup.svg)
<figcaption>figure 11: Unified Automation UaExpert OPC-UA client connection setup.</figcaption>

When the UaExpert client is successfully connected to the iQunet OPC-UA server,
direct access is provided to all realtime measurements, metadata and historical
values as stored in the local database.

![UaExpert History view]({{ site.baseurl }}/assets/images/uaexpert-history.svg)
<figcaption>figure 12: Unified Automation UaExpert OPC-UA client: history view.</figcaption>
<hr>

### Post-processing OPC-UA data with Python
The next step in this tutorial is connecting to the OPC-UA server using the
Python programming language. This allows for flexible **postprocessing**, such
as smoothing data, sending automated alarm messages or creating your own custom
aggregate dashboards with realtime data.

Below is the boilerplate Python code to connect to the OPC-UA server, extract
the temperatures from the last day, and generate a basic plot.
Three external libraries are used for this:
*[opcua-asyncio](https://pypi.org/project/asyncua/)*,
*[numpy](https://pypi.org/project/numpy/)* and
*[matplotlib](https://pypi.org/project/matplotlib/)*.

```python
import asyncio
import datetime
import matplotlib.pyplot as plt
import numpy as np
from asyncua import Client

def moving_avg(values, window):
    padded = np.pad(values, (window//2, window-1-window//2), mode='edge')
    window = np.ones(window) / window
    smooth = np.convolve(padded, window, mode='valid')
    return smooth

async def main():
    url = 'opc.tcp://192.168.10.101:4840'
    path = ['0:Objects', '2:31:86:84:11', '2:boardTemperature']

    async with Client(url=url) as client:
        root = client.nodes.root
        node = await root.get_child(path)

        # read history
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        end_time = datetime.datetime.now()
        history = await node.read_raw_history(start_time, end_time)

        # Extracting values
        times = [x.SourceTimestamp for x in history]
        values = [x.Value.Value for x in history]

        # Smooth
        smooth = moving_avg(values, window=5)

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(times, values, linestyle= '', marker='o', label='Original')
        plt.plot(times, smooth, linestyle='-', color='red', label='Smoothed')
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.title('Temperature')
        plt.grid(True)
        plt.legend()
        plt.show()

if __name__ == '__main__':
    asyncio.run(main())

```

![Temperature Plot]({{ site.baseurl }}/assets/images/temperature_plot.png)
<figcaption>figure 13: Smoothed temperature plot using opcua-asyncio and matplotlib.</figcaption>
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
