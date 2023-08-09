<h1 align="center">

  [:mag: nmap_iSpy - Network Scanning Made Simple :computer:](https://github.com/TreadSoftly/Projects/blob/main/NmapScanner.sh)
</h1>

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/427f0bbb-a874-4939-8270-fd7f08fba52c" alt="camera" width="50" height="50">
</p>

`nmap_iSpy` is a cutting-edge Bash script that integrates with [`nmap`](https://github.com/nmap/nmap) to conduct customized and automated network scans. Designed for security experts, system administrators, and developers, this tool offers a rich set of features tailored to meet diverse scanning needs.
<br>
<br>


<h2 align="center">
  Table of Contents
</h2>

<p align="center">
  <a href="#introduction">1. Introduction</a><br>
  <a href="#features">2. Features</a><br>
  <a href="#requirements">3. Requirements</a><br>
  <a href="#installation">4. Installation</a><br>
  <a href="#usage">5. Usage</a><br>
  <a href="#nmap-flags--options">6. Nmap Flags & Options</a><br>
  <a href="#example-code">7. Example Code</a><br>
  <a href="#links--resources">8. Links & Resources</a><br>
  <a href="#license">9. License</a><br>
</p>
<br>

## Introduction

`nmap_iSpy` streamlines the process of scanning networks by allowing users to easily set up comprehensive scans using [`nmap`](https://github.com/nmap/nmap). It automates various scanning functions and provides extensive customization options.

## Features

- **Wide Scan Range**: Conduct TCP, UDP, or combined scans across the entire port range.
- **Versatility**: Define scan type, port range, verbosity, duration, and detail level.
- **Automated Reporting**: Comprehensive reports in XML, TXT, and GNMAP formats.
- **Compression Integration**: Utilize `bzip2` and `xz` for efficient storage.

## Requirements

- [`nmap`](https://github.com/nmap/nmap)
- `bzip2` (Optional for compression)
- `xz` (Optional for compression)

## Installation

To get started with `nmap_iSpy`, simply clone the repository:

```bash
git clone https://github.com/YourUsername/nmap_iSpy.git
cd nmap_iSpy
chmod +x nmap_iSpy.sh
```

## Usage

Basic usage:

```bash
./nmap_iSpy.sh <target>
```

Advanced usage with optional parameters:

```bash
./nmap_iSpy.sh <target> <scan_type> <port> <verbosity> <scan_duration> <scan_detail>
```

## Nmap Flags & Options

`nmap` offers a wide variety of flags and options. Below are some examples:

- **Basic Scan**: `nmap <target>`
- **TCP SYN Scan**: `nmap -sS <target>`
- **UDP Scan**: `nmap -sU <target>`
- **Version Detection**: `nmap -sV <target>`
- **Operating System Detection**: `nmap -O <target>`
- **Output in XML Format**: `nmap -oX <output.xml> <target>`
- **Verbose Mode**: `nmap -v <target>`

Refer to the [Nmap Reference Guide](https://nmap.org/book/man.html) for a complete list of options.

## Example Code

<details>
<summary>Click here to view the full script</summary>

```bash
#!/bin/bash
# Your entire script code...
```

</details>

## Links & Resources

- [GitHub Repository](https://github.com/YourUsername/nmap_iSpy)
- [Nmap Official Site](https://nmap.org)
- [Nmap on GitHub](https://github.com/nmap/nmap)
- [Nmap Tutorial to find Network Vulnerabilities - NetworkChuck](https://youtu.be/4t4kBkMsDbQ)
- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [bzip2 Official Site](http://www.bzip.org)
- [xz Official Site](https://tukaani.org/xz/)

## License

This project is licensed under the MIT License. View the [LICENSE.md](LICENSE.md) file for details.
