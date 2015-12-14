run:
	-pkill asebamedulla
	-asebamedulla "ser:device=/dev/ttyACM0" &
	-DISPLAY=localhost:10.0 python run.py
	-pkill asebamedulla
color:
	-pkill asebamedulla
	-asebamedulla "ser:device=/dev/ttyACM0" &
	-DISPLAY=localhost:10.0 python colors.py
	-pkill asebamedulla
xvfb:
	-pkill Xvfb 
	-Xvfb :0 -screen 0 800x600x16 &
