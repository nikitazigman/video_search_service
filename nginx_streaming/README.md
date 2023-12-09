Article: https://www.nginx.com/blog/video-streaming-for-remote-learning-with-nginx/

Installing 

sudo apt update
sudo apt install build-essential git
sudo apt install libpcre3-dev libssl-dev zlib1g-dev

cd /path/to/build/dir
git clone https://github.com/arut/nginx-rtmp-module.git
git clone https://github.com/nginx/nginx.git
cd nginx
./auto/configure --add-module=../nginx-rtmp-module
make
sudo make install