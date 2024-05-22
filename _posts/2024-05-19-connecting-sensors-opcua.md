---
layout: post
title: "LoRaWAN to OPC-UA Gateway"
date: 2024-05-19 22:10:15 +0200
categories: tutorial
---

* TOC
{:toc}

# Tutorial: LoRaWAN sensor to Python graph

LoRaWAN (Long Range Wide Area Network) is a wireless communication protocol
designed for low-power, long-range, and low-data-rate applications, making it
ideal for IoT devices. For more detailed information,
visit [lora-alliance.org](https://lora-alliance.org/about-lorawan/).

<span style="background-color: yellow">
**Note:** This tutorial makes use of the iQunet Industrial Edge Server.
<br>A demo gateway is provided for the purpose of this guide.
</span>

You will learn how to:
- Connect a **LoRaWAN sensor** to the iQunet Industrial Edge Server.
- Understand how sensor data is stored into the **local OPC-UA database**.
- Test the OPC-UA server connection using **UaExpert**.
- Use **Python** to connect to the OPC-UA server for visualization and post-processing.
<br>
<br>
![LoRaWAN to OPC UA]({{ site.baseurl }}/assets/images/lora-opc-python.svg)

## Typical LoRaWAN Setup

In a standard LoRaWAN setup, a sensor sends data to a **gateway**, which
then forwards the encrypted data to a **network server** over the internet.
The network server buffers the data and forwards it to an **application server**
via MQTT. The application server decrypts and unpacks the binary sensor data
and stores the measurement in a database, where it can be retrieved by,
for example, **dashboarding software** for visualization.

![Typical LoRaWAN setup]({{ site.baseurl }}/assets/images/typical-lora.svg)
<figcaption>figure 1: Typical LoRaWAN setup for large networks</figcaption>
<br>
For a simple one-time setup, this multi-step process can be quite challenging,
especially when integrating software from different vendors.

## An Integrated Approach

The LoRaWAN gateway, network/application server and database can all be
integrated in a single device, such as is the case for the iQunet Edge Server.
The result is a secure standalone LoRaWAN network which only requires a **local
network** (LAN) connection for API data access. Sensor data is immediately written
to the **local database** and can be accessed via various protocols: OPC-UA, GraphQL,
MQTT, CSV or the internal web interface.
<br>

![iQunet LoRaWAN setup]({{ site.baseurl }}/assets/images/iqunet-lora.svg)
<figcaption>figure 2: iQunet single-server LoRaWAN setup for
medium size networks (e.g. 250 devices)</figcaption>
<br>
For this tutorial, the **<span style="background-color:#ff9494">red route</span>**
as indicated in figure 2 will be used. The iQunet Server will receive the
LoRaWAN packets via the attached **LoRa concentrator** radio module, **decode
and unpack** the payload and store the data in the **build-in database**.
<br>

### The OPC-UA server interface

After being written to the database, the data is made accessible via the 
**embedded OPC-UA server**.
OPC-UA (Open Platform Communications Unified Architecture)
is a machine-to-machine communication protocol for industrial automation
developed for secure, realtime data exchange. Visit
[opcfoundation.org](https://opcfoundation.org/about/opc-technologies/opc-ua/).

Measurements related to a single LoRaWAN sensor are organized under the
corresponding DevEUI node of that sensor in the OPC-UA tree (figure 3). 

![iQunet OPC-UA]({{ site.baseurl }}/assets/images/iqunet-opcua.svg)
<figcaption>figure 3: iQunet embedded OPC-UA server API</figcaption>
<br>


## LoRaWAN Hardware Setup

Figure 4 shows a modular setup for a **private LoRaWAN network**. It consists
of an **SX1302 LoRa Radio** receiver, an iQunet Edge SBC (database and OPC-UA
server) and an (optional) 4G mobile router. The router is the temporary
placeholder for -for example- a company VLAN.

![iQunet Base Setup]({{ site.baseurl }}/assets/images/iqunet-setup.svg)
<figcaption>figure 4: The setup with SX1302 concentrator module,
OPC-UA server and mobile network</figcaption>
<br>

For the purpose of this tutorial, the Dragino LSN50v2-S31 temperature and
humidity LoRaWAN sensor will be used. Both the LSN50 and the iQunet server
understand the OTAA (over-the-air activation) protocol V1.0.4. OTAA allows to
automatically generate and exchange the network and application security keys
between sensor and the target application.
<br>

<img src="{{ site.baseurl }}/assets/images/lsn50v2-s31.svg" alt="Dragino LSN50v2-S31" width="400"/>
<figcaption>figure 5: Dragino LSN50v2-S31 LoRaWAN temperature and humidity sensor.</figcaption>
<br>

After the battery of the Dragino LSN50 sensor is inserted, the configuration
dashboard in iQunet server shall display a new LoRaWAN device under the LoRa
Radio Module. The DevEUI found on the LSN50 sensor should match the devEUI as
displayed in the dashboard.

![iQunet Dashboard new LoRaWAN]({{ site.baseurl }}/assets/images/iqunet-new-lorawan.svg)
<figcaption>figure 6: The LoRaWAN sensor is detected and a new device LoRaWAN
device is created in the sensor tree.</figcaption>
<br>

Communication with the sensor will not start before the encryption key is
set up. For this, click on the "Edit" button next to the **Application Key**
and fill in the 32-character key that comes with the Dragino Device.
The AppKey (aka JOIN key) is only used once during the setup of the device.
<br>

![iQunet LoRaWAN AppKey]({{ site.baseurl }}/assets/images/iqunet-key-lorawan.svg)
<figcaption>figure 7: Setup of the LoRaWAN Application Key in the dashboard.</figcaption>
<br>

If the **Application Key** is correct, the sensor and the iQunet server will
generate 2 new session keys:
- The **Network Session Key** (NwkSKey) is used for all communications related to
  the LoRaWAN protocol (e.g. regional parameters and frequencies).
- The **Application Session Key** (AppSKey) is used for the exchange of sensor
  data, in this particular case temperature and humidity.
<br>

![iQunet LoRaWAN Session Keys]({{ site.baseurl }}/assets/images/iqunet-sessionkeys-lorawan.svg)
<figcaption>figure 8: Secure Session keys are calculated from the Application Key.</figcaption>
<br>

After all OTAA keys have been successfully set up, the actual **uplink of sensor
data** will start. The iQunet Server automatically detects the sensor model and
selects the corresponding **payload decoder** module. Binary sensor data is now
unpacked into the appropriate fields in the OPC-UA tree. The dashboard will
adjust and display all relevant information. For example, the LSN50v2-S31 will
transmit temperature, humitidy and battery power, as shown in figure 9:
<br>

![iQunet custom dashboard]({{ site.baseurl }}/assets/images/iqunet-lsn50.svg)
<figcaption>figure 9: Dashboard will adjust to the sensor type.</figcaption>
<br>

When available, sensor settings can be adjusted via the **LoRaWAN downlink**
channel. For example, the LSN50 allows the on-the-fly setup of the measurement
interval. The configuration can not only be adjusted in the dashboard, but also
programmatically via the OPC-UA, MQTT or GraphQL interface. This allows for
**automated provisioning** of multiple sensors.
<br>

At this point, the sensor has successfully joined the private LoRaWAN network
and incoming measurements are stored into the **local database**. Historical
data can be accessed via the OPC-UA "**historical access**" extension. Click on
the OPC-UA tab in the dashboard to open the embedded OPC-UA browser (figure 10).
The browser allows to manually export data to Google Sheets, or as a CSV file.

![iQunet OPC-UA browser]({{ site.baseurl }}/assets/images/iqunet-dashboard-opcua.svg)
<figcaption>figure 9: Embedded OPC-UA client and browser.</figcaption>
<br>

The OPC-UA server is also accessible by all 3rd party client softwares such as
the UaExpert Client. The server is listening on all network interfaces
(LAN, WLAN, wireguard VPN) at **port 4840**.

For example, for the demo iQunet server connected to LAN network 192.168.10.0/24:

| Service             | URL                                      |
|---------------------|------------------------------------------|
| WebServer           | http://192.168.10.101:8000/dashboard     |
| GraphQL server      | http://192.168.10.101:8000/graphql       |
| OPC-UA server       | opc.tcp://192.168.10.101:4840            |



<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

===================

 were combined into a single unit? This integration could operate as a standalone LoRaWAN network within a local area network (LAN), eliminating the need for an internet connection.

[Figure here: Diagram of integrated server setup]

In this scenario, the server would decode LoRaWAN packets, extract the payload from binary to SI units, and organize the data in an OPC UA tree structure under the sensor's MAC address. This structured approach allows for easy data access and management.

[Figure here: Example of OPC UA tree structure]

## Step-by-Step Guide

### Step 1: Power Up the Gateway
Connect your [Your Product Name] gateway to a power source. You should see the power indicator light up.

### Step 2: Connect Sensors
Attach your LoRaWAN or Modbus sensors to the gateway. Refer to the diagrams below for correct connections.

### Step 3: Configure the Gateway
Access the gateway's web interface by entering its IP address in your browser. Login with your credentials.

### Step 4: Setup OPC UA
Navigate to the OPC UA settings in the menu. Enter the necessary details to configure the connection.

### Step 5: Install FreeOpcUa
If you haven't installed FreeOpcUa, follow this guide: [FreeOpcUa Installation](#).

### Step 6: Connect FreeOpcUa to Gateway
Open your Python environment and use the following code to connect to the gateway:
```python
from opcua import Client

client = Client("opc.tcp://<gateway-ip>:4840")
client.connect()
print("Connected to OPC UA Server")
```

### Step 7: Retrieve Sensor Data
Use this code snippet to read data from your sensors:
```python
sensor_node = client.get_node("ns=2;i=2")
sensor_value = sensor_node.get_value()
print(f"Sensor Value: {sensor_value}")
```

### Step 8: Visualize Historical Data
Install Matplotlib if you haven't:
```bash
pip install matplotlib
```
```python
import matplotlib.pyplot as plt
import datetime

# Retrieve historical data
history = sensor_node.read_raw_history(datetime.datetime.now() - datetime.timedelta(days=1), datetime.datetime.now())

# Extract timestamps and values
timestamps = [entry.SourceTimestamp for entry in history]
values = [entry.Value.Value for entry in history]

# Plot data
plt.plot(timestamps, values)
plt.xlabel('Time')
plt.ylabel('Sensor Value')
plt.title('Sensor Data Over Time')
plt.show()
```

### Step 9: Try It Out Online
To make it even easier, we've created an interactive Jupyter Notebook that you can run directly in your browser. Click [here](link-to-notebook) to try it out.

## Conclusion
Congratulations! You've successfully set up your [Your Product Name] gateway, connected it to sensors, and visualized the data using FreeOpcUa. We hope this tutorial was helpful and gave you a clear understanding of how to leverage our product for your data management needs.

For more advanced features and support, visit our [documentation](#) or contact our [support team](#). Happy data monitoring!
