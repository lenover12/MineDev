#instructions for running on local host

#command line in the root folder

#set up virtual environment fir the first Time
python -m venv venv

#activate virtual environment
venv\Scripts\activate

#install requirements
pip install -r requirements.txt

#run application
python application.py
#it will tell you what website it is running on

#deactivate virtual environment
deactivate