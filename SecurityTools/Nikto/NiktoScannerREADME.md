<p align="center">
  <img src="https://path/to/your/logo.png" alt="Put this logo in later" width="200">
</p>

<h1 align="center">
  <a href="https://github.com/sullo/nikto">
    🔍 Advanced Web Security Scanner
  </a>
</h1>

<p align="center">
  Empowering security assessments with Nikto integration, providing comprehensive web vulnerability insights.
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#examples">Examples</a> 
</p>

## 🌐 Overview
`LEVERAGE` is a web security scanner that harnesses the power of Nikto, designed to perform meticulous scans on target web servers. Created for professionals who value precision and efficiency, this tool offers streamlined vulnerability scanning with a focus on accuracy and depth.

## 💼 Features
- **Targeted Scanning**: Specify custom port numbers.
- **Rich Output**: Detailed logs and scan results.
- **Integration with Nikto**: Utilizes Nikto's extensive vulnerability database.
- **User-Centric Design**: Intuitive and easy-to-use options.

## 📦 Installation
Ensure you have Nikto installed on your system. Clone the repository and make the script executable:

```
git clone https://github.com/yourusername/LEVERAGE.git
cd LEVERAGE
chmod +x nc_iSpy.sh
```

## 🎲 Usage
```
sudo nc_ispy -h
sudo nc_ispy.sh <target> <port>
nc_ispy <target> <port> 
nc_ispy -v -z "$target" "$port" example.com
```

### Options
- **-p, --port <port>**: Specify the port (default: 80)
- **-h, --help, -?, --man**: Display the help message

## 🎓 Examples
### Scan Default Port
```
nc_ispy -v -z "$target" "$port" example.com
```

### Scan Custom Port
```
nc_ispy -v -z "$target" -p 8080 example.com
```
