#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "WiFly.h"
#include "HTTPClient.h"


// Network Settings!
#define SSID      "OLKAROLKA123"
#define KEY       "85386C52C2"
// WIFLY_AUTH_OPEN / WIFLY_AUTH_WPA1 / WIFLY_AUTH_WPA1_2 / WIFLY_AUTH_WPA2_PSK
#define AUTH      WIFLY_AUTH_WPA2_PSK
#define HTTP_GET_URL "http://httpbin.org/get?hello=world"
#define HTTP_POST_URL "http://192.168.1.248:8000/cardScan/"


// NFC init
PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

// Wifi init
SoftwareSerial uart(2, 3);
WiFly wifly(&uart);
HTTPClient http;
char get;

char json[400];

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
    
    delay(5000);

    nfc.begin();

    // Command disables welcome message from Seeed Studio WiFi shield.
    // The welcome message can interrupt the POST request later and wrong bytes
    // are sent over wifi. The server is unable to read the incoming request
    // and the whole thing errors. In this case WiFi Shield sends a "*HELLO*" stream
    // which would often be appended to the method type in the HTTP library.
    wifly.sendCommand("set comm remote 0\r");
}

void loop(void) {
    Serial.println("\nWaiting for a NFC card to be pressed.\n");
    if (nfc.tagPresent())
    {
        NfcTag tag = nfc.read();
        Serial.println(tag.getUidString());

        // There are C++ libraries that can construct JSON objects or strings
        // but we are trying to keep the arduino as lightweight as possible so
        // constructing it ourselves. However, no standard library (std) in the Uno
        // means this is difficult. 

        // Note: sprintf is unsafe
        
        Serial.println("\r\n\r\nTry to post data to url - " HTTP_POST_URL);
        Serial.println("-------------------------------");


        String stringTag = tag.getUidString();
        
        // sizeof was returning 6 for the tag... Different std library causing confusion
        // built in length() used instead: https://www.arduino.cc/en/Tutorial/StringLength     
        // Is +1 needed?
        char __tag[stringTag.length() + 1];

        Serial.println(sizeof(__tag));
        
        stringTag.toCharArray(__tag, sizeof(__tag));
        
        while (http.post(HTTP_POST_URL, __tag, 10000) < 0) {
        }
        while (wifly.receive((uint8_t *)&get, 1, 1000) == 1) {
          Serial.print(get);
        }
    }
    
    delay(1500);
}
