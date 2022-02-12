# Keyboard Case and Plate STL Generator With Automatic Model Segmentation

This is meant to generate a scad and or stl file from a [keyboard-layout-editor](http://www.keyboard-layout-editor.com/) layout file. 

Additionally the model can be automatically segmented so that the parts will fit within the build area of your 3d printer


## How it Works

The program takes a keyboard-layout-editor json file as one of the inputs along with an optional parameter json file to customize other parts of the resulting model

The program can then genarate a number of different items. The entire case can be generated as a single model or the case can be broken up so that parts will fit within the build size of your 3d printer. The build size is one of the values that can be places in the optional parameters file.

Here is an examle of the program cli usage

![keyboard_stl_generator.py usage](/images/usage.png)


## Example

This shows testing done using a msall layout and changing the printer build plate settings to force it to split the design up.

This is an image of the layout design on keyboard-layout-editor

![small_test_layout.png](/images/small_test_layout/small_test_layout.png)


if just passing in the layput fle with the "-i" option the entire case will be generated. An example of the top of the case of that model is shown bellow

![small_test.png](/images/small_test_layout/small_test.png)


using the "-a" option it will generate files for 2 different models that make up the entire layout. The images bellow show the separate section top case models

![small_test_top_0.png](/images/small_test_layout/small_test_top_0.png)

![small_test_top_1.png](/images/small_test_layout/small_test_top_1.png)


using the "-e" file will generate an exploded view of the case where all the sections are shown but they are offset to be viewed more easily. See the iamge bellow

![small_test_top_exploded.png](/images/small_test_layout/small_test_top_exploded.png)




## Printed Part

Here are some pictures of that raw parts from the printer and the assembled case

Topside of Top
![top_topside.jpg](/images/small_test_layout/top_topside.jpg)

Underside of Top
![top_underside.jpg](/images/small_test_layout/top_underside.jpg)

Top edge on view
![top_edge.jpg](/images/small_test_layout/top_edge.jpg)

Focus on stabilizer cutout
![top_stab_cutout.jpg](/images/small_test_layout/top_stab_cutout.jpg)

Bottom
![bottom.jpg](/images/small_test_layout/bottom.jpg)

Bottom edge on view
![bottom_edge.jpg](/images/small_test_layout/bottom_edge.jpg)

Assembeled Front
![assembled_front.jpg](/images/small_test_layout/assembled_front.jpg)

Assembeled Side
![assembled_side.jpg](/images/small_test_layout/assembled_side.jpg)

Assembeled Tilt 
![assembled_tile.jpg](/images/small_test_layout/assembled_tilt.jpg)





Shout out to Will Stevens https://github.com/swill for his plate generator that provided inspiration and very useful measurements. The swillkb plate and case generator is here http://builder.swillkb.com/
