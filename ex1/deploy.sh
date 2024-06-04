sudo yum -y install python-pip
sudo yum install python3

mkdir parking_lot
cd parking_lot
git clone https://github.com/guyfarhi11/cloud_computing_course.git
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

nohup sudo env "PATH=$PATH" python3 app.py
