Byregot-Bot
===========

Basically an attempt to use q-learning to solve FFXIV crafting. Super shitty right now because I don't have access to a GPU so I'm just running the neural network learning on a crappy laptop and getting "only use Careful Synthesis" LUL

Todo
----
* Condition should probably be a one-hot
* Training should use more default values
* Better regularization of parameters? I'll probably get some advice for this one
* Change negative rewards to more reasonable values; failure to craft is better than invalid choice
* Add more actions (currently only actions available at 1-35)

