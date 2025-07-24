
# <p align="center">🎯 Targeting Function Toolkit</p>
<div align="center">

![Target Logo](assets/target-logo.png)

_The Targeting Function Toolkit offers precision and intelligence in identifying input types. Whether you're a security expert or a developer, this function opens up new horizons in validating and categorizing diverse data like IPs, domains, ports, MAC addresses, URLs, and ASNs._

## 📌 Table of Contents
1. [Introduction](#-introduction)
2. [Features](#-features)
3. [Installation](#-installation)
4. [Usage](#-usage)
5. [Examples](#-examples)
6. [API Reference](#-api-reference)


</div>

## <p align="center">🎉 Introduction</p>

<div align="center">

Meet your new best friend in data validation—the Targeting Function Toolkit. Created with precision and finesse, this function is more than just a validator; it's a compass, guiding you to recognize different input types accurately.

</div>

## <p align="center">🛠️ Features</p>

<div align="center">

- **Robust Recognition Algorithms:** Sophisticated regex patterns for accurate identification.
- **Multi-Dimensional Targeting:** IP, domain, port, MAC, URL, ASN.
- **Interactive User Interface:** Real-time input and validation.
- **Customizable Integration:** Seamless integration with your existing projects.
- **Error Handling:** Informative error messages for invalid inputs.

</div>

## <p align="center">💻 Installation</p>

<div align="center">

1. **Clone the Repository:**
   ```
   git clone https://github.com/yourusername/targeting-function.git
   ```

2. **Navigate to the Directory:**
   ```
   cd targeting-function
   ```

3. **Install Requirements:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the Script:**
   ```
   python target.py
   ```

</div>

## <p align="center">📘 Usage</p>

<div align="center">

### Using the Command Line

Run the script directly from the command line and follow the prompt:

```
python target.py
```

### Integrating with Python Script

Import the `target_input_type` function into your Python script:

```
from target import target_input_type

target = target_input_type("192.168.1.1")
print(f"Target type: {target}")
```

</div>

## <p align="center">🧪 Examples</p>

<div align="center">

### Validating an IP Address

```
target = target_input_type("192.168.1.1")
print(f"Target type: {target}") # Output: ip
```

### Checking a Domain

```
target = target_input_type("example.com")
print(f"Target type: {target}") # Output: domain
```

... [More Examples](EXAMPLES.md)

</div>

## <p align="center">📚 API Reference</p>

<div align="center">

### `target_input_type(input_str: str) -> str:`

- `input_str` (string): The input string containing the target.
- Returns a string representing the target type (`ip`, `domain`, `port`, `mac`, `url`, `asn`, `unknown`).

</div>


## <p align="center">📚 Appendix</p>

<div align="center">

# PLACE HOLDER TO TEST OUT BUILDING ADDED LIBRARIES AND APPENDIX ETC..
Check out the [Appendix](APPENDIX.md) for more details on regular expressions used, additional examples, and advanced configurations.

</div>

---

