int relayPins[] = {12, 11, 10, 9};
bool relayStates[] = {false, false, false, false};
void setup() {
  Serial.begin(9600);
  Serial.println("Relay Control Ready");
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);
  }
}
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    processCommand(cmd);
  }
}
void processCommand(String cmd) {
  cmd.toUpperCase();
  if (cmd == "S") {
    sendStatus();
  }
  else if (cmd == "A+") {
    setAllRelays(true);
  }
  else if (cmd == "A-") {
    setAllRelays(false);
  }
  else if (cmd.length() == 1 && cmd[0] >= '1' && cmd[0] <= '4') {
    int relay = cmd[0] - '1';
    toggleRelay(relay);
  }
  else {
    Serial.println("Commands: 1-4(toggle), A+(all on), A-(all off), S(status)");
  }
}
void setRelay(int index, bool state) {
  relayStates[index] = state;
  digitalWrite(relayPins[index], state ? LOW : HIGH);
  Serial.print("R");
  Serial.print(index + 1);
  Serial.println(state ? ":ON" : ":OFF");
}
void toggleRelay(int index) {
  setRelay(index, !relayStates[index]);
}
void setAllRelays(bool state) {
  for (int i = 0; i < 4; i++) {
    setRelay(i, state);
  }
}
void sendStatus() {
  Serial.print("Status: ");
  for (int i = 0; i < 4; i++) {
    Serial.print("R");
    Serial.print(i + 1);
    Serial.print(relayStates[i] ? ":ON " : ":OFF ");
  }
  Serial.println();
}