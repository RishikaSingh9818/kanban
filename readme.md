## Steps to run :-

1. Create a virtual environment using `python -m venv .venv`.
2. Navigate inside the virtual environment.
3. Activate the virtual environment `.\Scripts\activate`
4. Install the packages required using `pip install -r requirements.txt`
5. After all the packages are installed, its time to finally run the app.
6. Run the app using `python main.py`
7. Go inside project directory using `cd project`
8. Run using command `npm run server`
9. Open ubuntu terminal1 and cd to project and run `sudo service redis-server start` to start redis server on windows
10. Then run command `~/go/bin/MailHog` to start mailhog server
11. Open ubuntu terminal and run command `celery -A main.celery beat --max-interval 1 -l info` to start beat in windows
12. Open ubuntu terminal and run command `celery -A main.celery worker -l info` to start worker in ubuntu
13. To open mailhog, run the mailhog server on the ip address which you can get by running command `ip addr` on port 8025
 # kanban
