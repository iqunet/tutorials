---
layout: post
title: "LoRaWAN to OPC-UA Gateway"
date: 2024-05-19 22:10:15 +0200
categories: tutorial
---

# Tutorial: from LoRaWAN to Python via OPC-UA

<span style="background-color: yellow">
**Note:** This tutorial makes use of the iQunet Industrial Edge Server.
<br>A demo gateway is provided for the purpose of this guide.
</span>

You will learn how to:
- Connect a **LoRaWAN sensor** to the iQunet Industrial Edge Server.
- Understand how sensor data is stored into the **local OPC-UA database**.
- Test the OPC-UA server connection using **UaExpert**.
- Use **Python** to connect to the OPC UA server for data visualization and post-processing.

![LoRaWAN to OPC UA](/assets/images/lora-opc-python.svg)


## Prerequisites

Before we begin, ensure you have the following:
- [Your Product Name] gateway
- LoRaWAN or Modbus sensors
- A computer with internet access
- Basic knowledge of OPC UA (recommended)
- FreeOpcUa installed (if not, follow this [installation guide](#))

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
