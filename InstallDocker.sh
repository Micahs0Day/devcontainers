#!/bin/bash

#Update the installed packages and package cache on your instance.
sudo yum update -y
#Install the most recent Docker Community Edition package.
sudo yum install docker -y
#Start the Docker service.
sudo service docker start
#Start the service docker at boot
sudo systemctl enable docker
#Add the ec2-user to the docker group so you can execute Docker commands without using sudo.
sudo usermod -a -G docker ec2-user