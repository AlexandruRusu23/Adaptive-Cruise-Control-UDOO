#define MAX_SPEED                 255
#define MIN_SPEED                 100
#define MAX_TRESHOLD              250
#define MIN_TRESHOLD              100
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

#define MOTORS_NR                 4

const int RightFrontMotorPin  =   11;
const int LeftFrontMotorPin   =   10;
const int RightBackMotorPin   =   5;
const int LeftBackMotorPin    =   3;

int motorSpeedValue[MOTORS_NR] = {0, 0, 0, 0};
bool GoBackWard[MOTORS_NR] = {false, false, false, false};

unsigned long serialData;
int inByte;

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
    while(inByte != '/')
    {
      inByte = Serial.read();
      if(inByte > 0 && inByte != '/')
      {
        serialData = serialData * 10 + inByte - '0';
        //Serial.println(serialData);
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
      int maxim = motorSpeedValue[0];
      for(int i = 0; i<MOTORS_NR; i++)
        if (maxim < motorSpeedValue[i])
          maxim = motorSpeedValue[i];

      for(int i = 0; i<MOTORS_NR; i++)
      {
        motorSpeedValue[i] = maxim;
        if(motorSpeedValue[i] < MIN_TRESHOLD)
          motorSpeedValue[i] = MIN_SPEED;
        else if (motorSpeedValue[i] < MAX_TRESHOLD)
          motorSpeedValue[i] += SPEED_UNIT;
      }
      break;
    }
    case 2: // speed down
    {
      for(int i = 0; i<MOTORS_NR; i++)
      {
        if (motorSpeedValue[i] > MIN_TRESHOLD)
          motorSpeedValue[i] -= SPEED_UNIT;
        else
          motorSpeedValue[i] = 0;
      }
      break;
    }
    case 3: // brake
    {
      for(int i = 0; i<MOTORS_NR; i++)
      {
        GoBackWard[i] = false;
        motorSpeedValue[i] = 0;
      }
      break;
    }
    case 4: // turn left
    {
      motorSpeedValue[LEFT_FRONT] = 0;
      motorSpeedValue[LEFT_BACK] = 0;
      
      if (motorSpeedValue[RIGHT_FRONT] < MIN_TRESHOLD)
      {
        motorSpeedValue[RIGHT_FRONT] = MIN_SPEED;
        motorSpeedValue[RIGHT_BACK] = MIN_SPEED;
      }
      else if (motorSpeedValue[RIGHT_FRONT] < MAX_TRESHOLD)
      {
        motorSpeedValue[RIGHT_FRONT] += SPEED_UNIT;
        motorSpeedValue[RIGHT_BACK] += SPEED_UNIT;
      }
      else
      {
        motorSpeedValue[RIGHT_FRONT] = MAX_SPEED;
        motorSpeedValue[RIGHT_BACK] = MAX_SPEED;
      }
      break;
    }
    case 5: // turn right
    {
      motorSpeedValue[RIGHT_FRONT] = 0;
      motorSpeedValue[RIGHT_BACK] = 0;
      
      if (motorSpeedValue[LEFT_FRONT] < MIN_TRESHOLD)
      {
        motorSpeedValue[LEFT_FRONT] = MIN_SPEED;
        motorSpeedValue[LEFT_BACK] = MIN_SPEED;
      }
      else if (motorSpeedValue[LEFT_FRONT] < MAX_TRESHOLD)
      {
        motorSpeedValue[LEFT_FRONT] += SPEED_UNIT;
        motorSpeedValue[LEFT_BACK] += SPEED_UNIT;
      }
      else
      {
        motorSpeedValue[LEFT_FRONT] = MAX_SPEED;
        motorSpeedValue[LEFT_BACK] = MAX_SPEED;
      }
      break;
    }
    case 6: // go back
    {
      for(int i = 0; i<MOTORS_NR; i++)
      {
        if(motorSpeedValue[i] < MIN_TRESHOLD)
          motorSpeedValue[i] = MIN_SPEED;
        GoBackWard[i] = true;
      }
    }
  }
    Serial.flush();
}
