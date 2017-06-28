#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

#define MAX_SPEED                 255
#define MIN_SPEED                 120
#define MAX_TRESHOLD              250
#define MIN_TRESHOLD              120
#define SPEED_UNIT                10

// motors indices in vector of speeds
#define LEFT_FRONT                0
#define RIGHT_FRONT               1
#define LEFT_BACK                 2
#define RIGHT_BACK                3

#define TURNING_LEFT              2
#define TURNING_RIGHT             1
#define DISABLED                  0

#define MOTORS_NR                 4

Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_DCMotor *leftBackMotor = AFMS.getMotor(1);
Adafruit_DCMotor *rightBackMotor = AFMS.getMotor(2);
Adafruit_DCMotor *rightFrontMotor = AFMS.getMotor(3);
Adafruit_DCMotor *leftFrontMotor = AFMS.getMotor(4);

int normalSpeed = 0;
int directionSpeed = 0;
int turning;

int motorSpeedValue[MOTORS_NR] = {0, 0, 0, 0};
bool GoBackWard = false;

unsigned long print_timer = 0;

unsigned long serialData;
int inByte;
String action;

void setup()
{
  AFMS.begin();
  Serial.begin(115200);
}

void loop()
{
  CommandManager();
  if (millis() - print_timer > 500)
  {
    PrintCarData();
    print_timer = millis();
  }

  rightBackMotor->setSpeed(motorSpeedValue[RIGHT_BACK]);
  leftBackMotor->setSpeed(motorSpeedValue[LEFT_BACK]);
  rightFrontMotor->setSpeed(motorSpeedValue[RIGHT_FRONT]);
  leftFrontMotor->setSpeed(motorSpeedValue[LEFT_FRONT]);

  if (GoBackWard == false)
  {
    rightBackMotor->run(FORWARD);
    leftBackMotor->run(FORWARD);
    rightFrontMotor->run(FORWARD);
    leftFrontMotor->run(FORWARD);
  }
  else
  {
    rightBackMotor->run(BACKWARD);
    leftBackMotor->run(BACKWARD);
    rightFrontMotor->run(BACKWARD);
    leftFrontMotor->run(BACKWARD);
  }

  delay(50);
}

long getSerial()
{
  serialData = 0;
  if (Serial.available() > 0)
  {
    while (inByte != '/')
    {
      inByte = Serial.read();
      if (inByte > 0 && inByte != '/')
      {
        serialData = serialData * 10 + inByte - '0';
        //Serial.println(serialData);
      }
    }
    inByte = 0;
  }
  return serialData;
}

void PrintCarData()
{
  Serial.println("CAR_DATA");
  Serial.print("SPEED: ");
  if (turning == DISABLED)
    Serial.println(normalSpeed);
  else
    Serial.println(directionSpeed);
  Serial.print("ACTION: ");
  Serial.println(action);
  Serial.println("END_CAR_DATA");
  Serial.println("");
}

void updateVectorSpeed()
{
  for (int i = 0; i < MOTORS_NR; i++)
  {
    motorSpeedValue[i] = normalSpeed;
  }
}

void CommandManager()
{
  getSerial();
  switch (serialData)
  {
    case 1: // speed up
      {
        getSerial();
        switch(serialData)
        {
          case 1:
          // mergi inainte (fara increase)
          {
            directionSpeed = normalSpeed;
            turning = DISABLED;
            action = "FRONT";
            updateVectorSpeed();
            break;
          }
          case 2:
          // mergi inainte cu increase
          {
            if(turning == DISABLED)
            {
              if (normalSpeed < MIN_TRESHOLD)
                normalSpeed = MIN_SPEED;
              else if (normalSpeed < MAX_TRESHOLD)
                normalSpeed += SPEED_UNIT;
            }
            directionSpeed = normalSpeed;
            turning = DISABLED;
            action = "SPEED_UP";
    
            updateVectorSpeed();
            break;
          }
        }
        break;
        
       /*turning = DISABLED;
        if (action != "LEFT" && action != "RIGHT")
        {
          if (normalSpeed < MIN_TRESHOLD)
            normalSpeed = MIN_SPEED;
          else if (normalSpeed < MAX_TRESHOLD)
            normalSpeed += SPEED_UNIT;
        }

        directionSpeed = normalSpeed;
        action = "SPEED_UP";

        updateVectorSpeed();
        break;*/
      }
      case 2: // speed down
      {
        if (turning == DISABLED)
        {
          if (normalSpeed > MIN_TRESHOLD)
            normalSpeed -= SPEED_UNIT;
          else
            normalSpeed = 0;
        }
        else
        {
          if (directionSpeed > MIN_TRESHOLD)
            directionSpeed -= SPEED_UNIT;
          else
            directionSpeed = 0;
        }

        if(turning == TURNING_LEFT)
        {
          motorSpeedValue[RIGHT_FRONT] = directionSpeed;
          motorSpeedValue[RIGHT_BACK] = directionSpeed;
        }
        else if(turning == TURNING_RIGHT)
        {
          motorSpeedValue[LEFT_FRONT] = directionSpeed;
          motorSpeedValue[LEFT_BACK] = directionSpeed;
        }
        else
        {
          updateVectorSpeed();
        }
        
        action = "SPEED_DOWN";

        break;
      }
    case 3: // brake
      {
        turning = DISABLED;
        action = "BRAKE";
        normalSpeed = 0;
        GoBackWard = false;
        for (int i = 0; i < MOTORS_NR; i++)
        {
          motorSpeedValue[i] = normalSpeed;
        }
        directionSpeed = normalSpeed;
        break;
      }
    case 4: // turn left
      {
        turning = TURNING_LEFT;
        motorSpeedValue[LEFT_FRONT] = 0;
        motorSpeedValue[LEFT_BACK] = 0;

        if (action != "SPEED_UP" && action != "SPEED_DOWN" && action != "RIGHT")
        {
          if (directionSpeed < MIN_TRESHOLD)
          {
            directionSpeed = MIN_SPEED;
          }
          else if (directionSpeed < MAX_TRESHOLD)
          {
            directionSpeed += SPEED_UNIT;
          }
          else
          {
            directionSpeed = MAX_SPEED;
          }
        }
        
        action = "LEFT";
        
        motorSpeedValue[RIGHT_FRONT] = directionSpeed;
        motorSpeedValue[RIGHT_BACK] = directionSpeed;

        break;
      }
    case 5: // turn right
      {
        turning = TURNING_RIGHT;
        motorSpeedValue[RIGHT_FRONT] = 0;
        motorSpeedValue[RIGHT_BACK] = 0;

        if (action != "SPEED_UP" && action != "SPEED_DOWN" && action != "LEFT")
        {
          if (directionSpeed < MIN_TRESHOLD)
          {
            directionSpeed = MIN_SPEED;
          }
          else if (directionSpeed < MAX_TRESHOLD)
          {
            directionSpeed += SPEED_UNIT;
          }
          else
          {
            directionSpeed = MAX_SPEED;
          }
        }

        action = "RIGHT";

        motorSpeedValue[LEFT_FRONT] = directionSpeed;
        motorSpeedValue[LEFT_BACK] = directionSpeed;

        break;
      }
    case 6: // go back
      {
        turning = DISABLED;
        action = "REAR";
        if (normalSpeed < MIN_TRESHOLD)
        {
          normalSpeed = MIN_SPEED;
        }
        GoBackWard = true;
        for (int i = 0; i < MOTORS_NR; i++)
        {
          motorSpeedValue[i] = normalSpeed;
        }
      }
  }
  Serial.flush();
}
