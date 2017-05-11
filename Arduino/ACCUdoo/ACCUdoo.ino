#define MAX_SPEED                 255
#define MIN_SPEED                 120
#define MAX_TRESHOLD              250
#define MIN_TRESHOLD              120
#define SPEED_UNIT                10

const int MOTORS_IN1 =            7;
const int MOTORS_IN2 =            6;
const int MOTORS_IN3 =            4;
const int MOTORS_IN4 =            2;

// motors indices in vector of speeds
#define LEFT_FRONT                0
#define RIGHT_FRONT               1
#define LEFT_BACK                 2
#define RIGHT_BACK                3

#define TURNING_LEFT              2
#define TURNING_RIGHT             1
#define DISABLED                  0

#define MOTORS_NR                 4

const int RightFrontMotorPin  =   11;
const int LeftFrontMotorPin   =   10;
const int RightBackMotorPin   =   5;
const int LeftBackMotorPin    =   3;

int normalSpeed = 0;
int directionSpeed = 0;
int turning;

int motorSpeedValue[MOTORS_NR] = {0, 0, 0, 0};
bool GoBackWard[MOTORS_NR] = {false, false, false, false};

unsigned long print_timer = 0;

unsigned long serialData;
int inByte;
String action;

void setup()
{
  pinMode (MOTORS_IN1,          OUTPUT);
  pinMode (MOTORS_IN2,          OUTPUT);
  pinMode (MOTORS_IN3,          OUTPUT);
  pinMode (MOTORS_IN4,          OUTPUT);

  pinMode (RightBackMotorPin,   OUTPUT);
  pinMode (LeftBackMotorPin,    OUTPUT);
  pinMode (RightFrontMotorPin,  OUTPUT);
  pinMode (LeftFrontMotorPin,   OUTPUT);

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

  analogWrite(RightBackMotorPin,    motorSpeedValue[RIGHT_BACK]);
  analogWrite(LeftBackMotorPin,     motorSpeedValue[LEFT_BACK]);
  analogWrite(RightFrontMotorPin,   motorSpeedValue[RIGHT_FRONT]);
  analogWrite(LeftFrontMotorPin,    motorSpeedValue[LEFT_FRONT]);

  if (GoBackWard[0] == false)
  {
    digitalWrite(MOTORS_IN1, HIGH);
    digitalWrite(MOTORS_IN2, LOW);
  }
  else
  {
    digitalWrite(MOTORS_IN1, LOW);
    digitalWrite(MOTORS_IN2, HIGH);
  }

  if (GoBackWard[1] == false)
  {
    digitalWrite(MOTORS_IN3, HIGH);
    digitalWrite(MOTORS_IN4, LOW);
  }
  else
  {
    digitalWrite(MOTORS_IN3, LOW);
    digitalWrite(MOTORS_IN4, HIGH);
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
       turning = DISABLED;
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

            updateVectorSpeed();
        }
        else
        {
          if (directionSpeed > MIN_TRESHOLD)
            directionSpeed -= SPEED_UNIT;
          else
            directionSpeed = 0;
        }

        if(turning = TURNING_LEFT)
        {
          motorSpeedValue[RIGHT_FRONT] = directionSpeed;
          motorSpeedValue[RIGHT_BACK] = directionSpeed;
        }
        else
        {
          motorSpeedValue[LEFT_FRONT] = directionSpeed;
          motorSpeedValue[LEFT_BACK] = directionSpeed;
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
        for (int i = 0; i < MOTORS_NR; i++)
        {
          motorSpeedValue[i] = normalSpeed;
          GoBackWard[i] = true;
        }
      }
  }
  Serial.flush();
}
