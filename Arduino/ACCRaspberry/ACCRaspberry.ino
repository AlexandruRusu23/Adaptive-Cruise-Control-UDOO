#include <AFMotor.h>

#define RIGHT_BACK_MOTOR 0
#define LEFT_BACK_MOTOR 1
#define LEFT_FRONT_MOTOR 2
#define RIGHT_FRONT_MOTOR 3

AF_DCMotor rightBackMotor(1, MOTOR12_64KHZ);
AF_DCMotor leftBackMotor(2, MOTOR12_64KHZ);
AF_DCMotor leftFrontMotor(3, MOTOR12_64KHZ);
AF_DCMotor rightFrontMotor(4, MOTOR12_64KHZ);

int motorSpeedValue[4] = {0, 0, 0, 0};
bool GoBackWard[4] = {false, false, false, false};

unsigned long serialData;
int inByte;

void setup() {
  Serial.begin(9600);
}
 
void loop() {
  CommandManager();
  //right - back motor
  rightBackMotor.setSpeed(motorSpeedValue[0]);
  if (!GoBackWard[RIGHT_BACK_MOTOR])
    rightBackMotor.run(FORWARD);
   else
    rightBackMotor.run(BACKWARD);
  //left - back motor
  leftBackMotor.setSpeed(motorSpeedValue[1]);
  if (!GoBackWard[LEFT_BACK_MOTOR]) 
    leftBackMotor.run(FORWARD);
  else
    leftBackMotor.run(BACKWARD);
  //left - front motor
  leftFrontMotor.setSpeed(motorSpeedValue[2]);
  if (!GoBackWard[LEFT_FRONT_MOTOR]) 
    leftFrontMotor.run(FORWARD);
  else
    leftFrontMotor.run(BACKWARD);
  //rigth - front motor
  rightFrontMotor.setSpeed(motorSpeedValue[3]);
  if (!GoBackWard[RIGHT_FRONT_MOTOR]) 
    rightFrontMotor.run(FORWARD);
  else
    rightFrontMotor.run(BACKWARD);
  delay(50);
}

long getSerial()
{
  serialData = 0;
  if (Serial.available() > 0) {
    while(inByte != '/')
    {
      inByte = Serial.read();
      if(inByte > 0 && inByte != '/')
      {
        serialData = serialData * 10 + inByte - '0';
        Serial.println(serialData);
      }
    }
    inByte = 0;
  }
  return serialData;
}

void CommandManager()
{
  getSerial();
  switch(serialData)
  {
    case 1: // speed up
    {
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 150)
          motorSpeedValue[i] = 150;
        else if (motorSpeedValue[i] < 250)
          motorSpeedValue[i] += 10;
      }
      break;
    }
    case 2: // speed down
    {
      for(int i = 0; i<4; i++)
      {
        if (motorSpeedValue[i] > 150)
          motorSpeedValue[i] -= 150;
        else
          motorSpeedValue[i] = 0;
      }
      break;
    }
    case 3: // brake
    {
      for(int i = 0; i<4; i++)
      {
        GoBackWard[i] = false;
      }
      for(int i = 0; i<4; i++)
      {
        motorSpeedValue[i] = 0;
      }
      break;
    }
    case 4: // turn right
    {
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 70)
          motorSpeedValue[i] = 70;
      }
      
      if (motorSpeedValue[LEFT_BACK_MOTOR] > 70)
      {
        motorSpeedValue[LEFT_BACK_MOTOR] -= 10;
        motorSpeedValue[LEFT_FRONT_MOTOR] = motorSpeedValue[LEFT_BACK_MOTOR];
      }

      if (motorSpeedValue[RIGHT_FRONT_MOTOR] < 250)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] += 10;
        motorSpeedValue[RIGHT_BACK_MOTOR] = motorSpeedValue[RIGHT_FRONT_MOTOR];
      }
      break;
    }
    case 5: // turn left
    {
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 70)
          motorSpeedValue[i] = 70;
      }
     
      if (motorSpeedValue[LEFT_BACK_MOTOR] < 250)
      {
        motorSpeedValue[LEFT_BACK_MOTOR] += 10;
        motorSpeedValue[LEFT_FRONT_MOTOR] = motorSpeedValue[LEFT_BACK_MOTOR];
      }

      if (motorSpeedValue[RIGHT_FRONT_MOTOR] > 70)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] -= 10;
        motorSpeedValue[RIGHT_BACK_MOTOR] = motorSpeedValue[RIGHT_FRONT_MOTOR];
      }
      break;
    }
    case 6: // go back
    {
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 150)
          motorSpeedValue[i] = 150;
        GoBackWard[i] = true;
      }
    }
  }
  Serial.flush();
}
