# Keyboard Case and Plate STL Generator With Automatic Model Segmentation

This is meant to generate a scad and or stl file from a [keyboard-layout-editor](http://www.keyboard-layout-editor.com/) layout file. 

Additionally the model can be automatically segmented so that the parts will fit within the build area of your 3d printer


## How it Works

The program takes a keyboard-layout-editor json file as one of the inputs along with an optional parameter json file to customize other parts of the resulting model

The program can then genarate a number of different items. The entire case can be generated as a single model or the case can be broken up so that parts will fit within the build size of your 3d printer. The build size is one of the values that can be places in the optional parameters file.

Here is an examle of the program sli usage

![keyboard_stl_generator.py usage](/images/usage.png)


Shout out to Will Stevens https://github.com/swill for his plate generator that provided inspiration and very useful measurements. The swillkb plate and case generator is here http://builder.swillkb.com/
