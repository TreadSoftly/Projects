<p align="center">
  <img src="https://path/to/your/logo.png" alt="nc_iSpy Logo" width="200">
</p>

<h1 align="center">🕵️ nc_iSpy: Netcat-Based Port Scanner</h1>

<p align="center">
  A sophisticated and efficient port scanner crafted with Netcat.
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#examples">Examples</a> •
  <a href="#contact">Contact</a>
</p>

## 🌟 Overview
`nc_iSpy` is a state-of-the-art port scanner built with Netcat, one of the most powerful and versatile networking utilities. This script provides a streamlined way to scan target hosts for open ports and organize the results neatly.

## 💎 Features
- **Precision Scanning**: Target specific port ranges or scan all 65535 ports.
- **Rich Output**: Organized and clean results, easily accessible for further analysis.
- **Lightweight**: Utilizes Netcat, offering speed without additional dependencies.
- **User Friendly**: Easy-to-use options and comprehensive help guide.

## 🛠 Installation
To run this script, ensure you have Netcat installed on your system. Clone the repository and make the script executable:

```
git clone https://github.com/yourusername/nc_iSpy.git
cd nc_iSpy
chmod +x nc_iSpy.sh
```

## 🎮 Usage
```
./nc_iSpy.sh [options] TARGET
```

### 🧩 Options
- **-h, --help**: Display the help message
- **-p, --port**: Specify the port range for the scan (default: 0-65535)
- **-o, --output**: Specify the output directory

## 📖 Examples
### Standard Scan
```
./nc_iSpy.sh example.com
```

### Custom Port Range
```
./nc_iSpy.sh -p 80-443 example.com
```

### Custom Output Directory
```
./nc_iSpy.sh -o ~/my_scans example.com
```
