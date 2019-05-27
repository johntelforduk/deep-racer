# deep-racer
Car at start of training,
![Start of training](https://github.com/johntelforduk/deep-racer/blob/master/deepracer-start-of-training.gif)


Car at end of training,
![Start of training](https://github.com/johntelforduk/deep-racer/blob/master/deepracer-end-of-training.gif)


For information about AWS DeepRacer see,

https://aws.amazon.com/blogs/aws/the-aws-deepracer-league-virtual-circuit-is-now-open-train-your-model-today/

This project has two main features,
* A visualisation of DeepRacer model training.
* An easy to read reward function.
#### Installation
Install the following packages,
~~~
pip install pygame
pip install imageio
~~~
#### Running
To see a graphical animation of the car going round the track,
~~~
python animate.py
~~~
#### Visualisation
This works by adding logging to the reward function. Status information is sent to stdout. This produces AWS CloudWatch Logs. The logs may be exported to AWS S3, and from there downloaded to the user's desktop PC. This repo includes `truncated_simulation_log.txt` which contains about 1 minute of training logs.
#### Reward Function
The aim is to be able to code rules in a fairly readable way, like (in pseudocode) "If going fast, and in right direction, and down middle of road, and steering pointing straight, then give a big reward".
The is done by working out booleans in advance of testing which rules apply. Booleans such as, `near_centre_of_track` and `going_fast`. This avoids having to write reward rules that have a lot of maths in them.

The reward function then tests reward rules in ascending level. Finally it (potentially) overrides the reward with any penalty that applies, for example if the car has wheels off the track.