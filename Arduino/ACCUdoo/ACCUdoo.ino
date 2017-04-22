const int IN1 = 7;
const int IN2 = 6;
const int IN3 = 5;
const int IN4 = 4;

#define LEFT_SIDE 1
#define RIGHT_SIDE 0

const int RightSideMotors = 9;
const int LeftSideMotors = 3;

int motorSpeedValue[2] = {0, 0};
bool GoBackWard[2] = {false, false};

unsigned long serialData;
int inByte;

void setup()
{
  pinMode (IN1, OUTPUT);
  pinMode (IN2, OUTPUT);
  pinMode (IN3, OUTPUT);
  pinMode (IN4, OUTPUT);
  pinMode (RightSideMotors, OUTPUT);
  pinMode (LeftSideMotors, OUTPUT);
  Serial.begin(115200);
}

void loop()
{
  CommandManager();
  //right - back motor

  analogWrite(RightSideMotors, motorSpeedValue[RIGHT_SIDE]); // dreapta
  analogWrite(LeftSideMotors, motorSpeedValue[LEFT_SIDE]);

  if (GoBackWard[0] == false)
  {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  }
  else
  {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }

  if (GoBackWard[1] == false)
  {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }
  else
  {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
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
      for(int i = 0; i<2; i++)
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
      for(int i = 0; i<2; i++)
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
      for(int i = 0; i<2; i++)
      {
        GoBackWard[i] = false;
      }
      for(int i = 0; i<2; i++)
      {
        motorSpeedValue[i] = 0;
      }
      break;
    }
    case 4: // turn left
    {  
      if (motorSpeedValue[LEFT_SIDE] > 70)
      {
        motorSpeedValue[LEFT_SIDE] -= 10;
      }
      else
      {
        motorSpeedValue[LEFT_SIDE] = 70;
      }

      if (motorSpeedValue[RIGHT_SIDE] < 70)
      {
        motorSpeedValue[RIGHT_SIDE] = 70;
      }
      else if (motorSpeedValue[RIGHT_SIDE] < 250)
      {
        motorSpeedValue[RIGHT_SIDE] += 10;
      }
      else
      {
        motorSpeedValue[RIGHT_SIDE] = 255;
      }
      break;
    }
    case 5: // turn right
    {
      if (motorSpeedValue[RIGHT_SIDE] > 70)
      {
        motorSpeedValue[RIGHT_SIDE] -= 10;
      }
      else
      {
        motorSpeedValue[RIGHT_SIDE] = 70;
      }

      if (motorSpeedValue[LEFT_SIDE] < 70)
      {
        motorSpeedValue[LEFT_SIDE] = 70;
      }
      else if (motorSpeedValue[LEFT_SIDE] < 250)
      {
        motorSpeedValue[LEFT_SIDE] += 10;
      }
      else
      {
        motorSpeedValue[LEFT_SIDE] = 255;
      }
      break;
    }
    case 6: // go back
    {
      for(int i = 0; i<2; i++)
      {
        if(motorSpeedValue[i] < 100)
          motorSpeedValue[i] = 100;
        GoBackWard[i] = true;
      }
    }
  }
  Serial.flush();
}
