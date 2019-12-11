# foosbot
track wins and loses with elo based ranking

# Pi Setup
As described on https://blog.eq8.eu/til/raspberi-pi-as-kiosk-load-browser-on-startup-fullscreen.html
1. sudo raspi-config
2. Boot Options -> B1. Descktop / CLI -> B4 Desktop Autologin
3. ~/kiosk.sh needs stuff. --start-fullscreen
#!/bin/bash
xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --start-fullscreen https://www.employeearcade.com/token?token=test

while true; do
   sleep 10
done

4. Make a service sudo nano /lib/systemd/system/kiosk.service
[Unit]
Description=Chromium Kiosk
Wants=graphical.target
After=graphical.target

[Service]
Environment=DISPLAY=:0.0
Environment=XAUTHORITY=/home/pi/.Xauthority
Type=simple
ExecStart=/bin/bash /home/pi/kiosk.sh
Restart=on-abort
User=pi
Group=pi

[Install]
WantedBy=graphical.target

then 
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service



# Pi SSH
1. connect pi to local network with ethernet
2. sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
3. ssh pi@<Pi IP>
4. pass: arcade

# Pi Clone
1. sudo fdisk -l
2. (without gzip) sudo ionice -c3 dd bs=4M of=/dev/sdc if=~/pi_template.img
    2. (with gzip) sudo gzip -dc ~/pi_template.gz | dd bs=4M of=/dev/sdc 
3. Set the account token (ask Mike how)
4. If reinstall required, follow https://pimylifeup.com/raspberry-pi-kiosk/
5. To create a new backup img, use sudo dd bs=4M if=/dev/sdc | gzip > ~/pi_img_em.gz
    -or instead of gzip, just use of=~/pi.img