const int LEFT_BACK_IN1 = 7;
const int LEFT_BACK_IN2 = 6;
const int RIGHT_BACK_IN3 = 4;
const int RIGHT_BACK_IN4 = 2;

// motors indices in vector of speeds
#define LEFT_FRONT_MOTOR 0
#define RIGHT_FRONT_MOTOR 1
#define LEFT_BACK_MOTOR 2
#define RIGHT_BACK_MOTOR 3

const int RightFrontMotorPin = 11;
const int LeftFrontMotorPin = 10;
const int RightBackMotorPin = 5;
const int LeftBackMotorPin = 3;

int motorSpeedValue[4] = {0, 0, 0, 0};
bool GoBackWard[4] = {false, false, false, false};

unsigned long serialData;
int inByte;

void setup()
{
  pinMode (LEFT_BACK_IN1, OUTPUT);
  pinMode (LEFT_BACK_IN2, OUTPUT);
  pinMode (RIGHT_BACK_IN3, OUTPUT);
  pinMode (RIGHT_BACK_IN4, OUTPUT);
  
  pinMode (RightBackMotorPin, OUTPUT);
  pinMode (LeftBackMotorPin, OUTPUT);
  pinMode (RightFrontMotorPin, OUTPUT);
  pinMode (LeftFrontMotorPin, OUTPUT);

  Serial.begin(115200);
}

void loop()
{
  CommandManager();

  analogWrite(RightBackMotorPin, motorSpeedValue[RIGHT_BACK_MOTOR]);
  analogWrite(LeftBackMotorPin, motorSpeedValue[LEFT_BACK_MOTOR]);
  analogWrite(RightFrontMotorPin, motorSpeedValue[RIGHT_FRONT_MOTOR]);
  analogWrite(LeftFrontMotorPin, motorSpeedValue[LEFT_FRONT_MOTOR]);

  if (GoBackWard[0] == false)
  {
    digitalWrite(LEFT_BACK_IN1, HIGH);
    digitalWrite(LEFT_BACK_IN2, LOW);
  }
  else
  {
    digitalWrite(LEFT_BACK_IN1, LOW);
    digitalWrite(LEFT_BACK_IN2, HIGH);
  }

  if (GoBackWard[1] == false)
  {
    digitalWrite(RIGHT_BACK_IN3, HIGH);
    digitalWrite(RIGHT_BACK_IN4, LOW);
  }
  else
  {
    digitalWrite(RIGHT_BACK_IN3, LOW);
    digitalWrite(RIGHT_BACK_IN4, HIGH);
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
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 100)
          motorSpeedValue[i] = 100;
        else if (motorSpeedValue[i] < 250)
          motorSpeedValue[i] += 10;
      }
      break;
    }
    case 2: // speed down
    {
      for(int i = 0; i<4; i++)
      {
        if (motorSpeedValue[i] > 100)
          motorSpeedValue[i] -= 10;
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
    case 4: // turn left
    {
      motorSpeedValue[LEFT_FRONT_MOTOR] = 0;
      motorSpeedValue[LEFT_BACK_MOTOR] = 0;
      
      if (motorSpeedValue[RIGHT_FRONT_MOTOR] < 100)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] = 100;
        motorSpeedValue[RIGHT_BACK_MOTOR] = 100;
      }
      else if (motorSpeedValue[RIGHT_FRONT_MOTOR] < 250)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] += 10;
        motorSpeedValue[RIGHT_BACK_MOTOR] += 10;
      }
      else
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] = 255;
        motorSpeedValue[RIGHT_BACK_MOTOR] = 255;
      }
      break;
    }
    case 5: // turn right
    {
      motorSpeedValue[RIGHT_FRONT_MOTOR] = 0;
      motorSpeedValue[RIGHT_BACK_MOTOR] = 0;
      
      if (motorSpeedValue[LEFT_FRONT_MOTOR] < 100)
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] = 100;
        motorSpeedValue[LEFT_BACK_MOTOR] = 100;
      }
      else if (motorSpeedValue[LEFT_FRONT_MOTOR] < 250)
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] += 10;
        motorSpeedValue[LEFT_BACK_MOTOR] += 10;
      }
      else
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] = 255;
        motorSpeedValue[LEFT_BACK_MOTOR] = 255;
      }
      break;
    }
    case 6: // go back
    {
      for(int i = 0; i<4; i++)
      {
        if(motorSpeedValue[i] < 100)
          motorSpeedValue[i] = 100;
        GoBackWard[i] = true;
      }
    }
  }
    Serial.flush();
}
