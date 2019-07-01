# Greystone Ansible

![Before and After installing heat pump](https://raw.githubusercontent.com/syspimp/greystone-ansible/master/pics/heat-pump-energy-savings.png)

## What is this?

I use Ansible to retrieve my power usage from my electric utility, store the results in a rrd (Round Robin Database) file, and graph the results in my favorite monitoring program, Zenoss 4.

Bonus: I overlay the power produced from my Solar Panels with my Utility Consumption to visualize energy usage and compare my results to their billing.

## Where?

Greystone Power Corporation is located in Cobb/Paulding County, Georgia, USA

## Why did you do it?

I bought a [Carrier Infinity, Seer 18 , 5 stage fan, 2.5 Ton, Heat Pump](https://www.carrier.com/residential/en/us/products/heat-pumps/25vna8/) system and wanted to see how it changed my energy consumption. It's supposed to save money, be super efficient. *Let's verify this claim!*

Baseline: My old system consumed about 1 kwh whenever it ran, verified.

I also have a 2.5 kwh Solar Array, 10x250 watt micro-inverters on 10x300 watt solar panels that are wired on one string into a breaker on the load side of the Main Power Breaker Panel. I graph and monitor the energy production on Zenoss 4, an Open Source, python based, monitoring tool that's compatible with Nagios plugins. When I produce more power than I consume, my meter runs backwards and I supply power to my neighbors and get a credit on my bill. At Georgia's latitude, there are on average 5 usable hours of Sunlight for panels, and I produce on average 12 kwh a day. All within specifications!

My house energy consumption baseline (most everything turned off, but server rack running) is about 550 watts (110 volts by about 5 devices pulling 1 amp)

## When did you do this?

After I noticed my power consumption going down.

Greystone Power shows your energy consumption down to 15 intervals. I already knew my old DC motor 2 ton furnance consumed 1kwh a power when the A/C is running. 2 days after the system was installed, I checked their portal and saw my overall power consumption drop in half!  I had to click back and forth to compare the days, and although the graphs were nice, the scale would change, so I couldn't visually compare the results. For my Solar Panels, there is the Enphase Enlighten portal https://enlighten.enphaseenergy.com where I can see the power produced by my solar panels. It, too, graphed the power down to 15 mins intervals, but it pulled the data from this little gateway device installed in my house. One weekend I made a script to grab this data and graphs it in my monitoring program. They provide an API, but getting the data from the gateway made more sense to me. I figured I could do the same but from my power company.

It took me a few days to get the code working and clean.

## How did you do it?

I turned on developer tools in Chrome (Menu - More Tools - Developer Tools), and then I clicked on the link that shows me the graph of my power consumption for a day. In the Network output, I saw the browser POST'ed form data to an API, and the response was a JSON object, then the browser takes that and renders a graph. All I needed was the JSON object. Sweet. At that point, all I had to do was reverse engineer how it creates an authenticated session. I used the Ansible uri module to handle the process. That took a while ... there were hidden forms and frames, and I had to hit certain url's in a certain order to mimic a user session, but I finished in about 24 hours or so.

I took create care to not hammer the API or the webserver, and in the end it makes about 8 uri calls to create a session, saving the results each time for processing, and then 2 to retrieve a single days results from the API, but you have to retrive each day separately, although it accepts a range in the request (I coded it this way on purpose. 30 requests for 30 days of data is not unreasonable). So, 10 in total for a normal run which is far less than it takes to render the login screen on a first visit, and far less than I guess the average user session normally is. I figure they had less than hundred 500 server errors in the log's in total, from different pages, during my testing. There should be no errors created now during a run. It certainly could be optimized, but hey as the saying goes "perfect is the enemy of complete."  I sent an email asking for an authentication token for an API, and am sending this project as a POC for community access to their power consumption data.

With the data retrieval part solved, I then created a python script to format and put it somewhere: a rrd file that was compatible with monitoring tools. That part took another day or so, I thank **Risto Hietala** for his very relevant (I too use a raspberry pi, temperature sensor and graph the results, but I use Zenoss to monitor and create the rrd for that project. This project, I create the rrd and give it to Zenoss) [blog post](http://www.hietala.org/rrdtool-as-timeseries-datastore-for-sensor-data.html) and [github repo](https://github.com/rhietala/raspberry-ansible/blob/master/roles/tempreader-rrdtool/files/readtemp-rrd.py) for helping me solve this part.

## Who are you?

Who has two thumbs and wants to monitor his power consumption? *This guy*

## Conclusion?

Well, I will certainly save money over time with my new HVAC. My consumption droped noticeable, visually, after the installation. My power consumption spiked up to 1 kwh twice over a two day period, probably when the 5th stage fan kicked in for a short while, compared to whenever the old system was running.

However, the data seems to suggest that I only eliminate consuming utility power when I produce over 1.5 to 2 kwh of energy, which is basically on a bright, clear, cloudless day, EVEN THOUGH I may only be consuming 0.5 kwh as reported by the utility company. I wonder why this is? Is this the result of electrical resistance? Is there an electrical barrier or wave to overcome, like when rushing creek water meets a river, and the river wants to push into the creek? At some point it equalizes, the water becomes one, and then flows together into the larger river. Once I cross this threshold does the "resistance" drop to my energy production drop according to some function? I have noticed my meter stopped when it is supposed to be running backwards. Hmmm.

Below (and above) is a screen shot of a 4 day period of my energy production and consumption.
Top, first graph: Generated Solar Power in Watts
Next, second graph: Total Power generated for the day in Watts
Next, third graph: Power consumed from Utility, measured in negative Watts
**Last, forth graph: Power produced laid on top of power consumed, stacked.**

The last graph is the important one.

I installed the new HVAC on Monday, so you see Sunday and Monday is the old energy consumption. Tuesday, Wednesday, and Friday is the new consumption.  Green is enegery consumed, blue is energy produced.  There is clearly more green on Sunday and Monday, than from Tuesday onwards.

![Before and After installing heat pump](https://raw.githubusercontent.com/syspimp/greystone-ansible/master/pics/heat-pump-energy-savings.png)

## For you!

Requires: `ansible, python3, and python3-rrdtool` (or python and python-rrdtool for python 2.7, but you will need to change the roles/files/manage-rrd.py file to use correct python interpreter)

Only tested on Fedora 30 and ansible 2.8, but your mileage may vary.

To use this, edit the `group_vars/all` file with your greystone information and then run the playbook. A sample installation and use would go like this:
    # clone the code
    git clone https://github.com/syspimp/greystone-ansible.git
    cd greystone-ansible
    # edit the group_vars/all with your greystone stuff and name of the graph you want to create
    vi group_vars_all
    # run the playbook
	ansible-playbook -i inventory site.yml
    # check the output
   firefox file:///tmp/yourgraphname.png 

The rrd file and a simple graph will be in /tmp with whatever graph name you set in the `group_vars/all` file.

Once you have that working, you can modify and use the included shell script to bulk import and then add daily usage to a rrd file.

You may use this free of charge, and you get what you paid for. No warranty implied. Don't change the wait times and don't hammer the API. Be nice.

## Notes

* `yum install python3-rrdtool` will get you going if you get an error on first run, I could install that via the ansible playbook, but then what fun will you have? :) Let as an exercise for the reader.
* it would be nice if the utility company gave customer access to the data in the form of some API token **hint hint**
* scripting/regex could be optimized
* getting the data into a modern graphing/monitoring tool would be nice
* Greystone doesn't give real-time data, it gives the previous day's data, but they have a zigbee or some type of radio module in the meter. Perhaps I can poll my meter directly?
* if the website changes in any way, this is broken.


