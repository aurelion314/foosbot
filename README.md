# foosbot
track wins and loses with elo based ranking

# Pi Setup
As described on https://blog.eq8.eu/til/raspberi-pi-as-kiosk-load-browser-on-startup-fullscreen.html
1. sudo raspi-config
2. Boot Options -> B1. Descktop / CLI -> B4 Desktop Autologin
3. sudo apt install midori
4. sudo nano /etc/xdg/lxsession/LXDE/autostart OR ~/.config/lxsession/LXDE-pi/autostart
    # Auto run the browser
    @xset s off
    @xset -dpms
    @xset s noblank
    @midori -e Fullscreen -a http://aurelion.pythonanywhere.com/100/hash/12345
5. sudo shutdown -r now

# Pi SSH
1. connect pi to local network with ethernet
2. sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
3. ssh pi@<Pi IP>
4. pass: raspberry