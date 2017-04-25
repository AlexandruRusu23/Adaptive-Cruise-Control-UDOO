const int LEFT_BACK_IN1 = 7;
const int LEFT_BACK_IN2 = 6;
const int RIGHT_BACK_IN3 = 4;
const int RIGHT_BACK_IN4 = 2;

const int LEFT_FRONT_IN1 = 13;
const int LEFT_FRONT_IN2 = 12;
const int RIGHT_FRONT_IN3 = 8;
const int RIGHT_FRONT_IN4 = 10;

// motors indices in vector of speeds
#define LEFT_FRONT_MOTOR 0
#define RIGHT_FRONT_MOTOR 1
#define LEFT_BACK_MOTOR 2
#define RIGHT_BACK_MOTOR 3

const int RightFrontMotorPin = 11;
const int LeftFrontMotorPin = 9;
const int RightBackMotorPin = 3;
const int LeftBackMotorPin = 5;

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

  pinMode (LEFT_FRONT_IN1, OUTPUT);
  pinMode (LEFT_FRONT_IN2, OUTPUT);
  pinMode (RIGHT_FRONT_IN3, OUTPUT);
  pinMode (RIGHT_FRONT_IN4, OUTPUT);

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

  if (GoBackWard[2] == false)
  {
    digitalWrite(LEFT_FRONTIN1, HIGH);
    digitalWrite(LEFT_FRONTIN2, LOW);
  }
  else
  {
    digitalWrite(LEFT_FRONTIN1, LOW);
    digitalWrite(LEFT_FRONTIN2, HIGH);
  }

  if (GoBackWard[3] == false)
  {
    digitalWrite(RIGHT_FRONT_IN3, HIGH);
    digitalWrite(RIGHT_FRONT_IN4, LOW);
  }
  else
  {
    digitalWrite(RIGHT_FRONT_IN3, LOW);
    digitalWrite(RIGHT_FRONT_IN4, HIGH);
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
        if(motorSpeedValue[i] < 50)
          motorSpeedValue[i] = 50;
        else if (motorSpeedValue[i] < 250)
          motorSpeedValue[i] += 10;
      }
      break;
    }
    case 2: // speed down
    {
      for(int i = 0; i<4; i++)
      {
        if (motorSpeedValue[i] > 50)
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
      if (motorSpeedValue[LEFT_FRONT_MOTOR] > 50)
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] -= 10;
        motorSpeedValue[LEFT_BACK_MOTOR] -= 10;
      }
      else
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] = 50;
        motorSpeedValue[LEFT_BACK_MOTOR] = 50;
      }

      if (motorSpeedValue[RIGHT_FRONT_MOTOR] < 50)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] = 50;
        motorSpeedValue[RIGHT_BACK_MOTOR] = 50;
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
      if (motorSpeedValue[RIGHT_FRONT_MOTOR] > 50)
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] -= 10;
        motorSpeedValue[RIGHT_BACK_MOTOR] -= 10;
      }
      else
      {
        motorSpeedValue[RIGHT_FRONT_MOTOR] = 50;
        motorSpeedValue[RIGHT_BACK_MOTOR] = 50;
      }

      if (motorSpeedValue[LEFT_FRONT_MOTOR] < 50)
      {
        motorSpeedValue[LEFT_FRONT_MOTOR] = 50;
        motorSpeedValue[LEFT_BACK_MOTOR] = 50;
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
