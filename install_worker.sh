git clone https://github.com/UrQA/Worker.git
mkdir poolfromdjango
mkdir poolfromdjango/sopool
mkdir poolfromdjango/sympool
mkdir poolfromdjango/mappool
mkdir poolfromworker
mkdir poolfromworker/logpool
mkdir poolfromworker/dmppool
echo "you should set rsync"
apt-get install python-pip
sudo apt-get --fix-missing  install openjdk-7-jre
sudo apt-get install python-jpype
sudo apt-get install python-sqlalchemy
sudo pip install pika
sudo pip install pytz
sudo apt-get install redis-server
sudo apt-get install python-redis
sudo /etc/init.d/redis-server restart
apt-get install python-mysqldb
