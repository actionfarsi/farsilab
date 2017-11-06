Lab Script.md

Figuring out a way to generalize and reuse as much as possible snipets of codes
Problem I'd like to solve

Quickly modifying option without delving in the source file
Standard Way to save the data
Fast graphical response for long measurement


The idea is to save the function on a script, that accepts
traits-like options
has a display callback
returns the acquire data


So the script can be either run by itself wrapping it around an appropriate __main__ function or called as a module


