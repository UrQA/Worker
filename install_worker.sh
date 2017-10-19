sudo git clone https://github.com/UrQA/Worker.git
sudo mkdir poolfromdjango
sudo mkdir poolfromdjango/sopool
sudo mkdir poolfromdjango/sympool
sudo mkdir poolfromdjango/mappool
sudo mkdir poolfromworker
sudo mkdir poolfromworker/logpool
sudo mkdir poolfromworker/dmppool
sudo echo "you should set rsync"
sudo apt-get install python-pip
sudo apt-get --fix-missing  install openjdk-7-jre
sudo apt-get install python-jpype
sudo apt-get install python-sqlalchemy
sudo pip install pika
sudo pip install pytz
sudo apt-get install redis-server
sudo apt-get install python-redis
sudo /etc/init.d/redis-server restart
sudo apt-get install python-mysqldb
