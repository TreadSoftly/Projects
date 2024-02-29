
<p align="center">
  
# **Antennas** - Better to ride the digital waves dude
</p>

<p align="center">

**First some inspiration on antennas and how powerful they can be**

</p>

<p align="center">

*The Thing*

</p>

<p align="center">

[![The Thing - Coolest and Creepiest Antenna Story](https://img.youtube.com/vi/QH9Ec_Q5gP0/0.jpg)](https://www.youtube.com/watch?v=QH9Ec_Q5gP0)

</p>

<p align="center">

*Click on the image above to watch a video on "The Thing" 
- Still one of the coolest and creepiest antenna documentaries I've ever learned about spying and specifically antenna capabilities.*

</p>

<p align="center">

#

</p>

This will be an open-source research journey into all things antennas. After busting my new shiny antenna and managing to fix it, I was left pondering. The simple 'plug and test' method showed it worked, but why? How can I evaluate its performance metrics like effectiveness, range, and efficiency? Is there any way to manipulate these?

- (The 'cantenna' scene from mr.ROBOT has a good example although alittle more technical know-how goes into the proper construction of one)

## Undressing the casing of the antenna

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/009f094a-1809-4b89-84ea-cd90a08da514" width="50%" height="50%">
</p>

## Tools used to get the casing off

- I broke out the hair dryer to loosen the heat-fitted end cap (and then watched my hair wave and pretended I was in a convertable with the top down) It's a neat trick; the hair dryer doesn't get hot enough to cause damage, but it does soften the plastic just enough.

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/90f49791-a55b-414b-9231-406d20388771" width="50%" height="50%">
</p>

## Exposed (Post Fixed) - Wire came free/loosened from the traces

A quick cold solder fixed it right up. But the question remains: Why did it work again? How can we measure its functionality beyond the simple 'plug and play'?

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/851f1784-e2df-48b5-9f4f-fa8e7f7e1687" width="50%" height="50%">
</p>

<p align="center">
  
## Size Matters in dBi and shielding 

</p>

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/21cac5a6-76dc-456f-90d5-0922ca08c938" width="50%" height="50%">
</p>

<p align="center">
  
  # Top tiny -  3-5dBi (802.1a/b/g/n ac ax) Omnidirectional Small Wifi/Bluetooth Mini RP-SAMA Antenna Dual Band.
  
  -  Frequency Bands: This antenna supports dual-band frequencies, typically operating in the 2.4 GHz and 5 GHz bands, catering to standards like 802.11a/b/g/n/ac/ax. The dual-band nature ensures compatibility with a wide range of devices and networks, from older Wi-Fi standards to the latest Wi-Fi 6 (802.11ax).
  
  -  Gain: With a gain range of 3-5dBi, it's designed for short to medium range communication, providing a balance between signal range and spatial coverage. This gain level is optimal for devices requiring modest signal enhancement without the need for extensive range, such as handheld devices, IoT sensors, or small access points.
  
  # Middle -  10dBi (802.11ax RP-SMA) MIMO Wi-Fi 6E Omnidirectional High Gain Dual Band

  -  Frequency Bands and Standard: This antenna is engineered for Wi-Fi 6E (802.11ax), which includes the newly opened 6 GHz band, alongside the traditional 2.4 GHz and 5 GHz bands. This tri-band capability allows for less congested airwaves and significantly faster data rates.
  
  -  Gain: A 10dBi gain indicates a more focused signal in certain directions, enhancing signal strength and range significantly compared to lower-gain antennas. This is especially beneficial for penetrating through obstacles and covering larger areas.
  
  -  MIMO Technology: The inclusion of Multiple Input Multiple Output (MIMO) technology implies that the antenna can handle multiple data streams simultaneously, boosting throughput and efficiency. This is critical for high-density environments and for supporting multiple users or devices.

  # Bottom -  5-8dBi (802.11a/b/g/n ac) Dual Band

  -  Frequency Bands: Supports both 2.4 GHz and 5 GHz bands, compatible with a broad array of Wi-Fi standards excluding the latest Wi-Fi 6E. This makes it suitable for general-purpose applications across a variety of devices.
  
  -  Gain: The gain range of 5-8dBi offers a good compromise between range and coverage area, making it suitable for both indoor and outdoor applications where moderate range enhancement is needed without overly sacrificing signal dispersion.

</p>

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/6b123335-9334-4b91-8a68-0dd8097cbc93" width="50%" height="50%">
</p>

<p align="center">
  
 ## Image of my 9 dBi antenna that is so long it can actually be used to spank the bottom of a naughty nephew that liked to bend it :\ 

</p>

<p align="center">
    
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/cd259862-cb65-48f6-a6b5-101571dd8ef3" width="50%" height="50%">
  
</p>

<p align="center">
  
## What the letters mean and how they matter

- **802.11a**
  - Launched: 1999
  - Frequency: 5 GHz
  - Max Speed: Up to 54 Mbps
  - Characteristics: First to use the higher-frequency 5 GHz band, less prone to interference but with shorter range compared to 2.4 GHz technologies.

- **802.11b**
  - Launched: 1999
  - Frequency: 2.4 GHz
  - Max Speed: Up to 11 Mbps
  - Characteristics: Offers better range than 802.11a due to the lower frequency but is more susceptible to interference from other devices like microwaves and cordless phones.

- **802.11g**
  - Launched: 2003
  - Frequency: 2.4 GHz
  - Max Speed: Up to 54 Mbps
  - Characteristics: Combines the best of both 802.11a and 802.11b, offering higher speeds at the more commonly used 2.4 GHz frequency.

- **802.11n (Wi-Fi 4)**
  - Launched: 2009
  - Frequency: 2.4 GHz & 5 GHz
  - Max Speed: Up to 600 Mbps
  - Characteristics: Introduces Multiple Input Multiple Output (MIMO) technology, significantly increasing speed and range. It operates on both frequencies, offering greater flexibility and performance.
 
  - 802.11ac (Wi-Fi 5)

  - Launched: 2014
  - Frequency: 5 GHz
  - Max Speed: Up to 3.46 Gbps
  - Characteristics: Provides wider channel bandwidths and more MIMO spatial streams, with higher QAM, greatly increasing throughput. Operates exclusively in the 5 GHz band, reducing interference.

  - 802.11ax (Wi-Fi 6)

  - Launched: 2019
  - Frequency: 2.4 GHz & 5 GHz
  - Max Speed: Up to 9.6 Gbps
  - Characteristics: Introduces OFDMA (Orthogonal Frequency Division Multiple Access), improving efficiency and capacity, especially in crowded environments. Supports both frequencies, enhancing performance and range.
    
</p>

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/c8bff814-7a0d-4b0e-8888-1735582344a4" width="50%" height="50%">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/7fa571a8-52e0-4a9d-98eb-4f274aa5fc74" width="50%" height="50%">
</p>

<p align="center">

## **Antenna Radiation Patter Reading Chart (E-Plane & H-Plane)**

- *E-Plane* (Electrical Plane): This plane contains the electric field vector and the direction of maximum radiation. It often coincides with the plane in which the main lobe of the antenna radiation pattern lies.

- *H-Plane* (Magnetic Plane): This plane contains the magnetic field vector and is orthogonal to the E-plane. It's defined by the direction of the current flow and the direction of maximum radiation.

</p>

<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/ddc53bd7-21ef-4341-81c6-ccc71704933f" width="50%" height="50%">
</p>

<p align="center">

## 2.4 GHz vs. 5 GHz

</p>

- 2.4 GHz Radiation Patterns: This frequency is common for Wi-Fi and other wireless communication systems. The radiation patterns shown indicate how the antenna radiates energy at this frequency. It's often used due to its range capabilities and wall penetration.

- 5 GHz Radiation Patterns: This higher frequency typically offers faster data rates and less interference compared to 2.4 GHz but at the cost of shorter range and less ability to penetrate solid objects.


# Types Of Antennas (This does seem like its backwards being all the way down here but we will get to making sense out of dollars soon)

- # *Yagi-Uda Antenna:*
  
  A directional antenna consisting of multiple parallel elements in a line, usually half-wave dipoles made of metal rods. Yagi antennas are widely used for radio and television reception and can be modified for increased gain, making them suitable for long-range detection of drones by focusing the RF energy in a specific direction.

- # *Loop Antenna:*
  
  A coil of wire or loop of metal that forms a closed circuit. These antennas can be modified to improve magnetic field sensitivity, making them effective for detecting the RF signatures of drones in environments where electric field detection is challenging.

- # *Helical Antenna:*
  
  Consists of a conducting wire wound in the form of a helix and is used primarily for satellite communication. Modifications can focus on circular polarization, making them suitable for communicating with drones that may be using circularly polarized RF signals for control or data transmission.

- # *Patch Antenna (Microstrip Antenna):*
  
  A type of radio antenna with a low profile, which can be mounted on a flat surface. They can be modified to enhance bandwidth or polarization characteristics, useful for drone detection systems that need to monitor a wide range of frequencies or differentiate between drone signals and other RF noise.

- # *Fractal Antenna:*
  
  Uses a fractal, self-similar design to maximize the length, or increase the perimeter of material that can receive or transmit electromagnetic radiation within a given total surface area or volume. Such modifications can make antennas more compact and broadband, useful for portable drone detection devices that need to be both efficient and discreet.


# Building Your Own Antenna / Modifying An Antenna For A Different Range Or Effectiveness

- # *Cantenna*

  - *Description:*

    Essentially a DIY directional antenna made by using an empty can as a waveguide, the cantenna is celebrated for its simplicity and effectiveness in extending Wi-Fi signals.

  - *Modification:*

    The can's dimensions are critical; they are calculated to resonate at specific frequencies, predominantly Wi-Fi bands around 2.4 GHz or 5 GHz.

  - *Advantages:*

    This modification significantly improves the antenna's directional gain, focusing the signal power in a specific direction, which enhances the range and signal quality.

  - *Application:*

    Ideal for long-range Wi-Fi reception, point-to-point links between networks, and as a cost-effective tool for RF exploration, including drone communication channels.
  

- # *Umbrellatenna* or the dumber name *Parabolic Dish Antenna*

  - *Description:*

    Features a parabolic reflector with a feed antenna at its focal point, focusing radio waves into a narrow beam.

  - *Modification:*

    Altering the size of the dish and the curvature of the parabolic reflector to increase focus and gain.

  - *Advantages:*

    Such modifications enable high precision in signal direction, allowing for targeted communication and interference management, crucial for jamming specific drones without affecting other devices.

  - *Application:*

    Used in tracking and communicating with distant drones and in high-gain jamming applications.
