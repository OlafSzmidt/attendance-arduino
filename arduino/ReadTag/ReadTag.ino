#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "WiFly.h"
#include "HTTPClient.h"


// Network Settings! This is the credentials that are used by the arduino
// to connect to the server. Note: the website also needs to be hosted on the
// same network.
#define SSID      "Attendance"
#define KEY       "attendancesystem"
#define AUTH      WIFLY_AUTH_WPA2_PSK
#define HTTP_POST_URL "http://192.168.43.205:8000/cardScan/"

// NFC Shield initlization
PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

// WiFi initialization
SoftwareSerial uart(2, 3);
WiFly wifly(&uart);
HTTPClient http;
char get;

// setup() gets ran as soon as the arduino begins to have sufficient power.
// WiFly UART Baud rate is set at 9600 and all serial debugs can be listened
// to at that rate. Setup joins the network and disables welcome messages
// that interrupt HTTP communication.
void setup(void) {
    uart.begin(9600);

    Serial.begin(9600);

    Serial.println("Attendance Monitor");
    pinMode(9, OUTPUT);

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

    delay(1000);
    noTone(9);

    nfc.begin();

    // Command disables welcome message from Seeed Studio WiFi shield.
    // The welcome message can interrupt the POST request later and wrong bytes
    // are sent over wifi. The server is unable to read the incoming request
    // and the whole thing errors. In this case WiFi Shield sends a "*HELLO*" stream
    // which would often be appended to the method type in the HTTP library.
    wifly.sendCommand("set comm remote 0\r");
}


// Loop is a function that gets called consecutively (ie. as soon as the previous
// terminates, this one begins). It listens for a NFC tag to be present at the
// antenna, reads data and sends an ID across WiFI using hand made HTTP protocols.
void loop(void) {
    Serial.println("\nWaiting for a NFC card to be pressed.\n");
    if (nfc.tagPresent())
    {
        NfcTag tag = nfc.read();
        Serial.println(tag.getUidString());

        Serial.println("\r\n\r\nTry to post data to url - " HTTP_POST_URL);
        Serial.println("-------------------------------");


        String stringTag = tag.getUidString();

        // sizeof was returning 6 for the tag... Different std library causing
        // confusion built in length() used instead:
        // https://www.arduino.cc/en/Tutorial/StringLength
        char __tag[stringTag.length() + 1];
        stringTag.toCharArray(__tag, sizeof(__tag));

        while (http.post(HTTP_POST_URL, __tag, 10000) < 0) {
        }

        String response = "";
        while (wifly.receive((uint8_t *)&get, 1, 1000) == 1) {
          response += get;
        }

        // Checks if a user has been found and marked present or not. Appropriate
        // buzzer sound is set (low tone for error and high for correct user).
        if(response.endsWith("404*CLOS*")) {
          tone(9, 100);
          delay(1000);
          noTone(9);
        }
        else {
          tone(9, 1000);
          delay(1000);
          noTone(9);
        }
    }
}
