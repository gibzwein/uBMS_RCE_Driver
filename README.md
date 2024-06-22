# Sterownik RCE
Sterownik na bazie ESP32, pobierający informacje o godzinowych/kwadransowych cenach energii elektrycznej i sterujący przekaźnikami.\
Urządzenie służy do załaczania i wyłączania innych urządzeń na podstawie ceny rynkowej.

Potrzebne elementy:
  1. ESP32 4ch relay board
  2. SSD1306 display
  3. Przewody do połączenia ESP32 z OLED
  4. Konwerter USB=>UART

Opcjonalnie:
  Obudowa - w trakcie doboru

Proces instalacji:
  1. Na płytkę ESP32 4ch relay board wgrywamy najnowszy Micropython zgodnie z instrukcją:\
     https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/
  2. Ściągamy zawartość niniejszego repozytorium.
  3. W pliku credentials.py podajemy swoje dane sieci WiFi i hasło
  4. W pliku config, możemy edytować progi przełączania przekaźników w %, z 1/2 i 2/3 oraz próg zatrzymania produkcji. Plik xls w repozytorium.
  5. Ja używam Visual Studio Code i dodatku PyMakr, ale dostępne jest wiele innych rozwiązań.
  6. Wgrywamy potrzebne pliki na płytkę ESP32 Relay board

Jeżeli coś jest niejasne, lub coś Ci nie wychodzi. Napisz do mnie, lub porusz temat na Discord.

ToDo:
1. WiFi Failed timeout - should be sorted
2. Acces Point

Jeżeli podoba ci się to co robię i chcesz mnie wesprzeć w dalszych pracach nad projektem.\
<a href="https://suppi.pl/gibzwein" target="_blank"><img width="165" src="https://suppi.pl/api/widget/button.svg?fill=6457FD&textColor=ffffff"/></a>
