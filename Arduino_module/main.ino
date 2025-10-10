const int trigPin = 9;
const int echoPin = 10;
const int brake_led = 3;
const int lost_led = 7;

long duration, distance;
float brightness = 0;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  if (distance < 10) {
    Serial.println("Stop!!!!!!");
    Serial.println(distance);
    brightness = 255;
    digitalWrite(lost_led,LOW);
    analogWrite(brake_led, brightness);
  }
  else if (distance > 500){
    Serial.println("lost detection");
    digitalWrite(lost_led,HIGH);
    analogWrite(brake_led, 0);
  }
  else{
    Serial.print("Distance: ");
    Serial.println(distance);
    digitalWrite(lost_led,LOW);
    analogWrite(brake_led, 0);
`
  }
  delay(10);
}