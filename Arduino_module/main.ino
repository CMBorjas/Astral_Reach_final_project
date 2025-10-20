int ledPin = 3;
int brake_led = 3;
const int trigPin = 9;
const int echoPin = 10;
float brightness = 0;
long duration, distance;

long Sensor_Reading() {
  long dur, dis;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  dur = pulseIn(echoPin, HIGH);
  dis = (dur/2) / 29.1;
  delay(10);
  return dis;
}


void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  distance = Sensor_Reading();
  Serial.println(distance);
  // if (distance < 10) {
  //   Serial.println("STOP");
  //   Serial.println(distance);
  //   brightness = 255;
  //   analogWrite(brake_led, brightness);
  // }
  // else if (distance > 500){
  //   Serial.println("LOST");
  //   analogWrite(brake_led, 0);
  // }
  // else{
  //   Serial.print("Distance: ");
  //   Serial.println(distance);
  //   analogWrite(brake_led, 0);

  // }

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // remove spaces or line breaks

    if (command == "ON") {
      digitalWrite(ledPin, HIGH);
      // Serial.println("LED is ON");
    }
    else if (command == "OFF") {
      digitalWrite(ledPin, LOW);
      // Serial.println("LED is OFF");
    }
  }
}


