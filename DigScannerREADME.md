<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/dc32b4c0-b78d-4756-bfec-863283d9d641" alt="bug">
</p>

<h1 align="center">🚀 <strong>dig_iSpy</strong>: DNS Enumeration Bash Script</h1>

<p align="center">
  <em>THIS IS JUST A TEMPLATE I USE TO DROP IN AND TEST THINGS WITH dig</em>
</p>

<p align="center">
  <strong>🚨 BUGGY AS HELL AS A STANDALONE SCRIPT 🚨</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## 📋 Overview
`dig_iSpy` is a powerful shell script designed for DNS enumeration, leveraging `dig` and other compression tools. It provides extensive flexibility with customizable timeouts and retry attempts. Get insights into your target's DNS setup with ease and save the results in multiple compressed formats!

## 🔧 Installation
Clone the repository and ensure that you have the required tools (`dig`, `gzip`, `bzip2`, `xz`) installed on your system.

\```bash
git clone https://github.com/yourusername/dig_iSpy.git
cd dig_iSpy
chmod +x dig_iSpy.sh
\```

## 🎮 Usage
### Basic Command
\```bash
./dig_iSpy.sh [target] [timeout] [max_retries]
\```
- **target**: The target domain or IP address.
- **timeout**: The time (in seconds) to wait for a response from dig (default: 10).
- **max_retries**: The maximum number of retries for dig (default: 3).

### Options
- **-h**, **--help**, **-?**, **--?**: Show the help message and exit.

### Example
\```bash
./dig_iSpy.sh example.com 5 2
\```

## 🚀 Features
- 🎯 Targeted DNS Enumeration
- ⏰ Customizable Timeout and Retry Settings
- 📂 Output in Various Compressed Formats
- 📝 Clean and Efficient Logging

## 🤝 Contributing
If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcomed.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 📞 Contact
For any inquiries or support, please contact the maintainer at [your-email@example.com](mailto:your-email@example.com).
</p>
