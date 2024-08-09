#!/bin/sh

windog_start(){
	rm -f ./.WinDog.Restart.lock
	python3 ./WinDog.py &
}

cd "$( dirname "$( realpath "$0" )" )"
windog_start

while true
do
	if [ -f ./.WinDog.Restart.lock ]
	then
		kill "$!"
		windog_start
	fi
	sleep 5
done