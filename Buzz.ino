#define M1 OCR1AL
#define M2 OCR1BL
#define M3 OCR2A
#define MAX_INPUT 15

void setup() 
{
    DDRB=0x0E; // PWM pins as output
    
    // using timer 1 ,2 for pwm on pins OCR1A ,OCR1B ,OCR2A to control the vibrating motors 
    // setting the timers for 8-bit pwm 
    //timer1 OCR1A ,OCR1B
    // non-inverting , pre-sc=8 -> 7.8kHz
    TCCR1A=(1<<COM1A1)|(1<<COM1B1)|(1<<WGM10);
    TCCR1B=(1<<WGM12)|(1<<CS11);
    OCR1AL=0x00;
    OCR1AH=0x00;
    OCR1BL=0x00;
    OCR1BH=0x00;
  
    //timer 2 OCR2A
    // non-inverting , pre-sc=8 -> 7.8kHz
    TCCR2A=(1<<COM1A1)|(1<<WGM10)|(1<<WGM11);
    TCCR2B=(1<<CS21);
    OCR2A=0x00;
    OCR2B=0x00;
  
    Serial.begin(115200);

}

void process_data (const char * data)
{
    sscanf(data,"%d %d %d",&M1,&M2,&M3);
    //Serial.println(M1,DEC);
    //Serial.println(M2,DEC);
    //Serial.println(M3,DEC);
}  

void processIncomingByte (const byte inByte)
{
    static char input_line [MAX_INPUT];
    static unsigned int input_pos = 0;
  
    switch (inByte)
    {
  
      case '\n':   // end of text
          input_line [input_pos] = 0;  
          // terminating null byte
          // terminator reached! process input_line here ...
          process_data (input_line);
  
          // reset buffer for next time
          input_pos = 0;  
          break;

      case '\r':   
          // discard carriage return
          break;

      default:
          // keep adding if not full ... allow for terminating null byte
          if (input_pos < (MAX_INPUT - 1))
              input_line [input_pos++] = inByte;
          break;
      
    }  
} 

void loop() 
{
    while (Serial.available () > 0)
        processIncomingByte(Serial.read ()); 
}
