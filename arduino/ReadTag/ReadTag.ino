
#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "WiFly.h"

// Network Settings!
#define SSID      "OLKAROLKA123"
#define KEY       "85386C52C2"
#define AUTH      WIFLY_AUTH_WPA2_PSK

// NFC init
PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

// Wifi init
SoftwareSerial uart(2, 3);
WiFly wifly(&uart);

void setup(void) {
    uart.begin(9600);

    Serial.begin(9600);
    
    Serial.println("Attendance Monitor");
    // wifly needs a delay for initlization.
    delay(3000);

    uart.begin(9600);     // WiFly UART Baud Rate: 9600

    wifly.reset();

    Serial.println("-------Joining network-------");
    Serial.println("SSID: " SSID);
    if (wifly.join(SSID, KEY, AUTH)) {
      Serial.println("Network connection OK");
    } else {
      Serial.println("Network connection failed");
    }
    
    nfc.begin();
}

void loop(void) {
    Serial.println("\nWaiting for a NFC card to be pressed.\n");
    if (nfc.tagPresent())
    {
        NfcTag tag = nfc.read();
        Serial.println(tag.getUidString());
    }
    delay(1500);
}
