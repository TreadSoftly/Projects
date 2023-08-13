
# Counter-Drone Intelligence Research Report: HESA Shahed 136

<div align="center">

## Executive Summary

This report presents a comprehensive analysis of the HESA Shahed 136, an Iranian kamikaze drone. It includes detailed specifications, potential vulnerabilities, and top-level advice on countermeasures.

---

### Table of Contents

1. [Introduction](#introduction)
2. [American Components](#american-components)
3. [GPS Guidance System](#gps-guidance-system)
4. [Signal Analysis and Countermeasures](#signal-analysis-and-countermeasures)
5. [Microcontroller Specifications](#microcontroller-specifications)
6. [Conclusion](#conclusion)

---

### 1. Introduction

The HESA Shahed 136 is a sophisticated military drone. This section introduces the drone's capabilities and the methods employed in the investigation.

---

### 2. American Components

#### **American Chips by Texas Instruments**

- **Availability:** Freely available on the market.
- **Serial Numbers:** Allow for investigation of the entire supply chain.

#### **Advice on Countermeasures**

1. **Supply Chain Monitoring:** Track and control the distribution of key components.
2. **Regulatory Compliance:** Ensure adherence to international export laws.
3. **Technology Analysis:** Conduct reverse engineering to identify vulnerabilities.

---

### 3. GPS Guidance System

#### **GPS Signal Prevention System**

- **Functionality:** Prevents GPS signals from being replaced by electronic devices.
- **Vulnerabilities:** Does not prevent interference, leading to navigational errors.

#### **Advice on Countermeasures**

1. **GPS Signal Interference:** Develop tools to exploit the interference vulnerability.
2. **Inertial System Analysis:** Study the inertial system to find weaknesses.
3. **Environmental Manipulation:** Utilize wind patterns to disrupt drone navigation.

---

### 4. Signal Analysis and Countermeasures

#### **Signal Analysis Tools**

- **HackRF One:** Popular SDR platform for frequency analysis.
- **Software Tools:** SDR#, GQRX for visualization and analysis.
- **Universal Software Radio Peripheral (USRP):** Analyzes and decodes communication protocols.

#### **Advice on Countermeasures**

1. **Frequency Jamming:** Utilize SDR tools to disrupt communication.
2. **Protocol Analysis:** Identify and target specific communication protocols.
3. **Real-time Monitoring:** Implement systems to detect and respond to drone signals.

---

### 5. Microcontroller Specifications

#### **TMS320F2833x, TMS320F2823x Real-Time Microcontrollers**
‘Ts320F28234,  ‘TMS320F 26332, TMS320F28235, TMS320F28235.01  

1, TMS320F 26232, TMS320F28232-01  
'SPis4390 = JUNE 2007 ~ REVISED AUGUST 3022    
TMS320F2833x, TMS320F2823x Real-Time Microcontrollers  

1 Features  
  
‘+ High-performance static CMOS technology  
— Up to 150 Mz (6 67-ns cycle time)  
= 1.9-V/1.8-V core, 3:3-V UO design  
‘+ High-performance 32-bit CPU (TMS320C28x)  
~ IEEE 754 single-precision Floating-Point Unit  
(FPU) (F2833x only)  
= 16 « 16 and 32 x 32 MAC operations  
16 * 16 dual MAC  
Harvard bus architecture  
— Fast interrupt response and processing  
— Unified memory programming mode!  
= Code-efficient (in C/C++ and Assembly)  
+ Six-channel DMA controller (for ADC, McBSP,  
‘ePWM, XINTF, and SARAM)  
+ 16:it or 32-bit External Interface (XINTF)  
= More than 2M x 16 address reach  
+ On-chip memory  
— F28335, F28333, F28235:  
256K * 16 flash, 34K x 16 SARAM  
— F28334, £28234  
128K * 16 flash, 34K « 16 SARAM  
— F28332, F28232:  
GaK x 16 flash, 26K * 16 SARAM  
~ 1Kx 16 OTP ROM  
+ Boot ROM (8K x 16)  
— With software boot modes (through SCI, SPI,  
CAN, I2C, McBSP, XINTF, and parallel /O)  
= Standard math tables  
+ Clock and system control  
— On-chip oscillator  
= Watchdog timer module  
‘+ GPIOO to GPIO6S pins can be connected to one of  
the eight external core interrupts  
‘+ Peripheral interrupt Expansion (PIE) block that  
‘supports all 58 peripheral interrupts  
+ 128-bit security key/lock  
— Protects flast/OTP/RAM blocks  
= Prevents firmware reverse-engineering  
‘+ Enhanced control peripherals  
— Upto 18 PWM outputs  
~ Upto HRPWM outputs with 150-ps MEP  
resolution  
— Up to6 event capture inputs  
= Up to2 Quadrature Encoder interfaces  
= Upto 32-bit timers  
(6 for eCAPS and 2 for eQEPs)  
~ Upto 16-bit timers  
(6 for ePWMs and 3 XINTCTRs)  
+ Three 32-bit CPU timers,  
Serial port peripherals  
= Upto2 CAN modules  
Upto 3 SCI (UART) modules  
Up to 2 McBSP modules (configurable as SPI)  
(One SPI module  
= One inter-integrated Circuit (12C) bus  
12-bit ADC, 16 channels  
= 80-ns conversion rate  
~ 28 channel input multiplexer  
= Two sample-and-hold  
— Singlesimuitaneous conversions  
= intemal or extemal reterence  

Up to 88 individually programmable, multiplexed  

GPIO pins with input fitering  

STAG boundary scan support  
— IEEE Standard 1149,1-1990 Standard Test  
‘Access Port and Boundary Scan Architecture  
‘Advanced debug features  
— Analysis and breakpoint functions  
= Real-time debug using hardware  

Development support includes  
~ ANSI C/C++ compiler/assemblerfnker  
~ Code Composer Stusio™ IDE  

DSPIBIOS™ and SYS/BIOS  
— Digital motor control and digital power sofware  
libraries  

Low-power modes and power savings  
— IDLE, STANDBY, HALT modes supported  
= Disable individual peripheral clocks  
Endianness:Litle endian  

Package options  
~ Leadfree, green packaging  
~  176-ball plastic Ball Grid Array (BGA) [2JZ]  
= 179-ball MicroStar BGA” [ZHH]  
—  178:ball New Fine Pitch Ball Gra Array  
(FBGA) [ZAY]  
—  176-pin Low-Profle Quad Flatpack (LOFP)  
(PGF  
= 176pin Thermally Enhanced Low-Profle Quad  
Flatpack (HLOFP) [PTP]  

Temperature options.  
— A--40°C to 85°C (PGF, ZHH, ZAY, ZZ)  
— S:-40°C to 125°C (PTP, ZJZ)  
— Q:-40°C to 125°C (PTP, ZZ)  
(AEC Q100 qualification for automotive  
applications)  
  
"An IMPORTANT NOTICE atte end ofthis data sheet addresses avalably waraniy, changes, use sally ciical applatons,  
intelectual propery matters and oer Important daciamers, PRODUCTION DATA.  


#### **Advice on Countermeasures**

1. **Microcontroller Analysis:** Understand the microcontroller's architecture to identify potential weak points.
2. **Software Exploitation:** Develop exploits targeting specific firmware functionalities.
3. **Hardware Manipulation:** Design tools to physically tamper with the microcontroller.

---

### 6. Conclusion

The investigation into the HESA Shahed 136 has provided actionable insights into its construction, capabilities, and weaknesses. By employing the advised countermeasures, we can develop effective strategies against this drone technology.

---

</div>
