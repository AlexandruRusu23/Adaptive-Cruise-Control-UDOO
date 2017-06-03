#include <AFMotor.h>

#define RIGHT_BACK_MOTOR          0
#define LEFT_BACK_MOTOR           1
#define LEFT_FRONT_MOTOR          2
#define RIGHT_FRONT_MOTOR         3

#define MAX_SPEED                 255
#define MIN_SPEED                 100
#define MAX_TRESHOLD              250
#define MIN_TRESHOLD              100
#define SPEED_UNIT                10

#define TURNING_LEFT              2
#define TURNING_RIGHT             1
#define DISABLED                  0

const int MOTORS_IN1 =            7;
const int MOTORS_IN2 =            6;
const int MOTORS_IN3 =            4;
const int MOTORS_IN4 =            2;

#define MOTORS_NR                 4

AF_DCMotor rightBackMotor(2); 
AF_DCMotor leftBackMotor(1);
AF_DCMotor leftFrontMotor(4);
AF_DCMotor rightFrontMotor(3);

int motorSpeedValue[4] = {0, 0, 0, 0};
bool GoBackWard[4] = {false, false, false, false};

int normalSpeed = 0;
int directionSpeed = 0;
String action;
int turning;

unsigned long print_timer = 0;

unsigned long serialData;
int inByte;

void setup() {
  Serial.begin(9600);
}
 
void loop() {
  CommandManager();

  if (millis() - print_timer > 500)
  {
    PrintCarData();
    print_timer = millis();
  }
  
  //right - back motor
  rightBackMotor.setSpeed(motorSpeedValue[RIGHT_BACK_MOTOR]);
  if (!GoBackWard[RIGHT_BACK_MOTOR])
    rightBackMotor.run(FORWARD);
   else
    rightBackMotor.run(BACKWARD);
  //left - back motor
  leftBackMotor.setSpeed(motorSpeedValue[LEFT_BACK_MOTOR]);
  if (!GoBackWard[LEFT_BACK_MOTOR]) 
    leftBackMotor.run(FORWARD);
  else
    leftBackMotor.run(BACKWARD);
  //left - front motor
  leftFrontMotor.setSpeed(motorSpeedValue[LEFT_FRONT_MOTOR]);
  if (!GoBackWard[LEFT_FRONT_MOTOR]) 
    leftFrontMotor.run(FORWARD);
  else
    leftFrontMotor.run(BACKWARD);
  //rigth - front motor
  rightFrontMotor.setSpeed(motorSpeedValue[RIGHT_FRONT_MOTOR]);
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

void PrintCarData()
{
  Serial.flush();
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
        
        /*if(turning == DISABLED)
        {
          if (normalSpeed < MIN_TRESHOLD)
            normalSpeed = MIN_SPEED;
          else if (normalSpeed < MAX_TRESHOLD)
            normalSpeed += SPEED_UNIT;
        }

        directionSpeed = normalSpeed;
        turning = DISABLED;
        action = "SPEED_UP";

        updateVectorSpeed();*/
        break;
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
          motorSpeedValue[RIGHT_FRONT_MOTOR] = directionSpeed;
          motorSpeedValue[RIGHT_BACK_MOTOR] = directionSpeed;
        }
        else if(turning == TURNING_RIGHT)
        {
          motorSpeedValue[LEFT_FRONT_MOTOR] = directionSpeed;
          motorSpeedValue[LEFT_BACK_MOTOR] = directionSpeed;
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
        for (int i = 0; i < MOTORS_NR; i++)
        {
          GoBackWard[i] = false;
          motorSpeedValue[i] = normalSpeed;
        }
        directionSpeed = normalSpeed;
        break;
      }
    case 4: // turn left
      {
        turning = TURNING_LEFT;
        motorSpeedValue[LEFT_FRONT_MOTOR] = 0;
        motorSpeedValue[LEFT_BACK_MOTOR] = 0;

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
        
        motorSpeedValue[RIGHT_FRONT_MOTOR] = directionSpeed;
        motorSpeedValue[RIGHT_BACK_MOTOR] = directionSpeed;

        break;
      }
    case 5: // turn right
      {
        turning = TURNING_RIGHT;
        motorSpeedValue[RIGHT_FRONT_MOTOR] = 0;
        motorSpeedValue[RIGHT_BACK_MOTOR] = 0;

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

        motorSpeedValue[LEFT_FRONT_MOTOR] = directionSpeed;
        motorSpeedValue[LEFT_BACK_MOTOR] = directionSpeed;

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
        for (int i = 0; i < MOTORS_NR; i++)
        {
          motorSpeedValue[i] = normalSpeed;
          GoBackWard[i] = true;
        }
      }
  }
  Serial.flush();
}
