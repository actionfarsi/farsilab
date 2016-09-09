/**********************************************************************
 *                                                                    *
 *                           FlexIOLibTypes.h                         *
 *                                                                    *
 **********************************************************************/
/*
 * Project:   TTM8-Virtex5 (Time Tagging Module)
 *
 * Company:   Roithner Lasertechnik GmbH - Vienna - Austria
 * Support:   office@roithner-laser.com
 *
 * Copyright: Roithner Lasertechnik GmbH
 *            Wiedner Hauptstrasse 76
 *            1040 Vienna
 *            Austria / Europe
 *
 * Decription: */
/** @file
 * TTMLibTypes.h defines the Types used in the Interface of the TTMLib
 * (Time Tagging Module Library).\n
 * C-Functions that use these types are defined in TTMLib.h. C++ Classes
 * wrapping these C-Functions are defined in TTMLib.hpp.\n
 *
 * Note that it defines only those types, that are specific to TTMLib.
 * General Types used to achieve system independence are defined in
 * SysTypes.h.\n
 * Note: Your application will probably include TTMLib.h (for C apps)
 * or TTMLib.hpp (for C++ apps). These already include TTMLibTypes, so
 * you don't need to explicitly include it again.
 *//*
 * Tab: 2 spaces
 *
 * Release 4.4.2 - 2015-04-14
 */

#ifndef FlexIOLibTypes_h
#define FlexIOLibTypes_h

/**********************************************************************
 *                                                                    *
 **********************************************************************/

#include "SysTypes.h"

/**********************************************************************/

#if defined __cplusplus
extern "C" {
#endif

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief Current Version of the TTM Library
  *
  * TTMVERSION gives the current Version of the TTM Library in the format
  * 0xMMNNPPSS (MM = major, NN = minor, PP = patch, SS = sub(0=none, 1='a', ...).
  * For example TTMLib 1.4.12b will return 0x01040C02.
  */
#define FLEXIOVERSION 0x00000201  // 0.0.2a

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
/** @brief Custom Configuration Data for FlexIO Applications
 *
 *  Every Application can store some application specific data in the
 *  Flash. This is just a simple placeholder for the FlexIO basic app.
 */
struct FlexIOCustomConfig
 {
  uint32_t  Reserved[64];       //!< Room for Application Specific Settings
 };

/** @brief Custom Configuration Data for TTM8 Applications
 *
 *  Every Application can store some application specific data in the
 *  Flash. TTMCustomConfig holds the application specific configuration
 *  data for the TTM8 Application.
 */
struct TTMCustomConfig
 {
  // uint32_t  TTMCntrlDebugLevel;
  // uint32_t  TTMDataDebugLevel;

  int16_t   InternClkCoarseTrim;   //!< Coarse Trim Setting for the Internal Crystal [Ticks +/- 32000]
  int16_t   ExternClkInRefVoltage; //!< Reference Voltage for the External Clock [mV]
  uint32_t  InternClkInFreq;       //!< Freq. of the Internal Crystal [Hz]
  uint32_t  ExternClkInFreq;       //!< Freq. of the external Clock Input [Hz]
  uint32_t  ExternClkOutFreq;      //!< Freq. of the external Clock Output [Hz]
  bool_t    UseExternClkIn;        //!< Do we want to obtain the reference clock from
                                   //   the external Clock Input (TRUE) or the internal Crystal (FALSE)?
  bool_t    UseExternClkOut;       //!< Do we want to drive the external Clock Output?

  bool_t    HasHighPrecisionCrystal; //!< Is the TTM8-Board fitted with a Oven Control Crystal Osc. (OCXO)?
  int16_t   InternClkFineTrim;     //!< Fine Trim Setting for the Internal Crystal [Ticks +/- 32000]

  int16_t   IModeChnOffset[8];     //!< Channel dependent Offset for I-Mode (unused)
  int16_t   GModeChnOffset[2];     //!< Channel dependent Offset for G-Mode (unused)
  int16_t   RModeChnOffset[2];     //!< Channel dependent Offset for R-Mode (unused)
  int16_t   MModeChnOffset[32][2]; //!< Channel dependent Offset for M-Mode (unused)

  uint32_t  Reserved[20];          //!< Room for more Application Specific Settings
 };

/** @brief Configuration Information of a FlexIO Board
  */
typedef struct FlexIOBoardConfig_t
 {
  uint32_t  ConfigMagic;    //!< Always ConfigCookie for Record Identification
  uint32_t  ConfigSize;     //!< Size of FlexIOBoardConfig_t
  uint32_t  ApplMagic;      //!< Device Type Cookie
  char      ApplType[32];   //!< Device Type Text
                              // FlexIO Boards w/o Extras use "AIT FlexIO" (padded with 0x00)
                              // TTM8000 Boards always use "AIT TimeTagging - TTM8000" (padded with 0x00)
  uint32_t  SerialNr;       //!< FlexIO Board Serial Number
  uint64_t  MACAddr;        //!< FlexIO Board MAC Address (Bits 47..0)
  char      BoardName[32];  //!< User Defined FlexIO Board Name - e.g. "Ports 1-8", or "Speed & Temp"
  in_addr_t IPAddr;         //!< FlexIO Board IP-Address
  in_addr_t NetMask;        //!< FlexIO Board Ethernet Subnet-Mask
  in_addr_t BroadcastAddr;  //!< FlexIO Board Ethernet Subnet Broadcast Address
  in_addr_t NetGateway;     //!< FlexIO Board Ethernet Gateway
  in_port_t CntrlPort;      //!< UDP Port used for the Control Connection by the FlexIO Board
  in_port_t DataPort;       //!< UDP Port used for the Data Connection by the FlexIO Board

  uint8_t   ButtonAction[2]; //!< Do the Buttons have a local function (0..None, 1..Reset, 2+ Reserved)
  uint16_t  ReservedA;       //!< Reserved for Future use...
  uint8_t   LEDAction[3];    //!< Do the User LEDs have a local function (0..None, 1..Liveness)
  uint8_t   ReservedB;       //!< Reserved for Future use...
  uint32_t  ReservedC[2];    //!< Reserved for Future use...

  uint16_t  DisplayType;     //!< Do we have a Display (0..No, 1..LEDs + Buttons, 2..ASCII)
  uint16_t  FanType;         //!< Do we have a Fan (0..No, 1..Non-Controlled, 2..Controlled)

  uint32_t  PowerSupplyDebugLevel;  //!< Debug Level for the FlexIO Power Supply (0..Off, >0 On)
  uint32_t  FlexIOServerDebugLevel; //!< Debug Level of the FlexIO Server Software (0..Off, >0 On)
  uint32_t  NetIPDebugLevel;    //!< Debug Level of the UDP/IP Software (0..Off, >0 On)
  uint32_t  NetARPDebugLevel;   //!< Debug Level of the ARP Software (0..Off, >0 On)
  uint32_t  NetCoreDebugLevel;  //!< Debug Level of the Ethernet Driver (MAC Level) Software (0..Off, >0 On)
  uint32_t  FlashDebugLevel;    //!< Debug Level of the Flash Erase/Programm Code (0..Off, >0 On)

  uint32_t  CustomAppCntrlDebugLevel; //!< Debug Level for the Control Network Connection
  uint32_t  CustomAppDataDebugLevel;  //!< Debug Level for the Data Network Connection

  union
   {
    struct FlexIOCustomConfig FlexIO; //!< FlexIO Specific Configuration Data
    struct TTMCustomConfig    TTM8;   //!< TTM8 Specific Configuration Data
   } CustomConfig;               //!< Application Specific Configuration Data
 } FlexIOBoardConfig_t;

/** @brief Magic Cookie for FlexIOBoardConfig.ConfigMagic
  */
#define ConfigCookie       htonl(0x46785263)  // 'FxRc'
/** @brief Default Value for the ApplCookie field */
#define AnyApplCookie      htonl(0x2A2A2A2A)  // '****'
/** @brief ApplCookie for the FlexIO Application */
#define FlexIOApplCookie   htonl(0x4678494F)  // 'FxIO'
// #define TTM8ApplCookie      htonl(0x46785454) // 'FxTT'
/** @brief ApplCookie for the TTM8 Application */
#define TTM8ApplCookie      htonl(0x54544D38) // 'TTM8'
// #define PolCntrlApplCookie  htonl(0x46785043) // 'FxPC'
// #define PolCntrlApplCookie  htonl(0x506F6C43) // 'PolC'
/** @brief ApplCookie for the LQuNet Application */
#define LQuNetApplCookie    htonl(0x4C51754E) // 'LQuN'

/** @brief Predefined Actions for the TTM8000-Buttons
 *
 * The Buttons of the TTM8000 can be configured to trigger some predifined
 * actions, or can be left to the user application to use for whatever seems
 * appropriate.
 */
typedef enum {
  ButtonAction_User        = 0,   //!< No FlexIO-internal Action - User application defines meaning of Buttons
  ButtonAction_SecureReset = 1,   //!< Soft Reset after warning period with flashing LEDs
  ButtonAction_FastReset   = 2,   //!< Soft Reset without warning
  ButtonAction_ClearError  = 3,   //!< Reset Error LED
  ButtonAction_Invalid     = 0xFF //!< Invalid Setting
 } ButtonAction_t;

/** @brief Predefined Actions for the TTM8000-LEDs
 *
 * The LEDs of the TTM8000 can be configured to display some predifined
 * signals, or can be left to the user application to use for whatever
 * purpose seems appropriate.
 */
typedef enum {
  LEDAction_User      = 0,       //!< No FlexIO-internal Action - User application defines LED State
  LEDAction_Heartbeat = 1,       //!< Slowly flash the LED to show that the FlexIO Board is alive
  LEDAction_Invalid   = 0xFF     //!< Invalid Setting
 } LEDAction_t;


/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief TTM8 Board Server Status
  */
typedef enum FlexIOServerState_t
 {
  FlexIOSrvState_Startup = 0,      //!< Server is Booting
  FlexIOSrvState_Idle    = 1,      //!< Server is Idle - No Measurement in Progress
  FlexIOSrvState_Measurement = 2   //!< Measurement is in Progress
 } FlexIOServerState_t;

/** @brief Address of a IP/UDP Network Endpoint
  */
typedef struct
 {
  in_addr_t IPAddr;   //!< IP-Address
  in_port_t UDPPort;  //!< UDP Port
  uint16_t  Reserved; //!< Padding
 } UDPAddr_t;


#if (!defined(_NETINET_IN_H) && !defined(_WINSOCK2API_) && !defined(_NETINET_IN_H_) && !defined(_GNU_H_WINDOWS32_SOCKETS))
/** @brief IPv4 Socket Address (incl. TCP/UDP Port)
  */
struct sockaddr_in
 {
  int16_t        sin_family;  //!< Address Family (e.g. AF_INET)
  uint16_t       sin_port;    //!< UDP/TCP Port (e.g. htons(10502))
  struct in_addr sin_addr;    //!< IPv4 Address
  char           zero[8];     //!< Unused - Zero this is you want
 };
#endif



/** @brief Configuration/Status Information about a TTM8 Board
  */
typedef struct
 {
  uint32_t  Uptime;             //!< Uptime in Seconds
  uint32_t  Dummy;              //!< Unused (Reserved for Uptime Microseconds)
  FlexIOBoardConfig_t BoardConfig; //!< Board Configuration
  in_port_t SrvCntrlPort;       //!< UDP Port used for the Control Channel by the Server on the FlexIO Board - Usually FlexIOCntrlPort
  uint8_t   SrvState;           //!< FlexIO Board Server Status (FlexIOServerState_t cast to a Byte)
  uint8_t   ConnectionCnt;      //!< Number of Host holding a Control Connection to the Server (Currently: max. 8)
  uint32_t  BoardVersion;       //!< Board Version - Format: 0xMMNNPPSS (MM = major, NN = minor, PP = patch, SS = sub(0=none, 1='a', ...)).
  uint32_t  FirmwareVersion;    //!< FPGA Firmware Version - Format: Subversion/SVN RevisionID
  uint32_t  FirmwareDate;       //!< FPGA Firmware Date - Format: 0xYYYYMMDD (e.g. 0x20110830 for 30-Aug-2011)
  uint32_t  ServerVersion;      //!< Software Version - Format: Subversion/SVN RevisionID
  uint32_t  ServerDate;         //!< Software Date -  - Format: 0xYYYYMMDD (e.g. 0x20110830 for 30-Aug-2011).

  UDPAddr_t CntrlClient[8];     //!< IP-Address/UDP-Port of the Connected Clients
  UDPAddr_t DataTarget;         //!< IP-Address/UDP-Port of the Data Target
 } FlexIOBoardInfo_t;

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief Measurement Modes / Data Formats for TTM8 Timetags
  */
typedef enum TTMDataFormat_t
 {
  TTFormat_Unknown          = 0, //!< Data Format Unknown (Should never be used!)
  TTFormat_IMode_EXT64_FLAT = 1, //!< I-Mode Continuous Flat - 3 Bit Channel - 1 Bit Slope - 60 Bit Timetag
  TTFormat_IMode_EXT64_PACK = 2, //!< I-Mode Continuous Packed - 1 Bit High(1)/Low(0) - High: 31 Bit Timetag - Low: 3 Bit Channel - 1 Bit Slope - 27 Bit Timetag
  TTFormat_IMode_Cont_RAW29 = 3, //!< I-Mode Continuous - 3 Bit Void - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
  TTFormat_IMode_Cont_RAW32 = 4, //!< I-Mode Continuous - 3 Bit StartOvrCnt - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
  TTFormat_IMode_StartStop_RAW29 = 5, //!< I-Mode Start/Stop - 3 Bit Void - 3 Bit Channel - 8 Bit StartCnt - 1 Bit Slope - 17 Bit Timetag
  TTFormat_GMode = 6,            //!< G-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit Void - 1 Bit Slope - 22 Bit Timetag
  TTFormat_RMode = 7,            //!< R-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit Void - 23 Bit Timetag
  TTFormat_MMode = 8,            //!< M-Mode - 3 Bit Void - 1 Bit Channel - 5 Bit StartCnt - 23 Bit Timetag
  TTFormat_MultiIMode_EXT64_FLAT = 9, //!< Multiboard I-Mode Continuous Flat - 4 Bit BoardID - 3 Bit Channel - 1 Bit Slope - 56 Bit Timetag
  TTFormat_MultiIMode_EXT64_PACK = 10 //!< Multiboard I-Mode Continuous Packed - 1 Bit High(1)/Low(0) - High: 31 Bit Timetag - Low: 4 Bit BoardID - 3 Bit Channel - 1 Bit Slope - 23 Bit Timetag
 } TTMDataFormat_t;

/** @brief Start/Stop1..Stop8 Input Channels for the TTM8 Module
  */
enum TTMChannel_t
 {
  TTMChnStart = 0, //!< Start Signal
  TTMChnStop1 = 1, //!< Stop1 Signal
  TTMChnStop2 = 2, //!< Stop2 Signal
  TTMChnStop3 = 3, //!< Stop3 Signal
  TTMChnStop4 = 4, //!< Stop4 Signal
  TTMChnStop5 = 5, //!< Stop5 Signal
  TTMChnStop6 = 6, //!< Stop6 Signal
  TTMChnStop7 = 7, //!< Stop7 Signal
  TTMChnStop8 = 8  //!< Stop8 Signal
 };

/** @brief Rising/Falling Slope of Start/Stop1..Stop8 Signals
  */
enum TTMSlope_t
 {
  TTMSlopeRising = 0, //!< Rising Slope
  TTMSlopeFalling= 1  //!< Falling Slope
 };

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief Timetag Measurement Configuration
  */
typedef struct TTMMeasConfig_t
 {
  uint16_t  GPXRefClkDiv;       //!< GPX Reference Clock Divider - Always use 0 for Automatic!
  uint16_t  GPXHSDiv;           //!< GPX High Speed Clock Divider - Always use 0 for Automatic!
  uint16_t  GPXStartTimer;      //!< GPX Restart Timer - Always use 0 for Automatic!
  uint16_t  PaddingA;           //!< Reserved
  uint8_t   DataFormat;         //!< Data Format (TTMDataFormat_t cast to a Byte)
  uint8_t   MModeDiv;           //!< Timing Resolution in M-Mode (not used in other modes)
  uint16_t  MModeTimeout;       //!< Timeout for Measurements in M-Mode (in 25ns Ticks)
  uint32_t  MagicGPXOffset;     //!< Use GPXUnderflowAvoidanceOffset
  bool_t    UseLittleEndianByteOrder; //!< Timetag Data is sent over the network in Little Endian (TRUE) or Big Endian (FALSE) Byte Order
  uint16_t  PaddingB;           //!< Reserved

  /** Enable Signal Edge Detection for Rising/Falling Edges
    * @see TTMChannel_t, TTMSlope_t
    */
  bool_t    EnableEdge[9][2];

  int16_t   SignalLevel[9];     //!< Start/StopX Signal Low/High Threshold Voltage [MilliVolt] (-4096mV .. +4095mV) - If some channels are not used, their threshold voltage should be set to 4000mV. Do NOT use 0V since stray fluctuation of the voltage level at the open pin might otherwise introduce unwanted pulses.
  // int16_t   Obsolete_ExternClockLevel;   //!< External Clock Low/High Threshold Voltage [MilliVolt] (-4096mV .. +4095mV)

  int16_t   StopChnOffset[8];   //!< Measurement Offset for all Stop Channels [Ticks]

  // bool_t    Obsolete_UseExternalClock;   //!< Use the External Clock (TRUE) or the internal 40MHz Crystal (FALSE)
  bool_t    UsePulseGenStart;   //!< Use Pulse Generator to drive Start (TRUE) or external Start Input (FALSE)
  bool_t    UsePulseGenStop1;   //!< Use Pulse Generator to drive Stop1 (TRUE) or external Stop1 Input (FALSE) - Only implemented on TTM8-Boards before Rev. 4.0
  bool_t    PermitAutoPulseGenStart; //!< Use the Pulse Generator to automatically generate a Start Pulse in cont. I-Mode
  bool_t    UseDifferentialInputs; //!< Use Differential Input Signals (TRUE) or Asymmetric Inputs (FALSE) - Only implemented on TTM8-Boards before Rev. 3.2

  uint32_t  DataIdleTimeout;    //!< How low do we want to wait for a Timetag Data Packet to become completly filled, before we send a partially filled packet? [8ns Ticks]

  in_addr_t DataTargetIPAddr;   //!< Target IP-Address for Timetag Data Packets (use INADDR_ANY if you use TTMData_c::Connect() to inform the TTM8000-Board of the Target IP-Address)
  in_port_t DataTargetPort;     //!< Target UDP-Port for Timetag Data Packets (use 0 if you use TTMData_c::Connect() to inform the TTM8000-Board of the Target UDP-Port)
  uint16_t  PaddingC;           //!< Reserved
  uint32_t  NetMTU;             //!< Network MTU (Max. Transmission Unit) = Max. UDP Packet Size - Use 0 for Automatic

  uint16_t  UserData;           //!< Arbitrary User Data (e.g. Measurement ID)
 } TTMMeasConfig_t;

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief Timing Offset for individual channels depending on the Measurement Mode
  *
  * The 'native' measurements from the TTM8000 boards have offsets, that depend on
  * the individual board, the selected channel and the measurement mode.
  */
 typedef struct TTMChannelOffset_t {
  int16_t   IModeChnOffset[8];     //!< Channel dependent Offset for I-Mode (unused)
  int16_t   GModeChnOffset[2];     //!< Channel dependent Offset for G-Mode (unused)
  int16_t   RModeChnOffset[2];     //!< Channel dependent Offset for R-Mode (unused)
  int16_t   MModeChnOffset[32][2]; //!< Channel dependent Offset for M-Mode (unused)
 } TTMChannelOffset_t;

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** @brief Header for TTM8 Timetag Packets
  *
  * The TTMDataHeader is sent as header information with every packet of
  * TTM8 Timestamps. It makes it possible to identify TTM8 timestamp packets
  * and contains information about the packet contents.
  *
  * @warning The size of TTMDataHeader is NOT arbitrary!! Each NEW network
  * packet is aligned to a 4-byte boundry (see xtemac_fifo.c:212). To obtain
  * good preformance we want to transfer the actual payload via DMA. DMA
  * transfers should be aligned to 8-byte boundries (according to xtemac.h:455)
  * however it seems that alignment to a 4-byte boundry is actually sufficient
  * (see xdmav2.h:278). Since we can't guarantee 8-byte alignment anyways we
  * shall only attempt 4-byte alignment.
  * Each network packet starts with a 42 byte network header (14 byte Ethernet +
  * 20 byte IP + 8 byte UDP = 42 byte). If we choose the sizeof TTMDataHeader_t
  * to be 8n-2 byte, the location of the DMA target will be properly aligned.
  * We shall choose n=4 or sizeof(TTMDataHeader_t) = 30.
  * Note: While this provides correct alignment for the TTMServer, it is not
  * optimal for the PC, since the individual timetags are now misaligned. This
  * will reduce performance during processing on the PC.
  */
typedef struct TTMDataHeader_t
 {
  uint16_t  TTMPacketMagicA;  //!< Always TTMCookieA for Packet Type Identification
  uint16_t  TTMPacketMagicB;  //!< Always TTMCookieB for Packet Type Identification
  uint16_t  TTMDataMagicA;    //!< Always DataCookieA for Packet Type Identification
  uint16_t  TTMDataMagicB;    //!< Always DataCookieB for Packet Type Identification
  uint16_t  PacketVersion;    //!< Const 0x0401
  uint16_t  PacketCnt;        //!< Running Packet Counter to Detect Duplicated/Missing Packets
  uint8_t   DataFormat;       //!< Data Format (TTMDataFormat_t cast to a Byte)
  uint8_t   MModeDiv;         //!< Timing Resolution in M-Mode (not used in other modes)
  uint16_t  MModeTimeout;     //!< Timeout for Measurements in M-Mode (in 25ns Ticks)
  uint16_t  DigitalIOState;   //!< Current State of Digital IOs (Bit 15..10: Reserved - Bit 9: User Button - Bit 8: Reset Button - Bit 7..0 - DigitalIOIn)
  uint16_t  RunMagic;         //!< Magic Identification of Measurement Run

  uint16_t  GPXClockConf;     //!< Contents of GPX Register GPX7 (Low Word)   -- New in Data Format 4.01
  uint16_t  ReservedB;        //!< Reserved for Future Use
  uint16_t  ReservedC;        //!< Reserved for Future Use
  uint16_t  UserData;         //!< User Data (see: TTMMeasConfig_t.UserData)
  uint16_t  DataSize;         //!< Number of Data Bytes available
 } TTMDataHeader_t;
#define TTMCookie    htonl(0x54544D38)  //!< Magic Cookie for TTMDataHeader_t (= "TTM8")
#define DataCookie   htonl(0x44617461)  //!< Magic Cookie for TTMDataHeader_t (= "Data")

#define TTMCookieA   htons(0x5454) //!< High Word of TTMCookie (= "TT")
#define TTMCookieB   htons(0x4D38) //!< Low Word of TTMCookie (= "M8")
#define DataCookieA  htons(0x4461) //!< High Word of DataCookie (= "Da")
#define DataCookieB  htons(0x7461) //!< High Word of DataCookie (= "ta")

#define PacketVersionCookie 0x0401     //!< Packet Version Identifier 4.01

/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/** Data Format for ACAM GPX Timetags measured in I-Mode processed for 64-bit
  * WARNING: Microsoft Visual Studio has an interesting way to handle an uint64_t
  * (or an unsigned long long) in a bitfield, resulting in a TimetagI64 that is
  * 16 bytes large. Obviously that makes a portable solution with bitfields
  * impossible and we are reduced to using plain variables and do the bitfield
  * extraction ourselves ;(
  *
  * Beware: Microsoft Visual Studio uses creative padding in bitfields if not
  * all the base types of a bitfield are of equal size. Thus we shall use
  * uint64_t even for bitfield that are just a single bit long. Using mixed
  * basetypes is no problem for gcc. Thus we can use shorter (more efficient)
  * types on Linux.
  *
  */
// (Visual Studio 6: _MSC_VER = 1200 - Visual Studio 2005: _MSC_VER = 1400)
// #if defined(_WIN32) && defined (_MSC_VER)  // Microsoft Visual Studio
//   #define UseBitfield64 0
// #else
//   #define UseBitfield64 1
// #endif

/** @brief Do we want to use compiler supplied bitfields to access 64-bit Timetags,
  *        rather than doing bit manipulation 'by hand'.
  */
#define UseBitfield64 1
/** @brief Do we want to use compiler supplied bitfields to access 32-bit Timetags,
  *        rather than doing bit manipulation 'by hand'.
  */
#define UseBitfield32 1

/** @brief Data Format for ACAM GPX Timetags measured in I-Mode expanded to 64-bit
  *
  */
#if UseBitfield64
/** Beware: Microsoft Visual Studio uses creative padding in bitfields if not
  * all the base types of a bitfield are of equal size. Thus we shall use
  * uint64_t even for bitfield that are just a single bit long. Using mixed
  * basetypes is no problem for gcc. Thus we can use shorter (more efficient)
  * types on Linux.
  */
  // (Visual Studio 6: _MSC_VER = 1200 - Visual Studio 2005: _MSC_VER = 1400)
  #if defined(_WIN32) && defined (_MSC_VER)  // Microsoft Visual Studio
  struct TimetagI64
   {
    uint64_t Time    : 60;  //!< Timestamp                         - Bit  0..59
    uint64_t Slope   :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   60
    uint64_t Channel :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 61..63
   };
  #else
  struct TimetagI64
   {
    uint64_t Time    : 60;  //!< Timestamp                         - Bit  0..59
    uint8_t Slope    :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   60
    uint8_t Channel  :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 61..63
   };
  #endif
#else
struct TimetagI64
 {
  uint64_t Data;
 };
#endif

/**  @brief Data Format for ACAM GPX Timetags measured in I-Mode expanded to 64-bit
  *         and compressed to 32-bit words
  *
  *  The upper Bits of a TimetagI64.Time value rarely change from one Timetag
  *  to the next. We can use this fact to build a compression scheme. Every
  *  TimetagI64 Timetag is used to build a High and Low Word.\n
  *  The High Word has following Format:
  *    - uint32_t  TimeHigh : 31;  // Bit  0..30 (TimetagI64 Bits: Time 27..57)
  *    - uint8_t   HighLow  :  1;  // Bit   31   (Const '1')
  *
  *  The Low Word has following Format:
  *    - uint32_t  TimeLow  : 27;  // Bit  0..26 (TimetagI64 Bits: Time 0..26)
  *    - uint8_t   Slope    :  1;  // Bit   27   (TimetagI64 Bits: Slope)
  *    - uint8_t   Channel  :  3;  // Bit 28..30 (TimetagI64 Bits: Channel)
  *    - uint8_t   HighLow  :  1;  // Bit   31   (Const '0')
  *
  * Note: TimetagI64 Bits Time 58.59 are not encoded in either the High- or
  * Low-Word and are lost. However since they change only every nine month,
  * they are rarely needed (and can easily be reconstructed in software if
  * they should actually be essential).\n
  * If the High Word of a Timetag is the same as the High Word of the
  * previous Timetag, we shall only send the Low Word. If the High Word is
  * different, we shall send both the High Word and the Low Word. Since the
  * value of the High Word changes only every about 11ms (2^27 * 82.3045ps),
  * (90.5Hz) we will send only the Low Word for almost all Timetags and
  * obtain almost 50% compression.
  */
#if UseBitfield32
struct TimetagI64Pack
 {
  uint32_t Payload : 31;  //!< Packed Timetag Payload - Bit  0..30
  uint32_t HighLow :  1;  //!< High/Low Word Marker   - Bit   31
 };
#else
struct TimetagI64Pack
 {
  uint32_t Data;
 };
#endif

/** @brief Data Format for ACAM GPX Timetags measured in I-Mode
  *                                     by multiple boards expanded to 64-bit
  *
  */
#if UseBitfield64
/** Beware: Microsoft Visual Studio uses creative padding in bitfields if not
  * all the base types of a bitfield are of equal size. Thus we shall use
  * uint64_t even for bitfield that are just a single bit long. Using mixed
  * basetypes is no problem for gcc. Thus we can use shorter (more efficient)
  * types on Linux.
  *
  * Note: 2^56 * 82.3045ps = 5 930 666s = 68.6 days
  */
  // (Visual Studio 6: _MSC_VER = 1200 - Visual Studio 2005: _MSC_VER = 1400)
  #if defined(_WIN32) && defined (_MSC_VER)  // Microsoft Visual Studio
  struct MultiBoardTimetagI64
   {
    uint64_t Time    : 56;  //!< Timestamp                         - Bit  0..55
    uint64_t Slope   :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   56
    uint64_t Channel :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 57..59
    uint64_t BoardID :  4;  //!< Board Index                       - Bit 60..63
   };
  #else
  #if 1
  struct MultiBoardTimetagI64
   {
    uint64_t Time    : 56;  //!< Timestamp                         - Bit  0..55
    uint8_t Slope    :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   56
    uint8_t Channel  :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 57..59
    uint8_t BoardID  :  4;  //!< Board Index                       - Bit 60..63
   };
  #else
  struct MultiBoardTimetagI64
   {
    uint64_t Time    : 56;  //!< Timestamp                         - Bit  0..55
    union {
      struct {
        uint8_t Slope    :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   56
        uint8_t Channel  :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 57..59
        uint8_t BoardID  :  4;  //!< Board Index                       - Bit 60..63
       }
      uint8_t EvtSrc : 8;  //!< Slope/Channel/Board all in _one_ field - Bit 56..63
     };
   };
  #endif
  #endif
#else
struct MultiBoardTimetagI64
 {
  uint64_t Data;
 };
#endif
/**  @brief Data Format for ACAM GPX Timetags measured in I-Mode by
  *         multiple boards expanded to 64-bit and compressed to 32-bit words
  *
  *  The upper Bits of a MultiBoardTimetagI64.Time value rarely change from
  *  one Timetag to the next. We can use this fact to build a compression
  *  scheme. Every MultiBoardTimetagI64 Timetag is used to build a High and
  *  Low Word.\n
  *  The High Word has following Format:
  *    - uint32_t  TimeHigh : 31;  // Bit  0..30 (MultiBoardTimetagI64 Bits: Time 23..53)
  *    - uint8_t   HighLow  :  1;  // Bit   31   (Const '1')
  *
  *  The Low Word has following Format:
  *    - uint32_t  TimeLow  : 23;  // Bit  0..22 (MultiBoardTimetagI64 Bits: Time 0..22)
  *    - uint8_t   Slope    :  1;  // Bit   23   (MultiBoardTimetagI64 Bits: Slope)
  *    - uint8_t   Channel  :  3;  // Bit 24..26 (MultiBoardTimetagI64 Bits: Channel)
  *    - uint8_t   BoardID  :  4;  // Bit 27..30 (MultiBoardTimetagI64 Bits: Board Index)
  *    - uint8_t   HighLow  :  1;  // Bit   31   (Const '0')
  *
  * Note: TimetagI64 Bits Time 54.55 are not encoded in either the High- or
  * Low-Word and are lost. However since they change only every 17.2 days,
  * they are rarely needed (and can easily be reconstructed in software if
  * they should actually be essential).\n
  * If the High Word of a Timetag is the same as the High Word of the
  * previous Timetag, we shall only send the Low Word. If the High Word is
  * different, we shall send both the High Word and the Low Word. Since the
  * value of the High Word changes only every about 0.69ms (2^23 * 82.3045ps),
  * (~1448Hz) we will send only the Low Word for almost all Timetags and
  * obtain almost 50% compression.
  */
#if UseBitfield32
struct MultiBoardTimetagI64Pack
 {
  uint32_t Payload : 31;  //!< Packed Timetag Payload - Bit  0..30
  uint32_t HighLow :  1;  //!< High/Low Word Marker   - Bit   31
 };
#else
struct MultiBoardTimetagI64Pack
 {
  uint32_t Data;
 };
#endif

/** @brief Raw Data Format for ACAM GPX Timetags measured in I-Mode.
  *
  * @see ACAM TDC-GPX Datasheet (p.19) - Chapter 1.7.2
  * Note: The GPX internally splits its 8 ports into 2x 4 ports and
  * maintains seperate event lists for each group of ports. Thus it
  * uses only 2 bits to identify the channel (within each group)! The
  * third channel bit is inserted by the FPGA on the TTM Board
  */
#if UseBitfield32
struct TimetagIRaw
 {
  uint32_t Time        : 17;   //!< Timestamp                         - Bit  0..16
  uint32_t Slope       :  1;   //!< Slope (1..Rising/0..Falling)      - Bit   17
  uint32_t StartCnt    :  8;   //!< Start Pulse Counter (GPX)         - Bit 18..25
  uint32_t Channel     :  3;   //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 26..28 (See note above!)
  uint32_t ExtStartCnt :  3;   //!< Extended Start Pulse Counter (FPGA intern.) - Bit 29..31 (only for TTFormat_IMode_Cont_RAW32)
 };
#else
struct TimetagIRaw
 {
  uint32_t Data;
 };
#endif

/** @brief Raw Data Format for ACAM GPX Timetags measured in G-Mode.
  *
  * @see ACAM TDC-GPX Datasheet (p.20) - Chapter 1.7.2
  */
#if UseBitfield32
struct TimetagGRaw
 {
  uint32_t Time      : 22; //!< Timestamp                         - Bit   0..21 - max. Value: 0x1B0000!
  uint32_t Slope     :  1; //!< Slope (1..Rising/0..Falling)      - Bit    22
  uint32_t ReservedA :  5; //!< Reserved                          - Bit  23..27
  uint32_t Channel   :  1; //!< Channel (0..1 +1 -> Stop1..Stop2) - Bit    28
  uint32_t ReservedB :  3; //!< Reserved                          - Bit  29..31
 };
#else
struct TimetagGRaw
 {
  uint32_t Data;
 };
#endif

/** @brief Raw Data Format for ACAM GPX Timetags measured in R-Mode.
  *
  * @see ACAM TDC-GPX Datasheet (p.20) - Chapter 1.7.2
  */
#if UseBitfield32
struct TimetagRRaw
 {
  uint32_t Time      : 23; //!< Timestamp                         - Bit   0..22
  uint32_t ReservedA :  5; //!< Reserved                          - Bit  23..27
  uint32_t Channel   :  1; //!< Channel (0..1 +1 -> Stop1..Stop2) - Bit    28
  uint32_t ReservedB :  3; //!< Reserved                          - Bit  29..31
 };
#else
struct TimetagRRaw
 {
  uint32_t Data;
 };
#endif

/** @brief Raw Data Format for ACAM GPX Timetags measured in M-Mode.
  *
  * @see ACAM TDC-GPX Datasheet (p.20) - Chapter 1.7.2
  */
#if UseBitfield32
struct TimetagMRaw
 {
  uint32_t Time      : 23; //!< Timestamp                         - Bit  0..22
  uint32_t StartCnt  :  5; //!< Start Pulse Counter (FPGA intern.)- Bit 23..27
  uint32_t Channel   :  1; //!< Channel (0..1 +1 -> Stop1..Stop2) - Bit   28
  uint32_t ReservedB :  3; //!< Reserved                          - Bit 29..31
 };
#else
struct TimetagMRaw
 {
  uint32_t Data; };
#endif

/** @brief Do we want to use a compiler supplied union to store Timetags of
  *        different types, rather than using a byte array and doing typecasts
  *        manually. */
#define UseDataPacketUnion 1

/** @brief Timetag Network Packet
  *
  * A Timetag Network Packet containing a Header with information about the
  * packet contents and the actual Timetag Data.
  * @note Usually the Data field will NOT be fully occupied. See Header.DataSize
  * to discover how many Bytes (NOT Data Elements!) are actually available.
  * @note The Data contained in a TTMDataPacket that is sent over the
  * network is at most 8KByte in size. However since the same data structure
  * will also be used to expand such a network packet from compressed
  * to plain 64-bit Timetags, we need twice as much room to accomodate the
  * expanded data. Furthermore sorting can add additional fluctuations in
  * the number of timetags passed. Thus we shall add an additional 16KByte.
  * @warning Conceptually we can think of a TTMDataPacket to consist of a
  * Header and a Data Field, where the Data is a union whose actual
  * format depends on the Header.DataFormat field. However the Header
  * contains just 30 byte (which can't be changed, see note at TTMDataPacket_t)
  * thus most compilers will add 2 byte padding between the Header and
  * Data. In order to avoid this padding we will add a 2-byte dummy word
  * _before_ the Header to get optimal alignment.
  * The use of the union is optional.
  */
typedef struct TTMDataPacket_t
 {
  uint16_t        Padding;     //!< Alignment Padding - Do not move/delete!!!
  TTMDataHeader_t Header;      //!< Packet Header
#if UseDataPacketUnion
  union
   {
    uint8_t               RawData[2* 16384]; // Raw Packet Payload (see Note above!)
    uint32_t              RawTime32[2* 4096];
    uint64_t              RawTime64[2* 2048];
    struct TimetagI64     TimetagI64[2* 2048];
    struct TimetagI64Pack TimetagI64Pack[2* 4096];
    struct MultiBoardTimetagI64     MultiTimetagI64[2* 2048];
    struct MultiBoardTimetagI64Pack MultiTimetagI64Pack[2* 4096];
    struct TimetagIRaw    TimetagIRaw[2* 4096];
    struct TimetagGRaw    TimetagGRaw[2* 4096];
    struct TimetagRRaw    TimetagRRaw[2* 4096];
    struct TimetagMRaw    TimetagMRaw[2* 4096];
   } Data;                     //!< Timetag Packet Payload
#else
  uint8_t         Data[32768]; //!< Raw Packet Payload (see Note above!)
#endif
 } TTMDataPacket_t;

/** @brief Correction Terms for Cable Delays and TTM8 Internal Delays
  *
  * Each Input of the TTM8 Board has an individual input delay that
  * that depends on things like the length of the cable used to connect
  * the pulse source with the TTM8 Board and on internal delays of the
  * TTM8 Board. These delays have to be subtracted from the results to
  * obtain correct measurement results.\n
  * Since the Delays are unique to each Measurement setup, these term
  * have to be determined by experiment each time. Use the application
  * ttmcalibrate, shipped with the TTM8 Board to aid your calibration
  * process.\n
  * Correction Terms are measured in BINs (of appropriate duration for
  * the specific Measurement Mode).
  */
typedef struct TTMPortCableOffset_t
 {
  int32_t IMode[8][2];   //!< Delays for I-Mode[Stop1..8][Rising/Falling]
  int32_t GMode[2][2];   //!< Delays for G-Mode[Stop1..2][Rising/Falling]
  int32_t RMode[2];      //!< Delays for R-Mode[Stop1..2]
  int32_t MMode[32][2];  //!< Delays for M-Mode[MDiv0..31][Stop1..2]
 }  TTMPortCableOffset_t;

/** @brief Configuration of the External Clock Input/Output
 *
 * The TTM8 Board has a Clock Synthesizer, that can operate using either the
 * TTM8's internal oscillator or an external reference clock. This external
 * reference clock must operate at 10, 20, 40 or 80MHz. In order to support
 * a wide range of logic families, the threshold voltage that distiguishes
 * between low- and high-logic levels can be set in the range +/- 4.095V.
 *
 * Besides providing the clocks necessary for the internal operation of the
 * TTM8, the Clock Synthesizer can optionally provide an external clock
 * output running at 1, 2, 5, 10, 20, 40 or 80 MHz.
 */
typedef struct TTMExternClkConfig_t
 {
  bool_t    UseExternClkIn;     //!< Do we want to use the External Clock Input?
  bool_t    ExternClkInActive;  //!< Is the External Clock Input actually used?
                                //    (or do we use the internal clock as fallback solution)?
  uint32_t  ExternClkInFreq;    //!< Frequency of the External Clock Input [Hz]
  uint16_t  ExternClkInRefVoltage; //!< Reference Voltage for the External Clock Input [mV]
  bool_t    UseExternClkOut;    //!< Do we want to use the External Clock Output?
  uint32_t  ExternClkOutFreq;   //!< Frequency of the External Clock Output [Hz]
  uint32_t  ExternClkOutFreqMaxPPMErr; //!< Max. Ext. Clock Output Error [ppm]
 } TTMExternClkConfig_t;

/** @brief Number of Events recorded on each Trigger Input
 *
 */
typedef struct TTMEventCnt_t
 {
  uint32_t SysTimeHigh;  //!< System Time of the TTM8 Module (High Word)
  uint32_t SysTimeLow;   //!< System Time of the TTM8 Module (Low Word)
  uint32_t EventCnt[8];  //!< Number of Events recorded on each channel
 } TTMEventCnt_t;

/** @brief Definition of a Multi-Channel Correlation
 *
 * A Multi-Channel Correlation checks if multiple events occur at the
 * 'same' time (i.e. within the windows defined in ConfigTiming()). Any
 * combination of channels can be part of each correlation.
 * In addition to this there exists an option to count correlation
 * only for a given timespan after an event occured on a specific channel.
 */
struct MultiCorrInfo
 {
  bool_t   ChannelActive[16]; //!< Which Channels/Edges shall be part of the MultiChannel Correlation?
  int      TriggerChnIdx;   //!< Which Event shall be used to enable the Correlation Counter
                            //   Use -1 for 'None' - i.e. The Correlation Counter is permanently enabled
                            //      0.. 7 for Stop1..8 Rising Edge and
                            //      8..15 for Stop1..8 Falling Edge
  uint32_t ActiveMicroTime; //!< How long will the Correlation Counter remain enabled after a Trigger Event?
                            //  Use 0 for 'forever' or specify the number of microseconds required.
 };

/** @brief Health State of the Reference Clock Sources
  *
  */
typedef struct TTMClockSourceState_t {
  uint32_t MeasureCnt;               //!< How many measurement where performed to determine ClockSourceState?
  uint32_t IntClockActiveCnt;        //!< How often was the Internal Clock in use?
  uint32_t IntClockLossOfSignalCnt;  //!< How often was there a Loss-of-Signal Error for the Internal Clock?
  uint32_t IntClockFreqOffsetCnt;    //!< How often was there a Frequency Offset Error for the Internal Clock?
  uint32_t ExtClockActiveCnt;        //!< How often was the External Clock in use?
  uint32_t ExtClockLossOfSignalCnt;  //!< How often was there a Loss-of-Signal Error for the External Clock?
  uint32_t ExtClockFreqOffsetCnt;    //!< How often was there a Frequency Offset Error for the External Clock?
 } TTMClockSourceState_t;

/**********************************************************************/
/* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */

/*  Network Communication between the FlexIO device and the control PC is
 *  done using UDP. While it is possible to do broadcasts to all local
 *  IP-Addresses to discover boards, it is not possible (or advisable!)
 *  to broadcast to all ports. Thus we need to predefine a port (FlexIOCntrlPort)
 *  that will be used by the FlexIO server to listen for commands and
 *  supply responses.
 *  The FlexIO server needs a second port to send application data. While
 *  it could theoretically use any port it chooses for this purpose, we
 *  shall still define a fixed port (FlexIODataPort).
 *  Applications running on the local PC that configure the FlexIO and then
 *  receive the data can (and should for reasons of flexibility) use
 *  arbitrary ports on the PC. They can obtain ports from the operating
 *  system, and then tell the FlexIO to communicate with these ports.
 *  If the configuration application is however separate from the data
 *  processing application, it is necessary that the configuration app.
 *  knowns where the data processing app will listen for data. Since they
 *  are separate applications, they can not communicate internally, so
 *  they either have to communicate externally (e.g. shared memory,
 *  messages etc.) or prearrange a data port. This is an alternate usage
 *  of FlexIODataPort.
 */
/** @brief UDP Port used by the Control Channel of the FlexIO Server */
#define FlexIOCntrlPort 10501

/** @brief UDP Port used by the Data Channel of the FlexIO Server */
#define FlexIODataPort  10502

#if defined __cplusplus
}  /* extern "C" */
#endif

/**********************************************************************
 *                           FlexIOLibTypes.h                         *
 **********************************************************************/
#endif /* FlexIOLibTypes_h */
