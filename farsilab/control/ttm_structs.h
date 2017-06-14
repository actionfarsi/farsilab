typedef unsigned char    uint8_t;
typedef unsigned short   uint16_t;
typedef unsigned long    uint32_t;
typedef unsigned __int64 uint64_t;

typedef signed char      int8_t;
typedef signed short     int16_t;
typedef signed int       int32_t;
typedef __int64          int64_t;

struct Timetag_I64
   {
    uint64_t time    : 60;  //!< Timestamp                         - Bit  0..59
    uint64_t slope   :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   60
    uint64_t channel :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 61..63
   };

<<<<<<< HEAD
=======
struct Timetag_I64c
   {
    uint32_t time    : 27;  //!< Timestamp                         - Bit  0..59
    uint32_t slope   :  1;  //!< Slope (1..Rising/0..Falling)      - Bit   60
    uint32_t channel :  3;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 61..63
    uint32_t highlow :  1;  //!< Channel (0..7 +1 -> Stop1..Stop8) - Bit 61..63
   };


>>>>>>> ttm
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

