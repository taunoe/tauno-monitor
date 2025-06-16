/*
 Started: 16.06.2025
 Author:  Tauno Erik
*/
const int del_val = 400;
static unsigned int counter = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {

  // 1
  /*
  Serial.println(counter);
  counter++;
  Serial.println("First");
  delay(del_val);
  Serial.println("Second");
  delay(del_val);
  Serial.println("Third");
  delay(del_val);
  */

  // 2
  
  Serial.print(counter);
  counter++;
  Serial.print("\n");
  Serial.print("First\n");
  delay(del_val);
  Serial.print("Second\n");
  delay(del_val);
  Serial.print("Third\n");
  delay(del_val);
  

  // 3
  /*
  Serial.print(counter);
  counter++;
  Serial.print("\r");
  Serial.print("First\r");
  delay(del_val);
  Serial.print("Second\r");
  delay(del_val);
  Serial.print("Third\r");
  delay(del_val);
  */

  // 4
  /*
  Serial.print(counter);
  counter++;
  Serial.print("\r\n");
  Serial.print("First\r\n");
  delay(del_val);
  Serial.print("Second\r\n");
  delay(del_val);
  Serial.print("Third\r\n");
  delay(del_val);
  */

  // 5
  /*
  Serial.print(counter);
  counter++;
  Serial.print(";");
  Serial.print("First;");
  delay(del_val);
  Serial.print("Second;");
  delay(del_val);
  Serial.print("Third;");
  delay(del_val);
  */

}
